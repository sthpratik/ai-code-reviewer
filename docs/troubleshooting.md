# Troubleshooting Guide

This guide helps resolve common issues with the AI Code Review Agent.

## Installation Issues

### Python Version Compatibility

**Problem:** `ModuleNotFoundError` or syntax errors

**Solution:**
```bash
# Check Python version (requires 3.8+)
python --version

# Use specific Python version if needed
python3.9 -m pip install -r requirements.txt
python3.9 main.py --mode local
```

### Dependency Installation Failures

**Problem:** `pip install` fails with compilation errors

**Solution:**
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install with no cache
pip install --no-cache-dir -r requirements.txt

# For M1 Macs with compilation issues
pip install --no-deps crewai
```

### Virtual Environment Issues

**Problem:** Packages not found despite installation

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Verify you're in the right environment
which python
pip list
```

## Configuration Issues

### YAML Syntax Errors

**Problem:** `yaml.scanner.ScannerError`

**Solution:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/review_standards.yaml'))"

# Common issues:
# - Incorrect indentation (use spaces, not tabs)
# - Missing quotes around special characters
# - Inconsistent list formatting
```

**Example Fix:**
```yaml
# ❌ Incorrect
code_review_standards:
performance:
- Check loops

# ✅ Correct  
code_review_standards:
  performance:
    - "Check loops"
```

### Environment Variable Issues

**Problem:** `KeyError` or authentication failures

**Solution:**
```bash
# Check if .env file exists and is loaded
ls -la .env
cat .env

# Verify environment variables are set
echo $BITBUCKET_TOKEN
echo $AWS_ACCESS_KEY_ID

# Load environment manually if needed
export $(cat .env | xargs)
```

### Missing Configuration Files

**Problem:** `FileNotFoundError: config/review_standards.yaml`

**Solution:**
```bash
# Check if config files exist
ls -la config/

# Create missing config from template
cp config/review_standards.yaml.template config/review_standards.yaml

# Verify file permissions
chmod 644 config/*.yaml
```

## AWS Bedrock Issues

### Authentication Failures

**Problem:** `UnauthorizedOperation` or `AccessDenied`

**Solution:**
```bash
# Test AWS credentials
aws sts get-caller-identity

# Check Bedrock permissions
aws bedrock list-foundation-models --region us-east-1

# Verify IAM policy includes Bedrock access
aws iam get-user-policy --user-name YOUR_USER --policy-name BedrockPolicy
```

**Required IAM Policy:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

### Model Not Available

**Problem:** `ValidationException: The model ID is not supported`

**Solution:**
```bash
# Check available models in your region
aws bedrock list-foundation-models --region us-east-1 | grep claude

# Update model ID in bedrock_client.py if needed
# Current: anthropic.claude-3-5-sonnet-20241022-v2:0
```

### Region Issues

**Problem:** `InvalidRegion` or model not found

**Solution:**
```bash
# Check Bedrock availability by region
aws bedrock list-foundation-models --region us-west-2

# Update region in .env file
AWS_REGION=us-west-2
```

### Rate Limiting

**Problem:** `ThrottlingException` or `TooManyRequestsException`

**Solution:**
```python
# Add retry logic to bedrock_client.py
import time
import random
from botocore.exceptions import ClientError

def invoke_model_with_retry(self, prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            return self.invoke_model(prompt)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
            else:
                raise
    raise Exception("Max retries exceeded")
```

## Git Integration Issues

### Repository Not Found

**Problem:** `fatal: not a git repository`

**Solution:**
```bash
# Ensure you're in a Git repository
git status

# Initialize Git if needed
git init
git remote add origin <repository-url>

# Check current directory
pwd
ls -la .git/
```

### Branch Not Found

**Problem:** `fatal: bad revision 'develop'`

**Solution:**
```bash
# List available branches
git branch -a

# Use existing branch name
python main.py --mode local --base-branch main

# Fetch remote branches if needed
git fetch origin
```

### No Changes Detected

**Problem:** Empty review results

**Solution:**
```bash
# Check for actual changes
git diff develop..HEAD --name-only

# Ensure changes are committed
git status
git add .
git commit -m "Changes for review"

# Check file extensions are supported
git diff develop..HEAD --name-only | grep -E '\.(py|js|ts|java)$'
```

### Permission Issues

**Problem:** `Permission denied` for Git operations

**Solution:**
```bash
# Check Git configuration
git config --list

# Set up SSH key or use HTTPS
git remote set-url origin https://github.com/user/repo.git

# Check file permissions
ls -la .git/
chmod -R 755 .git/
```

## Bitbucket API Issues

### Authentication Failures

**Problem:** `401 Unauthorized`

**Solution:**
```bash
# Test token manually
curl -H "Authorization: Bearer $BITBUCKET_TOKEN" \
     https://git.cnvrmedia.net/rest/api/1.0/user

# Check token permissions in Bitbucket settings
# Required: Repositories (Read, Write), Pull requests (Read, Write)

# Verify token format (no extra spaces/characters)
echo "$BITBUCKET_TOKEN" | wc -c
```

### Repository Access Issues

**Problem:** `404 Not Found` for repository

**Solution:**
```bash
# Verify workspace and repo names
curl -H "Authorization: Bearer $BITBUCKET_TOKEN" \
     https://git.cnvrmedia.net/rest/api/1.0/repositories/WORKSPACE

# Check exact repository name (case-sensitive)
# Use repository slug, not display name
```

### Pull Request Not Found

**Problem:** `404 Not Found` for pull request

**Solution:**
```bash
# List available pull requests
curl -H "Authorization: Bearer $BITBUCKET_TOKEN" \
     https://git.cnvrmedia.net/rest/api/1.0/repositories/WORKSPACE/REPO/pullrequests

# Verify PR ID is numeric, not branch name
# Check PR status (open/merged/declined)
```

### Rate Limiting

**Problem:** `429 Too Many Requests`

**Solution:**
```python
# Add rate limiting to bitbucket_utils.py
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 1.0 / calls_per_second - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

# Apply to API methods
@rate_limit(calls_per_second=0.5)
def add_comment(self, ...):
    # existing code
```

## CrewAI Issues

### Agent Creation Failures

**Problem:** `TypeError` or `ValidationError` in agent creation

**Solution:**
```python
# Verify agent configuration structure
import yaml
config = yaml.safe_load(open('config/agents.yaml'))
print(config['agents']['senior_reviewer'])

# Check required fields are present
required_fields = ['role', 'goal', 'backstory']
for field in required_fields:
    assert field in config['agents']['senior_reviewer']
```

### Task Execution Failures

**Problem:** `CrewAI execution failed`

**Solution:**
```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Check task description formatting
context = {
    'file_path': 'test.py',
    'file_content': 'def test(): pass',
    'diff_content': '+def test(): pass',
    'standards': {'quality': ['Check naming']}
}

# Verify template variables match context keys
template = config['tasks']['code_review']['description_template']
print(template.format(**context))
```

### Memory Issues

**Problem:** `OutOfMemoryError` with large files

**Solution:**
```python
# Limit file size for review
def _should_review_file(self, file_path: str) -> bool:
    if os.path.getsize(file_path) > 1024 * 1024:  # 1MB limit
        return False
    return super()._should_review_file(file_path)

# Process files in batches
def review_in_batches(self, files: List[str], batch_size: int = 5):
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        yield self.review_files(batch)
```

## Performance Issues

### Slow Review Times

**Problem:** Reviews take too long to complete

**Solutions:**

1. **Limit file scope:**
```bash
# Review only specific file types
git diff develop..HEAD --name-only | grep '\.py$' | head -10
```

2. **Optimize prompts:**
```python
# Reduce prompt size in task templates
description_template: |
  Review: {file_path}
  Changes: {diff_content}
  Focus on: critical issues only
```

3. **Use smaller model context:**
```python
# Reduce max_tokens in bedrock_client.py
def invoke_model(self, prompt: str, max_tokens: int = 2000):
```

### High API Costs

**Problem:** Bedrock usage costs are high

**Solutions:**

1. **Cache similar reviews:**
```python
import hashlib
import json

def get_cache_key(self, file_content: str, diff: str) -> str:
    content = f"{file_content}{diff}"
    return hashlib.md5(content.encode()).hexdigest()

def review_with_cache(self, file_path: str):
    cache_key = self.get_cache_key(file_content, diff)
    if cache_key in self.review_cache:
        return self.review_cache[cache_key]
    
    result = self.review_file(file_path)
    self.review_cache[cache_key] = result
    return result
```

2. **Filter files more aggressively:**
```python
def _should_review_file(self, file_path: str) -> bool:
    # Skip test files, generated files, etc.
    skip_patterns = ['test_', '_test.py', 'generated/', 'vendor/']
    if any(pattern in file_path for pattern in skip_patterns):
        return False
    return super()._should_review_file(file_path)
```

## Debugging Tips

### Enable Verbose Logging

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Test Individual Components

```bash
# Test Git utilities
python -c "from utils.git_utils import *; print(get_current_branch())"

# Test Bedrock client
python -c "from utils.bedrock_client import BedrockClient; BedrockClient().invoke_model('test')"

# Test Bitbucket API
python -c "from utils.bitbucket_utils import create_bitbucket_client; create_bitbucket_client()"
```

### Validate Configurations

```bash
# Validate YAML files
python -c "import yaml; print('Valid YAML' if yaml.safe_load(open('config/agents.yaml')) else 'Invalid')"

# Check environment variables
python -c "import os; print({k:v for k,v in os.environ.items() if 'BITBUCKET' in k or 'AWS' in k})"
```

### Monitor Resource Usage

```bash
# Monitor memory usage
python -c "
import psutil
import time
from code_reviewer import CodeReviewer

process = psutil.Process()
print(f'Initial memory: {process.memory_info().rss / 1024 / 1024:.1f} MB')

reviewer = CodeReviewer()
reviews = reviewer.review_local_changes()

print(f'Final memory: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

## Getting Help

If issues persist:

1. **Check logs:** Look for detailed error messages
2. **Verify prerequisites:** Ensure all requirements are met
3. **Test minimal example:** Start with a simple test case
4. **Check permissions:** Verify all API tokens and AWS permissions
5. **Update dependencies:** Ensure you're using compatible versions

### Useful Debug Commands

```bash
# System information
python --version
pip list | grep -E "(crewai|boto3|requests|yaml)"

# Git information  
git --version
git status
git branch -a

# AWS information
aws --version
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-east-1

# Network connectivity
curl -I https://git.cnvrmedia.net/rest/api/1.0/
curl -I https://bedrock-runtime.us-east-1.amazonaws.com/
```
