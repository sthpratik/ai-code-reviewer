import yaml
from crewai import Task
from typing import Dict, List

def load_task_config(config_path: str = 'config/agents.yaml') -> dict:
    """Load task configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_task_from_config(task_name: str, agent, context: Dict, 
                          config_path: str = 'config/agents.yaml') -> Task:
    """Create task from YAML configuration."""
    config = load_task_config(config_path)
    task_config = config['tasks'][task_name]
    
    description = task_config['description_template'].format(**context)
    
    return Task(
        description=description,
        agent=agent,
        expected_output=task_config['expected_output']
    )
