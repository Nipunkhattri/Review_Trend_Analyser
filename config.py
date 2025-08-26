import os
from typing import Optional

class AzureOpenAIConfig:
    """Configuration class for Azure OpenAI settings"""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
        
    def is_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured"""
        return bool(self.api_key and self.endpoint and self.deployment_name)
    
    def get_config_dict(self) -> dict:
        """Get configuration as dictionary for LangChain"""
        return {
            "azure_openai_api_key": self.api_key,
            "azure_openai_endpoint": self.endpoint,
            "azure_openai_api_version": self.api_version,
            "azure_openai_deployment_name": self.deployment_name,
        }

azure_config = AzureOpenAIConfig()
