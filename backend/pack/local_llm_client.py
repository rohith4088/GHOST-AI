import requests
import json
import logging
from typing import Dict, Any
import os
logger = logging.getLogger(__name__)

class LocalLLMClient:
    def __init__(self, base_url='http://192.168.0.113:1234'):
        self.base_url = base_url.rstrip('/')
        self.timeout = 30
        self.headers = {'Content-Type': 'application/json'}

    def generate_text(self, prompt: str, **kwargs) -> Dict:
        payload = {
            "model": os.getenv("LOCAL_LLM_MODEL", "llama-3.2-3b-instruct"),  # Add model name here
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 2000)
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            return self._parse_response(response.json())
            
        except requests.RequestException as e:
            logger.error(f"Connection error: {str(e)}")
            return {'error': f'Connection failed: {str(e)}'}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {'error': f'Processing error: {str(e)}'}

    def _parse_response(self, raw_response: Dict) -> Dict:
        """Parse LM Studio's response format"""
        try:
            if 'choices' in raw_response and raw_response['choices']:
                content = raw_response['choices'][0]['message']['content']
                return {
                    'success': True,
                    'content': content,
                    'raw': raw_response
                }
            
            return {'error': 'Invalid response structure'}
            
        except KeyError as e:
            logger.error(f"Missing key in response: {str(e)}")
            return {'error': f'Response parsing failed: {str(e)}'}

    def parse_response(self, raw_response: Dict) -> Dict[str, Any]:
        """
        Parse the raw response into structured format
        Handles both successful responses and errors
        """
        if 'error' in raw_response:
            return raw_response
        
        try:
            # Attempt JSON parsing of the content
            return json.loads(raw_response['content'])
        except json.JSONDecodeError:
            # Fallback to text parsing
            return {
                'summary': raw_response['content'],
                'details': 'Response in free text format',
                'raw': raw_response
            }
        except Exception as e:
            logger.error(f"Parse error: {str(e)}")
            return {'error': f'Failed to parse response: {str(e)}'}