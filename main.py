#!/usr/bin/env python3
import argparse
import os
import sys
from dotenv import load_dotenv
from code_reviewer import CodeReviewer

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='AI-powered code review agent')
    parser.add_argument('--mode', choices=['local', 'bitbucket'], default='local',
                       help='Review mode: local or bitbucket')
    parser.add_argument('--base-branch', default='develop',
                       help='Base branch to compare against')
    parser.add_argument('--workspace', help='Bitbucket workspace (overrides BITBUCKET_WORKSPACE env var)')
    parser.add_argument('--repo', help='Bitbucket repository (overrides BITBUCKET_REPO env var)')
    parser.add_argument('--pr-id', help='Pull request ID')
    parser.add_argument('--config', default='config/review_standards.yaml',
                       help='Path to review standards config')
    
    args = parser.parse_args()
    
    try:
        reviewer = CodeReviewer(args.config)
        
        if args.mode == 'local':
            print("Starting local code review...")
            reviews = reviewer.review_local_changes(args.base_branch)
            reviewer.print_local_review(reviews)
            
        elif args.mode == 'bitbucket':
            # Use environment variables as defaults, CLI args as overrides
            workspace = args.workspace or os.getenv('BITBUCKET_WORKSPACE')
            repo = args.repo or os.getenv('BITBUCKET_REPO')
            pr_id = args.pr_id
            
            if not all([workspace, repo, pr_id]):
                missing = []
                if not workspace: missing.append('workspace (--workspace or BITBUCKET_WORKSPACE)')
                if not repo: missing.append('repo (--repo or BITBUCKET_REPO)')
                if not pr_id: missing.append('pr-id (--pr-id)')
                print(f"Error: Missing required parameters: {', '.join(missing)}")
                sys.exit(1)
            
            print("Starting Bitbucket pull request review...")
            reviews = reviewer.review_pull_request(workspace, repo, pr_id)
            print(f"Added {len([r for r in reviews if r.get('severity') in ['critical', 'major']])} comments to PR")
            reviewer.print_local_review(reviews)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
