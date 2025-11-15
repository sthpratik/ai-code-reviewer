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
        
        # Debug mode for storing fetched files
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        if self.debug_mode:
            os.makedirs('debug_files', exist_ok=True)
    
    def _load_standards(self, config_path: str) -> Dict:
        """Load code review standards from config file and merge with custom standards if available."""
        with open(config_path, 'r') as f:
            standards = yaml.safe_load(f)
        
        # Check for custom coding standards
        custom_standards_path = '.amazonq/rules/coding-standards.md'
        if os.path.exists(custom_standards_path):
            with open(custom_standards_path, 'r') as f:
                custom_content = f.read().strip()
                if custom_content:
                    standards['custom_guidelines'] = custom_content
        
        return standards
    
    def _format_custom_guidelines(self) -> str:
        """Format custom guidelines section for the prompt."""
        if 'custom_guidelines' in self.standards:
            return f"\nAdditional Project-Specific Guidelines:\n{self.standards['custom_guidelines']}"
        return ""
    
    def _save_debug_file(self, file_path: str, content: str, workspace: str, repo: str, pr_id: str, diff_content: str = None) -> None:
        """Save fetched file content for debugging line number issues."""
        if not self.debug_mode:
            return
            
        # Create safe filename
        safe_filename = file_path.replace('/', '_').replace('\\', '_')
        debug_filename = f"debug_files/{workspace}_{repo}_PR{pr_id}_{safe_filename}"
        
        try:
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(f"# DEBUG FILE - Fetched from Bitbucket\n")
                f.write(f"# Workspace: {workspace}\n")
                f.write(f"# Repo: {repo}\n")
                f.write(f"# PR: {pr_id}\n")
                f.write(f"# File: {file_path}\n")
                f.write(f"# Content length: {len(content)} characters\n")
                f.write(f"# Lines: {len(content.splitlines())}\n")
                f.write("# " + "="*50 + "\n\n")
                f.write(content)
                
                if diff_content:
                    f.write(f"\n\n# DIFF CONTENT\n")
                    f.write("# " + "="*50 + "\n")
                    f.write(diff_content)
                    
            print(f"🐛 Debug: Saved {debug_filename}")
        except Exception as e:
            print(f"⚠️  Debug: Failed to save {debug_filename}: {e}")
    
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
                    'standards': self.standards,
                    'custom_guidelines_section': self._format_custom_guidelines()
                }
                
                task = create_task_from_config('code_review', self.senior_agent, context)
                crew = Crew(agents=[self.senior_agent], tasks=[task])
                result = crew.kickoff()
                
                try:
                    review_data = json.loads(result)
                    
                    # Handle different response formats from AI
                    if isinstance(review_data, dict):
                        # Check if it has a feedback/reviews array
                        if 'feedback' in review_data:
                            for item in review_data['feedback']:
                                item['file_path'] = file_path
                                reviews.append(item)
                        elif 'reviews' in review_data:
                            for item in review_data['reviews']:
                                item['file_path'] = file_path
                                reviews.append(item)
                        elif 'review_items' in review_data:
                            for item in review_data['review_items']:
                                item['file_path'] = file_path
                                reviews.append(item)
                        elif 'review_feedback' in review_data:
                            for item in review_data['review_feedback']:
                                item['file_path'] = file_path
                                reviews.append(item)
                        else:
                            # Single review object
                            review_data['file_path'] = file_path
                            reviews.append(review_data)
                    elif isinstance(review_data, list):
                        # Array of reviews
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
                        
                        # Try to get actual file content from Bitbucket
                        try:
                            file_content = self.bitbucket_client.get_file_content(workspace, repo, file_path)
                            print(f"📄 Fetched full file content ({len(file_content)} chars)")
                            
                            # Save debug file if debug mode is enabled
                            self._save_debug_file(file_path, file_content, workspace, repo, pr_id, file_diff)
                            
                        except Exception as e:
                            print(f"⚠️  Could not fetch file content: {e}")
                            file_content = f"PR changes for {file_path}\n\nDiff:\n{file_diff}"
                        
                        context = {
                            'file_path': file_path,
                            'file_content': file_content,
                            'diff_content': file_diff,
                            'standards': self.standards,
                            'custom_guidelines_section': self._format_custom_guidelines()
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
            
            print(f"\n📝 Generated {len(reviews)} reviews")
            print(f"📊 Review summary:")
            for review in reviews[:3]:  # Show first 3 reviews
                severity = review.get('severity', 'no severity')
                issue = review.get('issue', 'no issue')
                file_path = review.get('file_path', 'unknown')
                print(f"  - {file_path}: {severity} - {issue[:50]}...")
            
            # Save reviews to file (don't post comments yet)
            try:
                review_file = self._save_reviews_to_file(reviews, workspace, repo, pr_id)
                print(f"💾 Reviews saved to: {review_file}")
                print(f"📋 To publish comments: ./review publish {review_file}")
            except Exception as e:
                print(f"❌ Error saving reviews: {e}")
            
            return reviews
            
        except Exception as e:
            print(f"Error fetching PR changes: {e}")
            return []
    
    def _parse_diff_line_numbers(self, diff_text: str, file_path: str) -> Dict[int, int]:
        """Parse diff to map absolute line numbers to diff line numbers."""
        lines = diff_text.split('\n')
        line_mapping = {}  # absolute_line -> diff_line
        
        current_old_line = 0
        current_new_line = 0
        diff_line = 0
        
        for line in lines:
            diff_line += 1
            
            if line.startswith('@@'):
                # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
                import re
                match = re.match(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
                if match:
                    current_old_line = int(match.group(1)) - 1
                    current_new_line = int(match.group(2)) - 1
            elif line.startswith('+'):
                # Added line
                current_new_line += 1
                line_mapping[current_new_line] = diff_line
            elif line.startswith('-'):
                # Removed line
                current_old_line += 1
            elif not line.startswith('\\'):
                # Context line (unchanged)
                current_old_line += 1
                current_new_line += 1
                line_mapping[current_new_line] = diff_line
        
        return line_mapping
    
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
    
    def _should_review_file(self, file_path: str) -> bool:
        """Check if file should be reviewed based on extension."""
        review_extensions = {'.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.cs', '.cpp', '.c', '.swift', '.kt', '.rs'}
        return any(file_path.endswith(ext) for ext in review_extensions)
    
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
        data = {
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
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Reviews saved to: {filename}")
        return filename
    
    def publish_comments(self, review_file: str, min_severity: str = None):
        """Publish comments from a review file to Bitbucket PR."""
        if not os.path.exists(review_file):
            raise FileNotFoundError(f"Review file not found: {review_file}")
        
        with open(review_file, 'r') as f:
            data = json.load(f)
        
        reviews = data.get('reviews', [])
        workspace = data.get('workspace')
        repo = data.get('repo')
        pr_id = data.get('pr_id')
        
        if not all([workspace, repo, pr_id]):
            raise ValueError("Review file missing required PR information")
        
        # Use provided min_severity or fall back to instance setting
        threshold = min_severity or self.min_severity
        
        # Extract individual feedback items from nested structure
        individual_reviews = []
        for review in reviews:
            file_path = review.get('file_path', 'unknown')
            
            # Check if this review has a feedback array (nested structure)
            if 'feedback' in review:
                for feedback_item in review['feedback']:
                    feedback_item['file_path'] = file_path
                    individual_reviews.append(feedback_item)
            else:
                # Single review item
                individual_reviews.append(review)
        
        print(f"📋 Found {len(individual_reviews)} individual review items")
        
        # Get PR diff to map line numbers correctly
        try:
            pr_diff = self.bitbucket_client.get_pull_request_diff(workspace, repo, pr_id)
            print(f"📄 Fetched PR diff for line number mapping")
        except Exception as e:
            print(f"⚠️  Could not fetch PR diff: {e}")
            pr_diff = ""
        
        comments_added = 0
        for review in individual_reviews:
            severity = review.get('severity', '').lower()
            file_path = review.get('file_path', 'unknown')
            absolute_line = review.get('line_number')
            
            print(f"🔍 Processing: {file_path} - {severity} (line {absolute_line})")
            
            if self._should_post_comment_with_threshold(severity, threshold):
                try:
                    comment = f"**{severity.upper()}**: {review.get('issue', 'No issue specified')}\n\n{review.get('recommendation', 'No recommendation')}"
                    
                    # Convert absolute line number to diff line number for Bitbucket Server
                    diff_line = None
                    if absolute_line and pr_diff:
                        line_mapping = self._parse_diff_line_numbers(pr_diff, file_path)
                        diff_line = line_mapping.get(absolute_line)
                        if diff_line:
                            print(f"📍 Mapped line {absolute_line} → diff line {diff_line}")
                        else:
                            print(f"⚠️  Could not map line {absolute_line} to diff")
                    
                    # Use diff line number if available, otherwise use absolute line
                    line_for_comment = diff_line if diff_line else absolute_line
                    
                    if line_for_comment:
                        print(f"📍 Adding inline comment at line {line_for_comment}")
                        result = self.bitbucket_client.add_comment(
                            workspace, repo, pr_id, comment,
                            file_path, line_for_comment
                        )
                    else:
                        print(f"📝 Adding general PR comment (no line number)")
                        result = self.bitbucket_client.add_comment(
                            workspace, repo, pr_id, comment
                        )
                    
                    comments_added += 1
                    print(f"✓ Published comment for {file_path} (severity: {severity})")
                    
                except Exception as e:
                    print(f"✗ Failed to publish comment for {file_path}: {e}")
            else:
                print(f"ℹ️  Skipping {file_path} (severity: {severity}, threshold: {threshold})")
        
        print(f"\n📝 Published {comments_added} comments to PR #{pr_id}")
        return comments_added
    
    def _should_post_comment_with_threshold(self, severity: str, threshold: str) -> bool:
        """Check if severity meets threshold for posting."""
        if not severity or severity not in self.severity_order:
            return False
        
        min_index = self.severity_order.index(threshold)
        severity_index = self.severity_order.index(severity)
        
        return severity_index >= min_index
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
