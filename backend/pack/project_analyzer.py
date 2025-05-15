# from pathlib import Path
# import networkx as nx
# from datetime import datetime
# from typing import Dict, List, Optional, Set, Any
# import asyncio
# from functools import wraps
# import chardet
# import logging
# from ratelimit import limits, sleep_and_retry
# from .ai_analyzer import AIAnalyzer
# from config import settings


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def retry_on_exception(retries=3, delay=5):
#     """Decorator to retry functions on exception."""
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             last_exception = None
#             for attempt in range(retries):
#                 try:
#                     return await func(*args, **kwargs)
#                 except Exception as e:
#                     last_exception = e
#                     logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
#                     if attempt < retries - 1:
#                         await asyncio.sleep(delay * (attempt + 1))
#             logger.error(f"All {retries} attempts failed: {str(last_exception)}")
#             raise last_exception
#         return wrapper
#     return decorator

# class ProjectAnalyzer:
#     def __init__(self, project_path: str):
#         """Initialize the ProjectAnalyzer with a project path."""
#         self.project_path = Path(project_path)
#         self.dependency_graph = nx.DiGraph()
#         self.ai_analyzer = AIAnalyzer()
#         self.processed_files: Set[str] = set()
#         self.analysis_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_ANALYSES)
#         self.file_cache: Dict[str, Any] = {}

#     def detect_file_encoding(self, file_path: Path) -> str:
#         """Detect the correct encoding of a file."""
#         try:
#             with open(file_path, 'rb') as file:
#                 raw_data = file.read()
#                 result = chardet.detect(raw_data)
#                 return result['encoding'] or 'utf-8'
#         except Exception as e:
#             logger.warning(f"Error detecting encoding for {file_path}: {e}")
#             return 'utf-8'

#     async def read_file_content(self, file_path: Path) -> Optional[str]:
#         """Read file content with proper encoding detection and error handling."""
#         try:
#             # Check cache first
#             cache_key = str(file_path)
#             if cache_key in self.file_cache:
#                 return self.file_cache[cache_key]

#             encoding = self.detect_file_encoding(file_path)
#             async with asyncio.Lock():
#                 with open(file_path, 'r', encoding=encoding) as f:
#                     content = f.read()
#                     self.file_cache[cache_key] = content
#                     return content
#         except Exception as e:
#             logger.error(f"Error reading file {file_path}: {e}")
#             return None

#     def _generate_skipped_file_analysis(self, file_path: Path, reason: str) -> Dict:
#         """Generate analysis result for skipped files."""
#         return {
#             'path': str(file_path.relative_to(self.project_path)),
#             'status': 'skipped',
#             'reason': reason,
#             'static_analysis': {
#                 'imports': [],
#                 'functions': [],
#                 'classes': [],
#                 'size': 0,
#                 'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
#             },
#             'ai_analysis': None
#         }

#     @retry_on_exception(retries=3, delay=2)
#     async def analyze_file(self, file_path: Path) -> Dict:
#         """Analyze a single file and its dependencies."""
#         if file_path.name.startswith('._') or file_path.name.startswith('.'):
#             return self._generate_skipped_file_analysis(file_path, "Hidden or system file")

#         if file_path.suffix not in settings.ALLOWED_EXTENSIONS:
#             return self._generate_skipped_file_analysis(file_path, "Unsupported file type")

#         content = await self.read_file_content(file_path)
#         if content is None:
#             return self._generate_skipped_file_analysis(file_path, "Failed to read file")

#         async with self.analysis_semaphore:
#             try:
#                 imports, functions, classes = self._perform_static_analysis(content)
#                 ai_analysis = await self._get_ai_analysis_with_fallback(content, file_path)
                
#                 return {
#                     'path': str(file_path.relative_to(self.project_path)),
#                     'status': 'analyzed',
#                     'static_analysis': {
#                         'imports': imports,
#                         'functions': functions,
#                         'classes': classes,
#                         'size': len(content.splitlines()),
#                         'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
#                     },
#                     'ai_analysis': ai_analysis
#                 }
#             except Exception as e:
#                 logger.error(f"Error analyzing {file_path}: {e}")
#                 return self._generate_skipped_file_analysis(file_path, str(e))

#     def _perform_static_analysis(self, content: str) -> tuple:
#         """Perform static analysis of code content."""
#         imports = []
#         functions = []
#         classes = []
        
#         for line in content.split('\n'):
#             line = line.strip()
#             if line.startswith('import ') or line.startswith('from '):
#                 imports.append(line)
#             elif line.startswith('def '):
#                 functions.append(line.split('def ')[1].split('(')[0])
#             elif line.startswith('class '):
#                 classes.append(line.split('class ')[1].split('(')[0].split(':')[0])
                
#         return imports, functions, classes

#     async def _get_ai_analysis_with_fallback(self, content: str, file_path: Path) -> Dict:
#         """Get AI analysis with fallback to basic analysis if AI fails."""
#         try:
#             return await self.ai_analyzer.analyze_code(content, str(file_path))
#         except Exception as e:
#             logger.warning(f"AI analysis failed, using fallback for {file_path}: {e}")
#             return self._generate_fallback_analysis(content)

#     def _generate_fallback_analysis(self, content: str) -> Dict:
#         """Generate basic analysis when AI analysis fails."""
#         return {
#             'summary': "Basic analysis (AI analysis failed)",
#             'complexity': len(content.splitlines()),
#             'type': 'unknown',
#             'concerns': [],
#             'suggestions': []
#         }

#     @sleep_and_retry
#     @limits(calls=2, period=100)
#     async def analyze_project(self) -> Dict:
#         """Analyze the entire project structure."""
#         analyses = []
#         file_paths = []
        
#         # Gather all files
#         files_to_analyze = []
#         for ext in settings.ALLOWED_EXTENSIONS:
#             files_to_analyze.extend(self.project_path.rglob(f"*{ext}"))
        
#         # Analyze files concurrently
#         tasks = []
#         for file_path in files_to_analyze:
#             if str(file_path) not in self.processed_files:
#                 tasks.append(self.analyze_file(file_path))
#                 self.processed_files.add(str(file_path))
        
#         analyses = await asyncio.gather(*tasks, return_exceptions=True)
        
#         # Filter out exceptions and failed analyses
#         valid_analyses = []
#         for analysis in analyses:
#             if isinstance(analysis, Dict) and analysis.get('status') == 'analyzed':
#                 valid_analyses.append(analysis)
#                 file_paths.append(analysis['path'])
        
#         # Build dependency graph
#         self._build_dependency_graph(valid_analyses)
        
#         # Get project-wide analysis
#         project_analysis = await self._get_project_analysis_with_fallback(
#             file_paths, valid_analyses
#         )
        
#         return {
#             'files': valid_analyses,
#             'dependency_graph': nx.node_link_data(self.dependency_graph,edges = "edges"),
#             'project_analysis': project_analysis,
#             'summary': self._generate_project_summary(valid_analyses)
#         }

#     def _build_dependency_graph(self, analyses: List[Dict]):
#         """Build the project dependency graph."""
#         for analysis in analyses:
#             file_path = analysis['path']
#             imports = analysis['static_analysis']['imports']
            
#             for imp in imports:
#                 # Parse import statement
#                 if imp.startswith('from '):
#                     parts = imp.split(' import ')
#                     if len(parts) == 2:
#                         module = parts[0].replace('from ', '')
#                         self.dependency_graph.add_edge(file_path, module)
#                 elif imp.startswith('import '):
#                     module = imp.replace('import ', '').split(' as ')[0]
#                     self.dependency_graph.add_edge(file_path, module)

#     async def _get_project_analysis_with_fallback(
#         self, 
#         file_paths: List[str], 
#         analyses: List[Dict]
#     ) -> Dict:
#         """Get project-wide analysis with fallback if AI analysis fails."""
#         try:
#             return await self.ai_analyzer.analyze_project_structure(
#                 file_paths=file_paths,
#                 analyses=analyses,
#                 dependency_graph=self.dependency_graph
#             )
#         except Exception as e:
#             logger.warning(f"Project AI analysis failed, using fallback: {e}")
#             return self._generate_fallback_project_analysis(analyses)

#     def _generate_project_summary(self, analyses: List[Dict]) -> Dict:
#         """Generate project summary statistics."""
#         total_lines = sum(a['static_analysis']['size'] for a in analyses)
#         total_functions = sum(len(a['static_analysis']['functions']) for a in analyses)
#         total_classes = sum(len(a['static_analysis']['classes']) for a in analyses)
        
#         return {
#             'total_files': len(analyses),
#             'total_lines': total_lines,
#             'total_functions': total_functions,
#             'total_classes': total_classes,
#             'average_file_size': total_lines / len(analyses) if analyses else 0,
#             'file_types': self._count_file_types(analyses),
#             'dependency_metrics': self._calculate_dependency_metrics()
#         }

#     def _count_file_types(self, analyses: List[Dict]) -> Dict[str, int]:
#         """Count the number of files of each type."""
#         file_types = {}
#         for analysis in analyses:
#             ext = Path(analysis['path']).suffix
#             file_types[ext] = file_types.get(ext, 0) + 1
#         return file_types

#     def _calculate_dependency_metrics(self) -> Dict:
#         """Calculate dependency graph metrics."""
#         return {
#             'total_dependencies': self.dependency_graph.number_of_edges(),
#             'average_dependencies': (
#                 self.dependency_graph.number_of_edges() / 
#                 self.dependency_graph.number_of_nodes()
#                 if self.dependency_graph.number_of_nodes() > 0 else 0
#             ),
#             'cyclic_dependencies': list(nx.simple_cycles(self.dependency_graph))
#         }

#     def _generate_fallback_project_analysis(self, analyses: List[Dict]) -> Dict:
#         """Generate basic project analysis when AI analysis fails."""
#         return {
#             'architecture_summary': "Basic structure analysis (AI analysis failed)",
#             'main_components': [a['path'] for a in analyses[:5]],
#             'tech_stack': self._detect_basic_tech_stack(analyses),
#             'recommendations': ["Automated recommendations unavailable"],
#             'complexity_assessment': {
#                 'total_files': len(analyses),
#                 'total_lines': sum(a['static_analysis']['size'] for a in analyses)
#             }
#         }

#     def _detect_basic_tech_stack(self, analyses: List[Dict]) -> List[str]:
#         """Detect basic technology stack from file extensions and imports."""
#         tech_stack = set()
#         for analysis in analyses:
#             ext = Path(analysis['path']).suffix.lstrip('.')
#             if ext:
#                 tech_stack.add(ext)
            
#             for imp in analysis['static_analysis']['imports']:
#                 if 'import' in imp:
#                     lib = imp.split()[1].split('.')[0]
#                     tech_stack.add(lib)
                    
#         return list(tech_stack)




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

def retry_on_exception(retries=3, delay=5):
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
        logger.info(f"Initialized ProjectAnalyzer with path: {project_path}")
        
        # Log the project directory structure
        self._log_project_structure()

    def _log_project_structure(self):
        """Log the project directory structure for debugging."""
        try:
            logger.info("Project structure:")
            file_count = 0
            
            for path in self.project_path.rglob('*'):
                if path.is_file() and not path.name.startswith('.'):
                    file_count += 1
                    if file_count <= 20:  # Limit logging to first 20 files
                        rel_path = path.relative_to(self.project_path)
                        logger.info(f"  - {rel_path}")
            
            logger.info(f"Total files found: {file_count}")
        except Exception as e:
            logger.error(f"Error logging project structure: {e}")

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
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
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
        # Skip hidden files and system files
        if file_path.name.startswith('._') or file_path.name.startswith('.'):
            return self._generate_skipped_file_analysis(file_path, "Hidden or system file")

        # Skip unsupported file types
        if file_path.suffix not in settings.ALLOWED_EXTENSIONS:
            return self._generate_skipped_file_analysis(file_path, f"Unsupported file type: {file_path.suffix}")

        content = await self.read_file_content(file_path)
        if content is None:
            return self._generate_skipped_file_analysis(file_path, "Failed to read file")

        async with self.analysis_semaphore:
            try:
                imports, functions, classes = self._perform_static_analysis(content, file_path.suffix)
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

    def _perform_static_analysis(self, content: str, file_extension: str) -> tuple:
        """Perform static analysis of code content."""
        imports = []
        functions = []
        classes = []
        
        # Different parsing logic based on file extension
        if file_extension in ['.py', '.pyx']:
            return self._parse_python_file(content)
        elif file_extension in ['.js', '.jsx', '.ts', '.tsx']:
            return self._parse_javascript_file(content)
        elif file_extension in ['.java']:
            return self._parse_java_file(content)
        elif file_extension in ['.cpp', '.cc', '.h', '.hpp']:
            return self._parse_cpp_file(content)
        else:
            # Basic parsing for other file types
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
                elif line.startswith('def ') or line.startswith('function '):
                    functions.append(line.split('def ')[1].split('(')[0] if line.startswith('def ') else 
                                    line.split('function ')[1].split('(')[0])
                elif line.startswith('class '):
                    classes.append(line.split('class ')[1].split('(')[0].split(':')[0])
                
        return imports, functions, classes
    
    def _parse_python_file(self, content: str) -> tuple:
        """Parse a Python file for imports, functions, and classes."""
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
    
    def _parse_javascript_file(self, content: str) -> tuple:
        """Parse a JavaScript file for imports, functions, and classes."""
        imports = []
        functions = []
        classes = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('require('):
                imports.append(line)
            elif 'function ' in line or '=>' in line:
                if 'function ' in line:
                    fn_name = line.split('function ')[1].split('(')[0]
                    if fn_name:
                        functions.append(fn_name)
                elif '=>' in line and '=' in line:
                    fn_name = line.split('=')[0].strip()
                    if fn_name:
                        functions.append(fn_name)
            elif 'class ' in line:
                class_part = line.split('class ')[1]
                if '{' in class_part:
                    class_name = class_part.split('{')[0].strip()
                elif 'extends' in class_part:
                    class_name = class_part.split('extends')[0].strip()
                else:
                    class_name = class_part
                classes.append(class_name)
                
        return imports, functions, classes
    
    def _parse_java_file(self, content: str) -> tuple:
        """Parse a Java file for imports, functions (methods), and classes."""
        imports = []
        functions = []
        classes = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import '):
                imports.append(line)
            elif 'class ' in line:
                class_part = line.split('class ')[1]
                if '{' in class_part:
                    class_name = class_part.split('{')[0].strip()
                elif 'extends' in class_part:
                    class_name = class_part.split('extends')[0].strip()
                elif 'implements' in class_part:
                    class_name = class_part.split('implements')[0].strip()
                else:
                    class_name = class_part
                classes.append(class_name)
                
        # For Java, simple function detection is harder
        # This is a basic approach
        in_method = False
        method_name = ""
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                continue
                
            # Method start detection
            if not in_method and ('public ' in line or 'private ' in line or 'protected ' in line) and '(' in line and ')' in line and '{' in line:
                parts = line.split('(')[0].strip().split()
                if len(parts) >= 2:
                    method_name = parts[-1]
                    functions.append(method_name)
                    
        return imports, functions, classes
    
    def _parse_cpp_file(self, content: str) -> tuple:
        """Parse a C++ file for imports, functions, and classes."""
        imports = []
        functions = []
        classes = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#include'):
                imports.append(line)
            elif 'class ' in line:
                class_part = line.split('class ')[1]
                if '{' in class_part:
                    class_name = class_part.split('{')[0].strip()
                elif ':' in class_part:
                    class_name = class_part.split(':')[0].strip()
                else:
                    class_name = class_part
                classes.append(class_name)
                
        # Basic function detection
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments
            if line.startswith('//') or line.startswith('/*'):
                continue
                
            # Function detection - very simplified
            if '(' in line and ')' in line and '{' in line and not line.startswith('if') and not line.startswith('for') and not line.startswith('while'):
                parts = line.split('(')[0].strip().split()
                if parts:
                    functions.append(parts[-1])
                    
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
    @limits(calls=2, period=100)
    async def analyze_project(self) -> Dict:
        """Analyze the entire project structure."""
        analyses = []
        file_paths = []
        
        # Gather all files
        logger.info(f"Gathering files from {self.project_path} with extensions {settings.ALLOWED_EXTENSIONS}")
        files_to_analyze = []
        for ext in settings.ALLOWED_EXTENSIONS:
            found_files = list(self.project_path.rglob(f"*{ext}"))
            logger.info(f"Found {len(found_files)} files with extension {ext}")
            files_to_analyze.extend(found_files)
        
        logger.info(f"Total files to analyze: {len(files_to_analyze)}")
        
        if not files_to_analyze:
            logger.warning("No files found to analyze in the project directory!")
            
        # Analyze files concurrently
        tasks = []
        for file_path in files_to_analyze:
            if str(file_path) not in self.processed_files:
                tasks.append(self.analyze_file(file_path))
                self.processed_files.add(str(file_path))
        
        if tasks:
            analyses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and failed analyses
            valid_analyses = []
            for analysis in analyses:
                if isinstance(analysis, Dict):
                    if analysis.get('status') == 'analyzed':
                        valid_analyses.append(analysis)
                        file_paths.append(analysis['path'])
                    else:
                        logger.info(f"Skipped file: {analysis.get('path')} - Reason: {analysis.get('reason')}")
                else:
                    logger.error(f"Analysis failed with exception: {analysis}")
            
            # Build dependency graph
            self._build_dependency_graph(valid_analyses)
            
            # Get project-wide analysis
            project_analysis = await self._get_project_analysis_with_fallback(
                file_paths, valid_analyses
            )
            
            return {
                'files': valid_analyses,
                'dependency_graph': nx.node_link_data(self.dependency_graph, edges = "edges"),
                'project_analysis': project_analysis,
                'summary': self._generate_project_summary(valid_analyses)
            }
        else:
            logger.warning("No files to analyze after filtering!")
            return {
                'files': [],
                'dependency_graph': nx.node_link_data(nx.DiGraph(), edges = "edges"),
                'project_analysis': {
                    'architecture_summary': "No valid files found for analysis",
                    'main_components': [],
                    'tech_stack': [],
                    'recommendations': ["Check that your ZIP file contains supported file types."],
                    'complexity_assessment': {
                        'total_files': 0,
                        'total_lines': 0
                    }
                },
                'summary': {
                    'total_files': 0,
                    'total_lines': 0,
                    'total_functions': 0,
                    'total_classes': 0,
                    'average_file_size': 0,
                    'file_types': {},
                    'dependency_metrics': {
                        'total_dependencies': 0,
                        'average_dependencies': 0,
                        'cyclic_dependencies': []
                    }
                }
            }

    def _build_dependency_graph(self, analyses: List[Dict]):
        """Build the project dependency graph."""
        for analysis in analyses:
            file_path = analysis['path']
            imports = analysis['static_analysis']['imports']
            
            # Add the file node to the graph
            if file_path not in self.dependency_graph:
                self.dependency_graph.add_node(file_path)
            
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
        if not analyses:
            logger.warning("No valid analyses found to generate project summary")
            return {
                'total_files': 0,
                'total_lines': 0,
                'total_functions': 0,
                'total_classes': 0,
                'average_file_size': 0,
                'file_types': {},
                'dependency_metrics': {
                    'total_dependencies': 0,
                    'average_dependencies': 0,
                    'cyclic_dependencies': []
                }
            }
            
        total_lines = sum(a['static_analysis']['size'] for a in analyses)
        total_functions = sum(len(a['static_analysis']['functions']) for a in analyses)
        total_classes = sum(len(a['static_analysis']['classes']) for a in analyses)
        
        summary = {
            'total_files': len(analyses),
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'average_file_size': total_lines / len(analyses) if analyses else 0,
            'file_types': self._count_file_types(analyses),
            'dependency_metrics': self._calculate_dependency_metrics()
        }
        
        logger.info(f"Generated project summary: {summary}")
        return summary

    def _count_file_types(self, analyses: List[Dict]) -> Dict[str, int]:
        """Count the number of files of each type."""
        file_types = {}
        for analysis in analyses:
            ext = Path(analysis['path']).suffix
            file_types[ext] = file_types.get(ext, 0) + 1
        return file_types

    def _calculate_dependency_metrics(self) -> Dict:
        """Calculate dependency graph metrics."""
        edges = self.dependency_graph.number_of_edges()
        nodes = self.dependency_graph.number_of_nodes()
        
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
        except Exception as e:
            logger.warning(f"Error detecting cycles in dependency graph: {e}")
            cycles = []
            
        return {
            'total_dependencies': edges,
            'average_dependencies': edges / nodes if nodes > 0 else 0,
            'cyclic_dependencies': cycles
        }

    def _generate_fallback_project_analysis(self, analyses: List[Dict]) -> Dict:
        """Generate basic project analysis when AI analysis fails."""
        file_paths = [a['path'] for a in analyses[:5]] if analyses else []
        
        return {
            'architecture_summary': "Basic structure analysis (AI analysis failed)",
            'main_components': file_paths,
            'tech_stack': self._detect_basic_tech_stack(analyses),
            'recommendations': ["Automated recommendations unavailable"],
            'complexity_assessment': {
                'total_files': len(analyses),
                'total_lines': sum(a['static_analysis']['size'] for a in analyses) if analyses else 0
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
                    parts = imp.split()
                    if len(parts) > 1:
                        lib = parts[1].split('.')[0]
                        tech_stack.add(lib)
                    
        return list(tech_stack)