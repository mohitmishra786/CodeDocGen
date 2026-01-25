import keyring
import getpass
import logging

SERVICE_NAME = "CodeDocGen"

class CredentialManager:
    """Manages secure storage of API keys using the system keyring."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def set_key(self, provider: str, key: str) -> None:
        """
        Securely store an API key.
        
        Args:
            provider: The AI provider name (e.g., 'groq', 'openai')
            key: The API key to store
        """
        try:
            keyring.set_password(SERVICE_NAME, f"{provider}_api_key", key)
            self.logger.info(f"Successfully stored API key for {provider}")
        except Exception as e:
            self.logger.error(f"Failed to store API key for {provider}: {e}")

    def get_key(self, provider: str) -> str:
        """
        Retrieve a stored API key.
        
        Args:
            provider: The AI provider name
            
        Returns:
            The API key or None if not found
        """
        try:
            return keyring.get_password(SERVICE_NAME, f"{provider}_api_key")
        except Exception as e:
            self.logger.debug(f"Could not retrieve API key for {provider} from keyring: {e}")
            return None

    def delete_key(self, provider: str) -> None:
        """
        Delete a stored API key.
        
        Args:
            provider: The AI provider name
        """
        try:
            keyring.delete_password(SERVICE_NAME, f"{provider}_api_key")
            self.logger.info(f"Deleted API key for {provider}")
        except Exception as e:
            self.logger.error(f"Failed to delete API key for {provider}: {e}")

    def prompt_and_set_key(self, provider: str) -> None:
        """Prompt user for key and store it."""
        print(f"Enter API Key for {provider}: ", end="", flush=True)
        key = getpass.getpass("")
        if key:
            self.set_key(provider, key)
        else:
            print("No key entered.")
