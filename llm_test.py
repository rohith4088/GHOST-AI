import requests
import json

class LocalLLMClient:
    def __init__(self, base_url='http://127.0.0.1:1234/'):
        """
        Initialize the client for locally hosted LLM via LM Studio
        
        :param base_url: Base URL for the local LLM server
        """
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json'
        }

    def generate_text(self, prompt, max_tokens=150, temperature=0.7):
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
            if result['choices']:
                return result['choices'][0]['message']['content']
            else:
                return result
        
        except requests.RequestException as e:
            print(f"Error connecting to local LLM: {e}")
            return None

def main():
    # Create an instance of the client
    client = LocalLLMClient()

    # Example usage
    prompt = "Explain quantum computing in simple terms"
    response = client.generate_text(prompt)
    
    if response:
        print("Model Response:")
        print(response)

if __name__ == '__main__':
    main()