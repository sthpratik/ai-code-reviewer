#!/usr/bin/env python3
"""Test adding comment to PR"""

from dotenv import load_dotenv
from utils.bitbucket_utils import create_bitbucket_client

load_dotenv()

def test_add_comment(workspace: str, repo: str, pr_id: str):
    try:
        client = create_bitbucket_client()
        
        # Add a test comment
        comment = "🤖 **TEST**: This is a test comment from the AI Code Review Agent"
        
        result = client.add_comment(workspace, repo, pr_id, comment)
        print(f"✓ Comment added successfully!")
        print(f"Comment ID: {result.get('id', 'Unknown')}")
        
    except Exception as e:
        print(f"✗ Error adding comment: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print("Usage: python test_comment.py <workspace> <repo> <pr_id>")
        sys.exit(1)
    
    test_add_comment(sys.argv[1], sys.argv[2], sys.argv[3])
