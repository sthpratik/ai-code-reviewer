# Bitbucket Integration

This guide explains how to integrate the AI Code Review Agent with Bitbucket (Bamboo) for automated pull request reviews.

## Getting Bitbucket API Token

### Step 1: Create App Password

1. Go to your Bitbucket account settings
2. Navigate to **App passwords** under **Access management**
3. Click **Create app password**
4. Give it a name (e.g., "AI Code Review Agent")
5. Select the following permissions:
   - **Repositories**: Read, Write
   - **Pull requests**: Read, Write
   - **Issues**: Read, Write (optional)

### Step 2: Configure Environment

Add your token to the `.env` file:

```bash
BITBUCKET_TOKEN=your_app_password_here
BITBUCKET_URL=https://git.cnvrmedia.net/rest/api/1.0
```

## Finding Pull Request ID

### Method 1: From Bitbucket Web UI

1. Navigate to your repository in Bitbucket
2. Go to **Pull requests**
3. Click on the pull request you want to review
4. Look at the URL: `https://bitbucket.org/workspace/repo/pull-requests/120`
5. The PR ID is the number at the end (e.g., `120`)

### Method 2: From Bamboo Build

If you're using Bamboo for CI/CD:

1. In your Bamboo build plan, the PR ID is available as:
   - `${bamboo.repository.pr.key}` - Pull request ID
   - `${bamboo.repository.pr.sourceBranch}` - Source branch
   - `${bamboo.repository.pr.targetBranch}` - Target branch

### Method 3: Using Bitbucket API

```bash
curl -X GET \
  "https://git.cnvrmedia.net/rest/api/1.0/repositories/WORKSPACE/REPO/pullrequests" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Integration Examples

### Manual PR Review

```bash
python main.py \
  --mode bitbucket \
  --workspace CTAPPS \
  --repo imageresizer \
  --pr-id 120
```

### Bamboo Integration

Create a Bamboo task that runs the code review:

```bash
#!/bin/bash
cd /path/to/codeReviewAgent

python main.py \
  --mode bitbucket \
  --workspace ${bamboo.planRepository.1.repositoryUrl.split('/')[3]} \
  --repo ${bamboo.planRepository.1.name} \
  --pr-id ${bamboo.repository.pr.key}
```

### GitHub Actions (Alternative CI)

```yaml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run AI Code Review
        env:
          BITBUCKET_TOKEN: ${{ secrets.BITBUCKET_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          python main.py \
            --mode bitbucket \
            --workspace ${{ github.repository_owner }} \
            --repo ${{ github.event.repository.name }} \
            --pr-id ${{ github.event.pull_request.number }}
```

## Comment Types

The agent adds different types of comments based on severity:

### Critical Issues
- **Automatically posted** to PR
- Must be fixed before merge
- Examples: Security vulnerabilities, performance bottlenecks

### Major Issues  
- **Automatically posted** to PR
- Should be fixed before merge
- Examples: Code quality issues, scalability concerns

### Minor Issues
- **Not posted** automatically (local review only)
- Consider fixing
- Examples: Style improvements, minor optimizations

### Suggestions
- **Not posted** automatically (local review only)  
- Optional improvements
- Examples: Alternative approaches, best practices

## Webhook Integration

For real-time PR reviews, set up a webhook:

### Step 1: Create Webhook Endpoint

```python
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    if data.get('eventKey') == 'pullrequest:created':
        pr_data = data['pullRequest']
        workspace = data['repository']['workspace']['slug']
        repo = data['repository']['name']
        pr_id = pr_data['id']
        
        # Run code review
        subprocess.run([
            'python', 'main.py',
            '--mode', 'bitbucket',
            '--workspace', workspace,
            '--repo', repo,
            '--pr-id', str(pr_id)
        ])
    
    return 'OK'
```

### Step 2: Configure Bitbucket Webhook

1. Go to repository settings in Bitbucket
2. Navigate to **Webhooks**
3. Add webhook URL: `https://your-server.com/webhook`
4. Select events: **Pull request created**, **Pull request updated**

## Troubleshooting

### Common Issues

**1. Authentication Failed**
- Verify your app password is correct
- Check if the token has required permissions
- Ensure the workspace name is correct

**2. PR Not Found**
- Verify the PR ID is correct
- Check if the repository name matches exactly
- Ensure the PR exists and is open

**3. Comments Not Appearing**
- Check if the token has write permissions
- Verify the PR is not from a fork (limited permissions)
- Look for API rate limiting

**4. Permission Denied**
- Ensure your token has repository write access
- Check if you're a member of the workspace
- Verify the repository is not private (unless you have access)
