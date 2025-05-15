import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import traceback
import networkx as nx

from config import settings, LLMProvider
from .local_llm_client import LocalLLMClient  

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        """
        Initialize the AI Analyzer with appropriate LLM client
        """
        # Select LLM client based on configuration
        if settings.LLM_PROVIDER == LLMProvider.LOCAL_LLM:
            self.llm_client = LocalLLMClient(
                base_url=settings.LOCAL_LLM_BASE_URL
            )
        else:
            # Fallback or other LLM providers can be added here
            raise ValueError(f"Unsupported LLM Provider: {settings.LLM_PROVIDER}")
        
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)

    def _get_cache_key(self, content: str, context: str) -> str:
        """Generate cache key for analysis results."""
        return f"{hash(content)}:{hash(context)}"

    def _generate_fallback_analysis(self, file_path: str) -> Dict:
        """Generate basic analysis when AI analysis fails."""
        return {
            'summary': f"Basic analysis for {file_path} (AI analysis failed)",
            'file_path': file_path,
            'error_details': 'Automated analysis could not be completed',
            'main_components': [],
            'dependencies': [],
            'improvements': ["Manual review recommended"],
            'complexity_analysis': {
                'lines': 0,
                'basic_metrics': {}
            }
        }

    async def analyze_code(self, content: str, file_path: str) -> Dict:
        """
        Analyze code content using local LLM with caching and fallback.
        
        Args:
            content (str): Code content to analyze
            file_path (str): Path of the file being analyzed
        
        Returns:
            Dict: Analysis results
        """
        try:
            # Check cache first
            cache_key = self._get_cache_key(content, file_path)
            if cache_key in self.cache:
                cached_result, cache_time = self.cache[cache_key]
                if datetime.now() - cache_time < self.cache_ttl:
                    return cached_result

            # Prepare prompt for code analysis
            prompt = f"""Perform a comprehensive code analysis for the file: {file_path}

            Analyze the following code (first 5000 characters):
            ```
            {content[:5000]}
            ```

            Provide a detailed analysis including:
            1. Code purpose and functionality
            2. Code complexity assessment
            3. Potential performance concerns
            4. Suggested improvements and refactoring opportunities
            5. Security and maintainability insights

            Format your response as a JSON object with clear, structured sections."""

            # Generate analysis using local LLM
            raw_result = await asyncio.to_thread(
                self.llm_client.generate_text, 
                prompt, 
                max_tokens=500, 
                temperature=0.5
            )

            # Parse the response
            parsed_result = self.llm_client.parse_response(raw_result)
            
            # Prepare analysis result
            analysis = {
                'summary': parsed_result.get('summary', 'No detailed summary available'),
                'file_path': file_path,
                'analysis_type': 'local_llm',
                'details': parsed_result
            }
            
            # Cache the result
            self.cache[cache_key] = (analysis, datetime.now())
            
            return analysis
        
        except Exception as e:
            logger.error(f"Code analysis failed for {file_path}: {str(e)}")
            logger.error(traceback.format_exc())
            return self._generate_fallback_analysis(file_path)

    async def analyze_project_structure(
        self, 
        file_paths: List[str], 
        analyses: List[Dict],
        dependency_graph: nx.DiGraph
    ) -> Dict:
        """
        Analyze overall project structure using local LLM.
        
        Args:
            file_paths (List[str]): List of file paths in the project
            analyses (List[Dict]): Detailed analyses of individual files
            dependency_graph (nx.DiGraph): Project dependency graph
        
        Returns:
            Dict: Project-wide analysis results
        """
        try:
            # Prepare prompt for project structure analysis
            prompt = f"""Perform a comprehensive project architecture analysis:

            Project Details:
            - Total Files: {len(file_paths)}
            - Key File Paths: {', '.join(file_paths[:10])}
            - Dependency Graph Edges: {list(dependency_graph.edges())}

            Provide a detailed analysis including:
            1. Overall project architecture overview
            2. Code organization and modularity assessment
            3. Design patterns and structural insights
            4. Potential system interaction improvements
            5. Technology stack recommendations
            6. Long-term maintainability assessment

            Format your response as a structured JSON object with clear sections."""
            
            # Generate project analysis using local LLM
            raw_result = await asyncio.to_thread(
                self.llm_client.generate_text, 
                prompt, 
                max_tokens=500, 
                temperature=0.5
            )
            
            # Parse the response
            parsed_result = self.llm_client.parse_response(raw_result)
            
            return {
                'architecture_summary': parsed_result.get('summary', 'No detailed summary available'),
                'main_components': file_paths[:5],
                'complexity_assessment': {
                    'total_files': len(file_paths)
                },
                'details': parsed_result
            }
        
        except Exception as e:
            logger.error(f"Project analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'architecture_summary': "Basic structure analysis (AI analysis failed)",
                'main_components': file_paths[:5],
                'tech_stack': [],
                'recommendations': ["Automated recommendations unavailable"],
                'complexity_assessment': {
                    'total_files': len(file_paths)
                }
            }