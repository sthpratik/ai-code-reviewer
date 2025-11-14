# API Examples

This document provides comprehensive examples for using the AI Code Review Agent API.

## Quick Start

### Simple CLI Commands

**Review local changes:**
```bash
./review local                    # Compare with develop branch
./review local --base main       # Compare with main branch
```

**Review Bitbucket PR:**
```bash
./review pr --workspace CTAPPS --repo imageresizer --pr-id 120
```

## REST API Examples

### Base URL
```
http://localhost:8000
```

### Health Check
```bash
curl http://localhost/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Code Review Agent"
}
```

### Local Code Review

Review changes in your current working directory against a base branch.

**Request:**
```bash
curl -X POST http://localhost/review/local \
  -H "Content-Type: application/json" \
  -d '{
    "base_branch": "develop",
    "config_path": "config/review_standards.yaml"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Reviewed 3 files",
  "reviews": [
    {
      "file_path": "src/utils.py",
      "severity": "major",
      "line_number": 45,
      "issue": "Potential memory leak in loop",
      "recommendation": "Consider using a generator or breaking large datasets into chunks"
    },
    {
      "file_path": "src/api.py", 
      "severity": "minor",
      "issue": "Missing error handling",
      "recommendation": "Add try-catch blocks for database operations"
    }
  ]
}
```

### Bitbucket Pull Request Review

Review a pull request directly from Bitbucket Server and automatically add comments.

**Request:**
```bash
curl -X POST http://localhost/review/bitbucket \
  -H "Content-Type: application/json" \
  -d '{
    "workspace": "CTAPPS",
    "repo": "imageresizer", 
    "pr_id": "120",
    "config_path": "config/review_standards.yaml"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Reviewed 5 files, added 2 comments to PR",
  "reviews": [
    {
      "file_path": "lib/image-processor.js",
      "severity": "critical",
      "line_number": 23,
      "issue": "Potential security vulnerability - unvalidated input",
      "recommendation": "Validate and sanitize all user inputs before processing"
    },
    {
      "file_path": "lib/utils.js",
      "severity": "major", 
      "issue": "Performance concern - synchronous file operations",
      "recommendation": "Use async file operations to prevent blocking"
    }
  ]
}
```

### Get Review Standards

Retrieve current review configuration.

**Request:**
```bash
curl http://localhost/config/standards
```

**Response:**
```json
{
  "code_review_standards": {
    "performance": [
      "Check for inefficient loops and nested iterations",
      "Identify potential memory leaks",
      "Review database query optimization"
    ],
    "security": [
      "Check for input validation",
      "Review authentication and authorization",
      "Validate sensitive data handling"
    ]
  },
  "severity_levels": {
    "critical": "Must fix before merge",
    "major": "Should fix before merge", 
    "minor": "Consider fixing",
    "suggestion": "Optional improvement"
  }
}
```

## Advanced CLI Examples

### Local Review with Custom Config
```bash
python main.py --mode local --base-branch main --config custom_standards.yaml
```

### Bitbucket Review with All Options
```bash
python main.py --mode bitbucket \
  --workspace CTAPPS \
  --repo imageresizer \
  --pr-id 120 \
  --config config/strict_standards.yaml
```

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Missing required parameter: workspace"
}
```

### 401 Unauthorized
```json
{
  "status": "error", 
  "message": "Invalid Bitbucket token or insufficient permissions"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Code reviewer not initialized"
}
```

## Batch Operations

### Review Multiple PRs
```bash
#!/bin/bash
# Review multiple PRs in sequence
for pr_id in 120 121 122; do
  echo "Reviewing PR $pr_id..."
  ./review pr --workspace CTAPPS --repo imageresizer --pr-id $pr_id
done
```

### Review All Open PRs
```bash
#!/bin/bash
# Get all open PRs and review them
prs=$(curl -s "https://git.cnvrmedia.net/rest/api/1.0/projects/CTAPPS/repos/imageresizer/pull-requests?state=OPEN" \
  -H "Authorization: Bearer $BITBUCKET_TOKEN" | \
  jq -r '.values[].id')

for pr_id in $prs; do
  ./review pr --workspace CTAPPS --repo imageresizer --pr-id $pr_id
done
```

## Integration Examples

### GitHub Actions
```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Code Review
        run: |
          curl -X POST ${{ secrets.REVIEW_API_URL }}/review/local \
            -H "Content-Type: application/json" \
            -d '{"base_branch": "main"}'
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Code Review') {
            steps {
                script {
                    sh '''
                        curl -X POST http://review-service:8000/review/local \
                          -H "Content-Type: application/json" \
                          -d '{"base_branch": "develop"}'
                    '''
                }
            }
        }
    }
}
```

### Webhook Integration
```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    if data['eventKey'] == 'pr:opened':
        pr_id = data['pullRequest']['id']
        workspace = data['pullRequest']['toRef']['repository']['project']['key']
        repo = data['pullRequest']['toRef']['repository']['slug']
        
        # Trigger review
        response = requests.post('http://localhost:8000/review/bitbucket', json={
            'workspace': workspace,
            'repo': repo,
            'pr_id': str(pr_id)
        })
        
        return response.json()
```

## Testing Examples

### Test Bitbucket Connection
```bash
python test_token.py
```

### Test PR Access
```bash
python debug_pr.py CTAPPS imageresizer 120
```

### Test PR Diff Fetch
```bash
python test_pr_diff.py CTAPPS imageresizer 120
```

## Configuration Examples

### Custom Review Standards
```yaml
# config/strict_standards.yaml
code_review_standards:
  performance:
    - "All database queries must use indexes"
    - "No synchronous operations in async functions"
    - "Memory usage must be under 100MB per request"
  
  security:
    - "All inputs must be validated and sanitized"
    - "No hardcoded secrets or credentials"
    - "HTTPS required for all external calls"
  
  testing:
    - "Unit test coverage must be above 80%"
    - "All public methods must have tests"
    - "Integration tests for API endpoints"

severity_levels:
  critical: "Blocks deployment"
  major: "Must fix before merge"
  minor: "Fix in next iteration"
  suggestion: "Consider for improvement"
```

### Environment Configuration
```bash
# .env
BITBUCKET_URL=https://git.cnvrmedia.net/rest/api/1.0
BITBUCKET_TOKEN=your_token_here
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```
