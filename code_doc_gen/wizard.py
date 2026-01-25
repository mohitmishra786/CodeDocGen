"""
Interactive setup wizard for CodeDocGen.
"""
import os
import logging
import getpass
from pathlib import Path
from typing import Dict, Any
import yaml

from .config import Config
from .credential_manager import CredentialManager

class SetupWizard:
    """Interactive setup wizard for first-time users."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cred_manager = CredentialManager()
        self.config = Config()
        
    def run(self) -> None:
        """Run the interactive setup wizard."""
        print("\n" + "="*50)
        print("Welcome to CodeDocGen Setup Wizard")
        print("="*50 + "\n")
        
        print("This wizard will help you configure CodeDocGen for your environment.\n")
        
        # 1. AI Provider Selection
        print("--- Step 1: AI Configuration ---")
        use_ai = self._ask_yes_no("Do you want to enable AI-powered documentation?", default=True)
        
        ai_config = self.config.get_ai_config()
        ai_config['enabled'] = use_ai
        
        if use_ai:
            print("\nSelect your primary AI provider:")
            providers = ['groq', 'openai', 'anthropic', 'mistral', 'azure_openai']
            for i, p in enumerate(providers, 1):
                print(f"{i}. {p}")
            
            while True:
                try:
                    choice = input(f"\nEnter choice (1-{len(providers)}) [1]: ").strip()
                    if not choice:
                        choice = "1"
                    idx = int(choice) - 1
                    if 0 <= idx < len(providers):
                        provider = providers[idx]
                        ai_config['provider'] = provider
                        break
                    print("Invalid choice. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            # Configure API Key
            print(f"\n--- Step 2: Configure {provider} Credentials ---")
            print(f"We can securely store your API key in your system keychain.")
            
            if self._ask_yes_no(f"Do you want to set the API key for {provider} now?", default=True):
                self.cred_manager.prompt_and_set_key(provider)
                print(f"API key for {provider} stored securely.")
                
            # Provider specific settings
            if provider == 'azure_openai':
                endpoint = input("\nEnter Azure Endpoint URL: ").strip()
                deployment = input("Enter Azure Deployment Name: ").strip()
                if endpoint:
                    ai_config['azure_endpoint'] = endpoint
                if deployment:
                    ai_config['azure_deployment'] = deployment

        # 2. NLP Settings
        print("\n--- Step 3: NLP Settings ---")
        use_spacy = self._ask_yes_no("Do you want to enable SpaCy for enhanced analysis? (Requires download)", default=False)
        self.config.config['nltk']['enable_spacy'] = use_spacy
        
        # 3. Save Configuration
        print("\n--- Step 4: Save Configuration ---")
        save_path = input("Where should we save the config file? [config.yaml]: ").strip() or "config.yaml"
        
        self.config.config['ai'] = ai_config
        self._save_config(save_path)
        
        print("\n" + "="*50)
        print("Setup Complete!")
        print(f"Configuration saved to {save_path}")
        print("You can now run CodeDocGen with: code_doc_gen --repo . --config " + save_path)
        print("="*50 + "\n")

    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a yes/no question."""
        hint = "[Y/n]" if default else "[y/N]"
        while True:
            resp = input(f"{question} {hint}: ").strip().lower()
            if not resp:
                return default
            if resp in ['y', 'yes']:
                return True
            if resp in ['n', 'no']:
                return False
            print("Please answer yes or no.")

    def _save_config(self, path: str) -> None:
        """Save configuration to YAML file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config.config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"Error saving configuration: {e}")
