from pathlib import Path
import networkx as nx
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
import asyncio
from functools import wraps
import chardet
import logging
from ratelimit import limits, sleep_and_retry
from .ai_analyzer import AIAnalyzer
from config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_on_exception(retries=3, delay=1):
    """Decorator to retry functions on exception."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            logger.error(f"All {retries} attempts failed: {str(last_exception)}")
            raise last_exception
        return wrapper
    return decorator

class ProjectAnalyzer:
    def __init__(self, project_path: str):
        """Initialize the ProjectAnalyzer with a project path."""
        self.project_path = Path(project_path)
        self.dependency_graph = nx.DiGraph()
        self.ai_analyzer = AIAnalyzer()
        self.processed_files: Set[str] = set()
        self.analysis_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_ANALYSES)
        self.file_cache: Dict[str, Any] = {}

    def detect_file_encoding(self, file_path: Path) -> str:
        """Detect the correct encoding of a file."""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception as e:
            logger.warning(f"Error detecting encoding for {file_path}: {e}")
            return 'utf-8'

    async def read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content with proper encoding detection and error handling."""
        try:
            # Check cache first
            cache_key = str(file_path)
            if cache_key in self.file_cache:
                return self.file_cache[cache_key]

            encoding = self.detect_file_encoding(file_path)
            async with asyncio.Lock():
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    self.file_cache[cache_key] = content
                    return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def _generate_skipped_file_analysis(self, file_path: Path, reason: str) -> Dict:
        """Generate analysis result for skipped files."""
        return {
            'path': str(file_path.relative_to(self.project_path)),
            'status': 'skipped',
            'reason': reason,
            'static_analysis': {
                'imports': [],
                'functions': [],
                'classes': [],
                'size': 0,
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            },
            'ai_analysis': None
        }

    @retry_on_exception(retries=3, delay=2)
    async def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single file and its dependencies."""
        if file_path.name.startswith('._') or file_path.name.startswith('.'):
            return self._generate_skipped_file_analysis(file_path, "Hidden or system file")

        if file_path.suffix not in settings.ALLOWED_EXTENSIONS:
            return self._generate_skipped_file_analysis(file_path, "Unsupported file type")

        content = await self.read_file_content(file_path)
        if content is None:
            return self._generate_skipped_file_analysis(file_path, "Failed to read file")

        async with self.analysis_semaphore:
            try:
                imports, functions, classes = self._perform_static_analysis(content)
                ai_analysis = await self._get_ai_analysis_with_fallback(content, file_path)
                
                return {
                    'path': str(file_path.relative_to(self.project_path)),
                    'status': 'analyzed',
                    'static_analysis': {
                        'imports': imports,
                        'functions': functions,
                        'classes': classes,
                        'size': len(content.splitlines()),
                        'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    },
                    'ai_analysis': ai_analysis
                }
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
                return self._generate_skipped_file_analysis(file_path, str(e))

    def _perform_static_analysis(self, content: str) -> tuple:
        """Perform static analysis of code content."""
        imports = []
        functions = []
        classes = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
            elif line.startswith('def '):
                functions.append(line.split('def ')[1].split('(')[0])
            elif line.startswith('class '):
                classes.append(line.split('class ')[1].split('(')[0].split(':')[0])
                
        return imports, functions, classes

    async def _get_ai_analysis_with_fallback(self, content: str, file_path: Path) -> Dict:
        """Get AI analysis with fallback to basic analysis if AI fails."""
        try:
            return await self.ai_analyzer.analyze_code(content, str(file_path))
        except Exception as e:
            logger.warning(f"AI analysis failed, using fallback for {file_path}: {e}")
            return self._generate_fallback_analysis(content)

    def _generate_fallback_analysis(self, content: str) -> Dict:
        """Generate basic analysis when AI analysis fails."""
        return {
            'summary': "Basic analysis (AI analysis failed)",
            'complexity': len(content.splitlines()),
            'type': 'unknown',
            'concerns': [],
            'suggestions': []
        }

    @sleep_and_retry
    @limits(calls=50, period=60)
    async def analyze_project(self) -> Dict:
        """Analyze the entire project structure."""
        analyses = []
        file_paths = []
        
        # Gather all files
        files_to_analyze = []
        for ext in settings.ALLOWED_EXTENSIONS:
            files_to_analyze.extend(self.project_path.rglob(f"*{ext}"))
        
        # Analyze files concurrently
        tasks = []
        for file_path in files_to_analyze:
            if str(file_path) not in self.processed_files:
                tasks.append(self.analyze_file(file_path))
                self.processed_files.add(str(file_path))
        
        analyses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and failed analyses
        valid_analyses = []
        for analysis in analyses:
            if isinstance(analysis, Dict) and analysis.get('status') == 'analyzed':
                valid_analyses.append(analysis)
                file_paths.append(analysis['path'])
        
        # Build dependency graph
        self._build_dependency_graph(valid_analyses)
        
        # Get project-wide analysis
        project_analysis = await self._get_project_analysis_with_fallback(
            file_paths, valid_analyses
        )
        
        return {
            'files': valid_analyses,
            'dependency_graph': nx.node_link_data(self.dependency_graph),
            'project_analysis': project_analysis,
            'summary': self._generate_project_summary(valid_analyses)
        }

    def _build_dependency_graph(self, analyses: List[Dict]):
        """Build the project dependency graph."""
        for analysis in analyses:
            file_path = analysis['path']
            imports = analysis['static_analysis']['imports']
            
            for imp in imports:
                # Parse import statement
                if imp.startswith('from '):
                    parts = imp.split(' import ')
                    if len(parts) == 2:
                        module = parts[0].replace('from ', '')
                        self.dependency_graph.add_edge(file_path, module)
                elif imp.startswith('import '):
                    module = imp.replace('import ', '').split(' as ')[0]
                    self.dependency_graph.add_edge(file_path, module)

    async def _get_project_analysis_with_fallback(
        self, 
        file_paths: List[str], 
        analyses: List[Dict]
    ) -> Dict:
        """Get project-wide analysis with fallback if AI analysis fails."""
        try:
            return await self.ai_analyzer.analyze_project_structure(
                file_paths=file_paths,
                analyses=analyses,
                dependency_graph=self.dependency_graph
            )
        except Exception as e:
            logger.warning(f"Project AI analysis failed, using fallback: {e}")
            return self._generate_fallback_project_analysis(analyses)

    def _generate_project_summary(self, analyses: List[Dict]) -> Dict:
        """Generate project summary statistics."""
        total_lines = sum(a['static_analysis']['size'] for a in analyses)
        total_functions = sum(len(a['static_analysis']['functions']) for a in analyses)
        total_classes = sum(len(a['static_analysis']['classes']) for a in analyses)
        
        return {
            'total_files': len(analyses),
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'average_file_size': total_lines / len(analyses) if analyses else 0,
            'file_types': self._count_file_types(analyses),
            'dependency_metrics': self._calculate_dependency_metrics()
        }

    def _count_file_types(self, analyses: List[Dict]) -> Dict[str, int]:
        """Count the number of files of each type."""
        file_types = {}
        for analysis in analyses:
            ext = Path(analysis['path']).suffix
            file_types[ext] = file_types.get(ext, 0) + 1
        return file_types

    def _calculate_dependency_metrics(self) -> Dict:
        """Calculate dependency graph metrics."""
        return {
            'total_dependencies': self.dependency_graph.number_of_edges(),
            'average_dependencies': (
                self.dependency_graph.number_of_edges() / 
                self.dependency_graph.number_of_nodes()
                if self.dependency_graph.number_of_nodes() > 0 else 0
            ),
            'cyclic_dependencies': list(nx.simple_cycles(self.dependency_graph))
        }

    def _generate_fallback_project_analysis(self, analyses: List[Dict]) -> Dict:
        """Generate basic project analysis when AI analysis fails."""
        return {
            'architecture_summary': "Basic structure analysis (AI analysis failed)",
            'main_components': [a['path'] for a in analyses[:5]],
            'tech_stack': self._detect_basic_tech_stack(analyses),
            'recommendations': ["Automated recommendations unavailable"],
            'complexity_assessment': {
                'total_files': len(analyses),
                'total_lines': sum(a['static_analysis']['size'] for a in analyses)
            }
        }

    def _detect_basic_tech_stack(self, analyses: List[Dict]) -> List[str]:
        """Detect basic technology stack from file extensions and imports."""
        tech_stack = set()
        for analysis in analyses:
            ext = Path(analysis['path']).suffix.lstrip('.')
            if ext:
                tech_stack.add(ext)
            
            for imp in analysis['static_analysis']['imports']:
                if 'import' in imp:
                    lib = imp.split()[1].split('.')[0]
                    tech_stack.add(lib)
                    
        return list(tech_stack)