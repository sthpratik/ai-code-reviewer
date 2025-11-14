#!/usr/bin/env python3
"""Test local git detection"""

from dotenv import load_dotenv
from utils.git_utils import get_changed_files

load_dotenv()

def test_local_changes():
    print("=== TESTING LOCAL GIT CHANGES ===")
    
    # Test different base branches
    for branch in ['develop', 'main', 'master']:
        try:
            print(f"\nTesting against base branch: {branch}")
            changed_files = get_changed_files(branch)
            print(f"Found {len(changed_files)} changed files:")
            
            for file in changed_files[:5]:
                print(f"  - {file}")
            if len(changed_files) > 5:
                print(f"  ... and {len(changed_files) - 5} more")
                
        except Exception as e:
            print(f"Error with branch {branch}: {e}")
    
    # Show git status
    import subprocess
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        print(f"\nGit status output:")
        print(result.stdout if result.stdout else "No changes")
    except Exception as e:
        print(f"Git status error: {e}")

if __name__ == '__main__':
    test_local_changes()
