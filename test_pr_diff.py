#!/usr/bin/env python3
"""Test fetching PR diff directly from server"""

from dotenv import load_dotenv
from utils.bitbucket_utils import create_bitbucket_client

load_dotenv()

def test_pr_diff(workspace: str, repo: str, pr_id: str):
    print("=== TESTING PR DIFF FETCH ===")
    
    try:
        client = create_bitbucket_client()
        
        # Test 1: Get PR changes (list of files)
        print("1. Fetching PR changes...")
        changes = client.get_pull_request_changes(workspace, repo, pr_id)
        print(f"✓ Found changes: {type(changes)}")
        
        if isinstance(changes, dict) and 'values' in changes:
            files = changes['values']
            print(f"✓ Changed files: {len(files)}")
            for file_info in files[:5]:
                path = file_info.get('path', {}).get('toString', 'Unknown')
                print(f"  - {path}")
        else:
            print(f"Changes data: {changes}")
        
        # Test 2: Get PR diff (raw diff text)
        print("\n2. Fetching PR diff...")
        diff = client.get_pull_request_diff(workspace, repo, pr_id)
        print(f"✓ Diff length: {len(diff)} characters")
        print("First 500 characters:")
        print(diff[:500])
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print("Usage: python test_pr_diff.py <workspace> <repo> <pr_id>")
        sys.exit(1)
    
    test_pr_diff(sys.argv[1], sys.argv[2], sys.argv[3])
