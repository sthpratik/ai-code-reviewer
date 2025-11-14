import subprocess
import os
from typing import List, Dict

def get_current_branch() -> str:
    """Get the current Git branch name."""
    result = subprocess.run(['git', 'branch', '--show-current'], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def get_changed_files(base_branch: str = 'develop') -> List[str]:
    """Get list of changed files between current branch and base branch."""
    result = subprocess.run(['git', 'diff', '--name-only', f'{base_branch}...HEAD'], 
                          capture_output=True, text=True)
    return [f.strip() for f in result.stdout.split('\n') if f.strip()]

def get_file_diff(file_path: str, base_branch: str = 'develop') -> str:
    """Get diff for a specific file."""
    result = subprocess.run(['git', 'diff', f'{base_branch}...HEAD', '--', file_path], 
                          capture_output=True, text=True)
    return result.stdout

def get_file_content(file_path: str) -> str:
    """Read file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
