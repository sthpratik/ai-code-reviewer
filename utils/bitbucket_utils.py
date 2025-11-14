import requests
from typing import Dict, List
import os

class BitbucketAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.is_server = 'rest/api/1.0' in base_url
        
        if self.is_server:
            # Bitbucket Server uses Basic auth or Bearer token
            self.headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        else:
            # Bitbucket Cloud uses Bearer token
            self.headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
    
    def get_pull_request(self, workspace: str, repo: str, pr_id: str) -> Dict:
        """Get pull request details."""
        if self.is_server:
            # Bitbucket Server API
            url = f"{self.base_url}/projects/{workspace}/repos/{repo}/pull-requests/{pr_id}"
        else:
            # Bitbucket Cloud API
            url = f"{self.base_url}/repositories/{workspace}/{repo}/pullrequests/{pr_id}"
            
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_pull_request_diff(self, workspace: str, repo: str, pr_id: str) -> str:
        """Get pull request diff from server."""
        if self.is_server:
            url = f"{self.base_url}/projects/{workspace}/repos/{repo}/pull-requests/{pr_id}/diff"
        else:
            url = f"{self.base_url}/repositories/{workspace}/{repo}/pullrequests/{pr_id}/diff"
            
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text
    
    def get_pull_request_changes(self, workspace: str, repo: str, pr_id: str) -> List[Dict]:
        """Get list of changed files in PR."""
        if self.is_server:
            url = f"{self.base_url}/projects/{workspace}/repos/{repo}/pull-requests/{pr_id}/changes"
        else:
            url = f"{self.base_url}/repositories/{workspace}/{repo}/pullrequests/{pr_id}/diffstat"
            
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def add_comment(self, workspace: str, repo: str, pr_id: str, 
                   content: str, file_path: str = None, line_number: int = None) -> Dict:
        """Add comment to pull request."""
        if self.is_server:
            # Bitbucket Server API
            url = f"{self.base_url}/projects/{workspace}/repos/{repo}/pull-requests/{pr_id}/comments"
            comment_data = {"text": content}
            
            if file_path and line_number:
                comment_data["anchor"] = {
                    "path": file_path,
                    "line": line_number,
                    "lineType": "ADDED"
                }
        else:
            # Bitbucket Cloud API
            url = f"{self.base_url}/repositories/{workspace}/{repo}/pullrequests/{pr_id}/comments"
            comment_data = {"content": {"raw": content}}
            
            if file_path and line_number:
                comment_data["inline"] = {
                    "path": file_path,
                    "to": line_number
                }
        
        response = requests.post(url, json=comment_data, headers=self.headers)
        response.raise_for_status()
        return response.json()

def create_bitbucket_client() -> BitbucketAPI:
    """Create Bitbucket API client from environment variables."""
    return BitbucketAPI(
        base_url=os.getenv('BITBUCKET_URL', 'https://git.cnvrmedia.net/rest/api/1.0'),
        token=os.getenv('BITBUCKET_TOKEN')
    )
