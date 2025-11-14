#!/usr/bin/env python3
"""Debug script to validate Bitbucket PR access"""

import os
from dotenv import load_dotenv
from utils.bitbucket_utils import create_bitbucket_client
from utils.git_utils import get_changed_files

# Load environment variables
load_dotenv()

def debug_pr_access(workspace: str, repo: str, pr_id: str):
    """Debug PR access and file detection"""
    
    print("=== DEBUGGING PR ACCESS ===")
    
    # Check environment variables
    print(f"BITBUCKET_URL: {os.getenv('BITBUCKET_URL')}")
    print(f"BITBUCKET_TOKEN: {'SET' if os.getenv('BITBUCKET_TOKEN') else 'NOT SET'}")
    
    try:
        # Test Bitbucket API access
        print(f"\n1. Testing Bitbucket API access...")
        client = create_bitbucket_client()
        pr_data = client.get_pull_request(workspace, repo, pr_id)
        
        print(f"✓ PR found: {pr_data.get('title', 'No title')}")
        print(f"✓ PR state: {pr_data.get('state', 'Unknown')}")
        print(f"✓ Source branch: {pr_data.get('source', {}).get('branch', {}).get('name', 'Unknown')}")
        print(f"✓ Destination branch: {pr_data.get('destination', {}).get('branch', {}).get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"✗ Bitbucket API error: {e}")
        return
    
    try:
        # Test local git file detection
        print(f"\n2. Testing local git file detection...")
        changed_files = get_changed_files('develop')  # or try 'main'
        
        print(f"✓ Found {len(changed_files)} changed files:")
        for file in changed_files[:5]:  # Show first 5
            print(f"  - {file}")
        if len(changed_files) > 5:
            print(f"  ... and {len(changed_files) - 5} more")
            
        if not changed_files:
            print("⚠️  No changed files detected. This could be why no reviews were generated.")
            print("   Try: git status, git diff develop, or change base branch")
            
    except Exception as e:
        print(f"✗ Git error: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print("Usage: python debug_pr.py <workspace> <repo> <pr_id>")
        sys.exit(1)
    
    debug_pr_access(sys.argv[1], sys.argv[2], sys.argv[3])
