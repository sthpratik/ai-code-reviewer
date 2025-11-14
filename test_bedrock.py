#!/usr/bin/env python3
"""Test Bedrock model availability"""

import boto3
from dotenv import load_dotenv

load_dotenv()

def test_bedrock_models():
    try:
        client = boto3.client('bedrock', region_name='us-east-1')
        
        # List available foundation models
        response = client.list_foundation_models()
        
        print("Available Claude models:")
        for model in response['modelSummaries']:
            if 'claude' in model['modelId'].lower():
                print(f"  - {model['modelId']}")
                print(f"    Status: {model.get('modelLifecycle', {}).get('status', 'Unknown')}")
                
    except Exception as e:
        print(f"Error listing models: {e}")
        
    # Test specific model
    try:
        runtime_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Try the current model
        model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        print(f"\nTesting model: {model_id}")
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = runtime_client.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        print("✓ Model works!")
        
    except Exception as e:
        print(f"✗ Model error: {e}")
        
        # Try alternative models
        alternatives = [
            'anthropic.claude-3-sonnet-20240229-v1:0',
            'anthropic.claude-3-haiku-20240307-v1:0',
            'anthropic.claude-v2:1'
        ]
        
        for alt_model in alternatives:
            try:
                print(f"\nTrying alternative: {alt_model}")
                response = runtime_client.invoke_model(
                    modelId=alt_model,
                    body=json.dumps(body)
                )
                print(f"✓ {alt_model} works!")
                break
            except Exception as alt_e:
                print(f"✗ {alt_model} failed: {alt_e}")

if __name__ == '__main__':
    import json
    test_bedrock_models()
