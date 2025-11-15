#!/usr/bin/env python3
"""
Command Line Interface for AI Code Reviewer
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_reviewer import CodeReviewer

def load_environment():
    """Load environment variables from .env file if it exists."""
    # Look for .env in current directory first, then in package directory
    env_paths = [
        Path.cwd() / '.env',
        Path(__file__).parent.parent / '.env'
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break

def main():
    """Main CLI entry point."""
    load_environment()
    
    parser = argparse.ArgumentParser(
        description='AI-powered code review using AWS Bedrock',
        prog='ai-code-reviewer'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Local review command
    local_parser = subparsers.add_parser('local', help='Review local changes')
    local_parser.add_argument('--base', '--base-branch', dest='base_branch', 
                             default='develop', help='Base branch to compare against')
    local_parser.add_argument('--config', help='Path to review standards config')
    
    # PR review command
    pr_parser = subparsers.add_parser('pr', help='Review Bitbucket pull request')
    pr_parser.add_argument('--workspace', help='Bitbucket workspace (overrides BITBUCKET_WORKSPACE)')
    pr_parser.add_argument('--repo', help='Repository name (overrides BITBUCKET_REPO)')
    pr_parser.add_argument('--pr-id', required=True, help='Pull request ID')
    pr_parser.add_argument('--config', help='Path to review standards config')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start web server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    server_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    server_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'version':
        from ai_code_reviewer import __version__
        print(f"AI Code Reviewer v{__version__}")
        return
    
    if args.command == 'server':
        try:
            import uvicorn
            from api_server import app
            uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)
        except ImportError:
            print("Error: uvicorn not installed. Install with: pip install ai-code-reviewer[server]")
            sys.exit(1)
        return
    
    # Initialize reviewer
    config_path = getattr(args, 'config', None) or 'config/review_standards.yaml'
    
    try:
        reviewer = CodeReviewer(config_path)
    except Exception as e:
        print(f"Error initializing code reviewer: {e}")
        sys.exit(1)
    
    try:
        if args.command == 'local':
            print(f"🔍 Reviewing local changes against '{args.base_branch}' branch...")
            reviews = reviewer.review_local_changes(args.base_branch)
            
            if not reviews:
                print("✅ No files to review or no issues found")
                return
            
            reviewer.print_local_review(reviews)
            
        elif args.command == 'pr':
            # Use environment variables as defaults, CLI args as overrides
            workspace = args.workspace or os.getenv('BITBUCKET_WORKSPACE')
            repo = args.repo or os.getenv('BITBUCKET_REPO')
            pr_id = args.pr_id
            
            if not workspace:
                print("❌ Error: workspace required (use --workspace or set BITBUCKET_WORKSPACE)")
                sys.exit(1)
            if not repo:
                print("❌ Error: repo required (use --repo or set BITBUCKET_REPO)")
                sys.exit(1)
            
            print(f"🔍 Reviewing PR #{pr_id} in {workspace}/{repo}...")
            reviews = reviewer.review_pull_request(workspace, repo, pr_id)
            
            critical_major_count = len([r for r in reviews if r.get('severity') in ['critical', 'major']])
            print(f"📝 Added {critical_major_count} comments to PR")
            reviewer.print_local_review(reviews)
            
    except KeyboardInterrupt:
        print("\n⚠️  Review interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during review: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
