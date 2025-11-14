import yaml
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from crewai import Crew
from utils.git_utils import get_changed_files, get_file_diff, get_file_content
from utils.bitbucket_utils import create_bitbucket_client
from utils.bedrock_client import BedrockClient
from agents.code_review_agents import create_agent_from_config
from tasks.review_tasks import create_task_from_config

class CodeReviewer:
    def __init__(self, config_path: str = 'config/review_standards.yaml'):
        self.bedrock_client = BedrockClient()
        self.bitbucket_client = create_bitbucket_client()
        self.standards = self._load_standards(config_path)
        self.senior_agent = create_agent_from_config('senior_reviewer', self.bedrock_client)
        
        # Get minimum severity for comments from env
        self.min_severity = os.getenv('MIN_SEVERITY_FOR_COMMENTS', 'major').lower()
        self.severity_order = ['suggestion', 'minor', 'major', 'critical']
    
    def _load_standards(self, config_path: str) -> Dict:
        """Load code review standards from config file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def review_local_changes(self, base_branch: str = 'develop') -> List[Dict]:
        """Review local code changes without posting to Bitbucket."""
        changed_files = get_changed_files(base_branch)
        reviews = []
        
        for file_path in changed_files:
            if self._should_review_file(file_path):
                file_content = get_file_content(file_path)
                diff_content = get_file_diff(file_path, base_branch)
                
                context = {
                    'file_path': file_path,
                    'file_content': file_content,
                    'diff_content': diff_content,
                    'standards': self.standards
                }
                
                task = create_task_from_config('code_review', self.senior_agent, context)
                crew = Crew(agents=[self.senior_agent], tasks=[task])
                result = crew.kickoff()
                
                try:
                    review_data = json.loads(result)
                    # Ensure review_data has required fields
                    if isinstance(review_data, dict):
                        review_data['file_path'] = file_path
                        reviews.append(review_data)
                    elif isinstance(review_data, list):
                        # Handle case where AI returns array of reviews
                        for item in review_data:
                            if isinstance(item, dict):
                                item['file_path'] = file_path
                                reviews.append(item)
                    else:
                        raise ValueError("Invalid review format")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"⚠️  JSON parsing error for {file_path}: {e}")
                    print(f"Raw result: {result[:200]}...")
                    reviews.append({
                        'file_path': file_path,
                        'severity': 'minor',
                        'issue': 'Review parsing error',
                        'recommendation': result
                    })
        
        # Save reviews to file
        self._save_reviews_to_file(reviews, "local", "repository")
        
        return reviews
    
    def review_pull_request(self, workspace: str, repo: str, pr_id: str) -> List[Dict]:
        """Review pull request by fetching changes from Bitbucket server."""
        print(f"Fetching PR changes from server...")
        
        try:
            # Get PR changes from server
            changes = self.bitbucket_client.get_pull_request_changes(workspace, repo, pr_id)
            diff_text = self.bitbucket_client.get_pull_request_diff(workspace, repo, pr_id)
            
            reviews = []
            
            # Parse changed files from server response
            if isinstance(changes, dict) and 'values' in changes:
                changed_files = changes['values']
                print(f"Found {len(changed_files)} changed files in PR")
                
                for file_info in changed_files:
                    file_path = file_info.get('path', {}).get('toString', '')
                    
                    if self._should_review_file(file_path):
                        print(f"Reviewing: {file_path}")
                        
                        # Extract file-specific diff from full diff
                        file_diff = self._extract_file_diff(diff_text, file_path)
                        
                        context = {
                            'file_path': file_path,
                            'file_content': f"PR changes for {file_path}",
                            'diff_content': file_diff,
                            'standards': self.standards
                        }
                        
                        task = create_task_from_config('code_review', self.senior_agent, context)
                        crew = Crew(agents=[self.senior_agent], tasks=[task])
                        result = crew.kickoff()
                        
                        try:
                            review_data = json.loads(result)
                            # Ensure review_data has required fields
                            if isinstance(review_data, dict):
                                review_data['file_path'] = file_path
                                reviews.append(review_data)
                            elif isinstance(review_data, list):
                                # Handle case where AI returns array of reviews
                                for item in review_data:
                                    if isinstance(item, dict):
                                        item['file_path'] = file_path
                                        reviews.append(item)
                            else:
                                raise ValueError("Invalid review format")
                        except (json.JSONDecodeError, ValueError) as e:
                            print(f"⚠️  JSON parsing error for {file_path}: {e}")
                            print(f"Raw result: {result[:200]}...")
                            reviews.append({
                                'file_path': file_path,
                                'severity': 'minor',
                                'issue': 'Review parsing error',
                                'recommendation': result
                            })
            
            # Add comments to PR based on severity threshold
            comments_added = 0
            for review in reviews:
                severity = review.get('severity', '').lower()
                file_path = review.get('file_path', 'unknown')
                
                print(f"Review severity: '{severity}' for {file_path}")
                
                # Debug: show full review if severity is missing
                if not severity:
                    print(f"⚠️  Missing severity in review: {review}")
                
                if self._should_post_comment(severity):
                    try:
                        comment = f"**{severity.upper()}**: {review.get('issue', 'No issue specified')}\n\n{review.get('recommendation', 'No recommendation')}"
                        
                        result = self.bitbucket_client.add_comment(
                            workspace, repo, pr_id, comment,
                            review.get('file_path'), review.get('line_number')
                        )
                        comments_added += 1
                        print(f"✓ Added comment to PR for {file_path}")
                        
                    except Exception as e:
                        print(f"✗ Failed to add comment: {e}")
                else:
                    print(f"ℹ️  Skipping comment (severity: '{severity}', threshold: {self.min_severity}) for {file_path}")
            
            print(f"\n📝 Added {comments_added} comments to PR out of {len(reviews)} reviews")
            
            # Save reviews to file
            self._save_reviews_to_file(reviews, workspace, repo, pr_id)
            
            return reviews
            
        except Exception as e:
            print(f"Error fetching PR changes: {e}")
            return []
    
    def _extract_file_diff(self, full_diff: str, file_path: str) -> str:
        """Extract diff for specific file from full diff text."""
        lines = full_diff.split('\n')
        file_diff = []
        in_file = False
        
        for line in lines:
            if line.startswith('diff --git') and file_path in line:
                in_file = True
                file_diff = [line]
            elif line.startswith('diff --git') and in_file:
                break
            elif in_file:
                file_diff.append(line)
        
        return '\n'.join(file_diff)
    
    def _should_post_comment(self, severity: str) -> bool:
        """Check if severity level qualifies for PR comment."""
        if not severity or severity not in self.severity_order:
            return False
        
        min_index = self.severity_order.index(self.min_severity)
        severity_index = self.severity_order.index(severity)
        
        return severity_index >= min_index
    
    def _save_reviews_to_file(self, reviews: List[Dict], workspace: str, repo: str, pr_id: str = None):
        """Save reviews to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if pr_id:
            filename = f"reviews/pr_{workspace}_{repo}_{pr_id}_{timestamp}.json"
        else:
            filename = f"reviews/local_{timestamp}.json"
        
        # Create reviews directory if it doesn't exist
        os.makedirs("reviews", exist_ok=True)
        
        # Save reviews
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'workspace': workspace,
                'repo': repo,
                'pr_id': pr_id,
                'reviews': reviews,
                'summary': {
                    'total_files': len(reviews),
                    'critical': len([r for r in reviews if r.get('severity') == 'critical']),
                    'major': len([r for r in reviews if r.get('severity') == 'major']),
                    'minor': len([r for r in reviews if r.get('severity') == 'minor']),
                    'suggestion': len([r for r in reviews if r.get('severity') == 'suggestion'])
                }
            }, indent=2)
        
        print(f"💾 Reviews saved to: {filename}")
        return filename
    
    def _should_review_file(self, file_path: str) -> bool:
        """Check if file should be reviewed based on extension."""
        review_extensions = {'.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.cs', '.cpp', '.c', '.swift', '.kt', '.rs'}
        return any(file_path.endswith(ext) for ext in review_extensions)
        """Check if file should be reviewed based on extension."""
        review_extensions = {'.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.cs'}
        return any(file_path.endswith(ext) for ext in review_extensions)
    
    def print_local_review(self, reviews: List[Dict]):
        """Print review results to console."""
        print("\n" + "="*50)
        print("CODE REVIEW RESULTS")
        print("="*50)
        
        for review in reviews:
            print(f"\nFile: {review.get('file_path', 'Unknown')}")
            print(f"Severity: {review.get('severity', 'Unknown').upper()}")
            print(f"Issue: {review.get('issue', 'No issue specified')}")
            print(f"Recommendation: {review.get('recommendation', 'No recommendation')}")
            if review.get('line_number'):
                print(f"Line: {review['line_number']}")
            print("-" * 30)
