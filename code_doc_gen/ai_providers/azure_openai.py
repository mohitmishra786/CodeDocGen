from typing import Optional, Union, List
from .base import AIProvider

try:
    import openai
    from openai.lib.azure import AzureOpenAI
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

class AzureOpenAIProvider(AIProvider):
    def __init__(self, api_key: str, endpoint: str, deployment_name: Union[str, List[str]], api_version: str = "2023-05-15"):
        # We pass deployment_name as 'model' to base class for consistency
        super().__init__(api_key, model=deployment_name)
        self.endpoint = endpoint
        self.api_version = api_version
        self.client = None
        
        if AZURE_AVAILABLE and self.api_key and self.endpoint:
            try:
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version=self.api_version,
                    azure_endpoint=self.endpoint
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize Azure OpenAI client: {e}")
        
        # Ensure model is a list
        if isinstance(self.model, str):
            self.model = [self.model]

    def is_available(self) -> bool:
        return AZURE_AVAILABLE and bool(self.api_key) and bool(self.endpoint) and self.client is not None

    def generate_documentation(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> Optional[str]:
        if not self.is_available() or self.client is None:
            return None

        for deployment in self.model:
            try:
                # For Azure, 'model' parameter in client.chat.completions.create usually refers to the deployment name
                response = self.client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                if response.choices:
                    first_choice = response.choices[0]
                    if first_choice.message and first_choice.message.content:
                        return first_choice.message.content.strip()
                
            except Exception as e:
                self.logger.warning(f"Azure OpenAI deployment {deployment} failed: {e}")
                continue
        
        return None
