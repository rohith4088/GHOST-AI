import requests
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class LocalLLMClient:
    def __init__(self, base_url='http://192.168.1.155:1234/llama-3.2-3b-instruct'):
        """
        Initialize the client for locally hosted LLM
        
        :param base_url: Base URL for the local LLM server
        """
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json'
        }

    def generate_text(self, prompt: str, max_tokens: int = 30000, temperature: float = 0.7) -> str:
        """
        Generate text using the local LLM
        
        :param prompt: Input prompt for the model
        :param max_tokens: Maximum number of tokens to generate
        :param temperature: Sampling temperature for text generation
        :return: Generated text response
        """
        payload = {
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': temperature
        }

        try:
            response = requests.post(
                f'{self.base_url}/chat/completions', 
                headers=self.headers, 
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Robust parsing of the response
            if isinstance(result, dict):
                # Check multiple possible paths for the response text
                if 'choices' in result and result['choices']:
                    # OpenAI-style response
                    return result['choices'][0].get('message', {}).get('content', 
                        result['choices'][0].get('text', 'No content found'))
                elif 'content' in result:
                    # Alternative response format
                    return result['content']
            
            # Fallback if no standard format is found
            return str(result)
        
        except requests.RequestException as e:
            logger.error(f"Error connecting to local LLM: {e}")
            return f"Analysis failed due to LLM connection error: {str(e)}"
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return f"Analysis failed due to response parsing error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in LLM client: {e}")
            return f"Unexpected analysis error: {str(e)}"

    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Attempt to parse the raw LLM response into a structured format
        
        :param raw_response: Raw text response from the LLM
        :return: Parsed dictionary representation
        """
        try:
            # Try to extract JSON from code blocks
            import re
            json_match = re.search(r'```json\n(.*?)\n```', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try direct JSON parsing
            try:
                return json.loads(raw_response)
            except json.JSONDecodeError:
                pass
            
            # Basic structured parsing if JSON fails
            return {
                'summary': raw_response,
                'details': 'Unstructured response',
                'raw_text': raw_response
            }
        
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return {
                'error': 'Response parsing failed',
                'raw_text': raw_response
            }