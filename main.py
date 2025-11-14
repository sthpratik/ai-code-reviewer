#!/usr/bin/env python3
import argparse
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
    parser.add_argument('--workspace', help='Bitbucket workspace')
    parser.add_argument('--repo', help='Bitbucket repository')
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
            if not all([args.workspace, args.repo, args.pr_id]):
                print("Error: --workspace, --repo, and --pr-id are required for bitbucket mode")
                sys.exit(1)
            
            print("Starting Bitbucket pull request review...")
            reviews = reviewer.review_pull_request(args.workspace, args.repo, args.pr_id)
            print(f"Added {len([r for r in reviews if r.get('severity') in ['critical', 'major']])} comments to PR")
            reviewer.print_local_review(reviews)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
