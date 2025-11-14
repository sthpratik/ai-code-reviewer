import yaml
from crewai import Agent
from utils.bedrock_client import BedrockClient

def load_agent_config(config_path: str = 'config/agents.yaml') -> dict:
    """Load agent configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_agent_from_config(agent_name: str, bedrock_client: BedrockClient, 
                           config_path: str = 'config/agents.yaml') -> Agent:
    """Create agent from YAML configuration."""
    config = load_agent_config(config_path)
    agent_config = config['agents'][agent_name]
    
    return Agent(
        role=agent_config['role'],
        goal=agent_config['goal'],
        backstory=agent_config['backstory'],
        verbose=agent_config.get('verbose', True),
        allow_delegation=agent_config.get('allow_delegation', False),
        llm=bedrock_client
    )
