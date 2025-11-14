import boto3
import json
import os
from typing import Dict, Any
from langchain_aws import ChatBedrock

class BedrockClient:
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        self.client = ChatBedrock(
            model_id=self.model_id,
            region_name=region,
            model_kwargs={"max_tokens": 4000}
        )
    
    def invoke_model(self, prompt: str, max_tokens: int = 4000) -> str:
        """Invoke Bedrock model for code review."""
        response = self.client.invoke(prompt)
        return response.content
    
    def bind(self, **kwargs):
        """Bind method for CrewAI compatibility."""
        return self.client.bind(**kwargs)
