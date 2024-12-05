import requests
import json

class LocalLLMClient:
    def __init__(self, base_url='http://localhost:1234/v1'):
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
            return result['choices'][0]['message']['content']
        
        except requests.RequestException as e:
            print(f"Error connecting to local LLM: {e}")
            return None

def main():
    # Create an instance of the client
    client = LocalLLMClient()

    # Example usage
    prompt = "are you runnign locally"
    response = client.generate_text(prompt)
    
    if response:
        print("Model Response:")
        print(response)

if __name__ == '__main__':
    main()


# import requests
# import json

# class LocalLLMClient:
#     def __init__(self, host='192.168.0.106', port=1234, endpoint='/v1/chat/completions'):
#         """
#         Initialize the client for network-accessible LLM
#         :param host: Host IP (use '0.0.0.0' to allow external access)
#         :param port: Port number
#         :param endpoint: API endpoint path
#         """
#         self.base_url = f'http://{host}:{port}{endpoint}'
#         self.headers = {
#             'Content-Type': 'application/json'
#         }

#     def generate_text(self, prompt, max_tokens=150, temperature=0.7):
#         """
#         Generate text using the local LLM
#         :param prompt: Input prompt for the model
#         :param max_tokens: Maximum number of tokens to generate
#         :param temperature: Sampling temperature for text generation
#         :return: Generated text response
#         """
#         payload = {
#             'messages': [
#                 {'role': 'user', 'content': prompt}
#             ],
#             'max_tokens': max_tokens,
#             'temperature': temperature
#         }
#         try:
#             response = requests.post(
#                 self.base_url,
#                 headers=self.headers,
#                 data=json.dumps(payload),
#                 timeout=30  # Increased timeout
#             )
#             response.raise_for_status()
#             result = response.json()
#             return result['choices'][0]['message']['content']
#         except requests.RequestException as e:
#             print(f"Error connecting to local LLM: {e}")
#             return None

# def main():
#     local_client = LocalLLMClient(host='localhost', port=1234)
#     network_client = LocalLLMClient(host='192.168.0.106', port=1234)
    
#     # Example usage
#     prompt = "Explain quantum computing in simple terms"
#     response = network_client.generate_text(prompt)
#     if response:
#         print("Model Response:")
#         print(response)

# if __name__ == '__main__':
#     main()