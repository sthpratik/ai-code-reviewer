# Testing Guide

This guide explains how to test the AI Code Review Agent to ensure it's working correctly.

## Prerequisites

Before testing, ensure you have:
- Completed the [installation](installation.md)
- Configured your environment variables
- Access to a Git repository with some code changes

## Test 1: Basic Installation Test

Verify the application starts without errors:

```bash
python main.py --help
```

**Expected Output:**
```
usage: main.py [-h] [--mode {local,bitbucket}] [--base-branch BASE_BRANCH]
               [--workspace WORKSPACE] [--repo REPO] [--pr-id PR_ID]
               [--config CONFIG]

AI-powered code review agent

optional arguments:
  -h, --help            show this help message and exit
  --mode {local,bitbucket}
                        Review mode: local or bitbucket
  --base-branch BASE_BRANCH
                        Base branch to compare against
  --workspace WORKSPACE
                        Bitbucket workspace
  --repo REPO           Bitbucket repository
  --pr-id PR_ID         Pull request ID
  --config CONFIG       Path to review standards config
```

## Test 2: Configuration Loading Test

Test if configuration files load correctly:

```bash
python -c "
from code_reviewer import CodeReviewer
reviewer = CodeReviewer()
print('Configuration loaded successfully')
print(f'Standards: {len(reviewer.standards)} categories')
"
```

**Expected Output:**
```
Configuration loaded successfully
Standards: X categories
```

## Test 3: Git Integration Test

Test Git utilities with a sample repository:

```bash
python -c "
from utils.git_utils import get_current_branch, get_changed_files
print(f'Current branch: {get_current_branch()}')
print(f'Changed files: {get_changed_files(\"main\")}')
"
```

## Test 4: Local Code Review Test

### Step 1: Create Test Changes

Create a simple Python file with intentional issues:

```bash
# Create a test file
cat > test_review.py << 'EOF'
def bad_function():
    # This function has several issues
    x = 1
    y = 2
    z = x + y
    for i in range(1000000):  # Inefficient loop
        z = z + 1
    return z

def another_function(user_input):
    # Security issue - no input validation
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query
EOF

# Add and commit the file
git add test_review.py
git commit -m "Add test file for review"
```

### Step 2: Run Local Review

```bash
python main.py --mode local --base-branch main
```

**Expected Output:**
The agent should identify issues like:
- Performance: Inefficient loop
- Security: SQL injection vulnerability
- Code quality: Poor variable naming

### Step 3: Verify Review Results

Check that the output includes:
- File path: `test_review.py`
- Multiple severity levels
- Specific recommendations
- Line numbers (if applicable)

## Test 5: AWS Bedrock Connection Test

Test the Bedrock client directly:

```bash
python -c "
from utils.bedrock_client import BedrockClient
client = BedrockClient()
response = client.invoke_model('Hello, can you review code?')
print('Bedrock connection successful')
print(f'Response length: {len(response)} characters')
"
```

## Test 6: Bitbucket API Test

Test Bitbucket API connection (requires valid token):

```bash
python -c "
from utils.bitbucket_utils import create_bitbucket_client
client = create_bitbucket_client()
# Replace with your actual workspace/repo
try:
    pr = client.get_pull_request('workspace', 'repo', '1')
    print('Bitbucket API connection successful')
except Exception as e:
    print(f'Bitbucket API test failed: {e}')
"
```

## Test 7: End-to-End Bitbucket Test

### Prerequisites
- Active pull request in Bitbucket
- Valid Bitbucket token with write permissions

### Test Command
```bash
python main.py \
  --mode bitbucket \
  --workspace YOUR_WORKSPACE \
  --repo YOUR_REPO \
  --pr-id YOUR_PR_ID
```

### Verification
1. Check the console output for review results
2. Go to your Bitbucket PR and verify comments were added
3. Ensure only critical/major issues have comments

## Test 8: Custom Configuration Test

### Step 1: Create Custom Config

```bash
cat > config/test_standards.yaml << 'EOF'
code_review_standards:
  testing:
    - "Check for unit tests"
    - "Validate test coverage"
  
  documentation:
    - "Ensure docstrings exist"
    - "Check for README updates"

severity_levels:
  critical: "Must fix before merge"
  major: "Should fix before merge"
  minor: "Consider fixing"
  suggestion: "Optional improvement"
EOF
```

### Step 2: Test Custom Config

```bash
python main.py --mode local --config config/test_standards.yaml
```

## Test 9: Performance Test

Test with a larger codebase:

```bash
# Create multiple test files
for i in {1..5}; do
  cat > test_file_$i.py << EOF
def function_$i():
    # Test function $i
    data = []
    for j in range(1000):
        data.append(j * 2)
    return data
EOF
done

# Add and commit
git add test_file_*.py
git commit -m "Add multiple test files"

# Run review
time python main.py --mode local
```

Monitor:
- Execution time
- Memory usage
- API call efficiency

## Test 10: Error Handling Test

Test error scenarios:

### Invalid Configuration
```bash
# Test with missing config file
python main.py --config nonexistent.yaml
```

### Invalid Git Repository
```bash
# Test outside Git repository
cd /tmp
python /path/to/codeReviewAgent/main.py --mode local
```

### Invalid Bitbucket Credentials
```bash
# Test with invalid token
BITBUCKET_TOKEN=invalid_token python main.py --mode bitbucket --workspace test --repo test --pr-id 1
```

## Automated Test Suite

Create a comprehensive test script:

```bash
cat > run_tests.sh << 'EOF'
#!/bin/bash

echo "Running AI Code Review Agent Tests..."

# Test 1: Installation
echo "Test 1: Installation check"
python main.py --help > /dev/null && echo "✅ PASS" || echo "❌ FAIL"

# Test 2: Configuration loading
echo "Test 2: Configuration loading"
python -c "from code_reviewer import CodeReviewer; CodeReviewer()" && echo "✅ PASS" || echo "❌ FAIL"

# Test 3: Git utilities
echo "Test 3: Git utilities"
python -c "from utils.git_utils import get_current_branch; print(get_current_branch())" && echo "✅ PASS" || echo "❌ FAIL"

# Test 4: Bedrock client
echo "Test 4: Bedrock client"
python -c "from utils.bedrock_client import BedrockClient; BedrockClient()" && echo "✅ PASS" || echo "❌ FAIL"

echo "Tests completed!"
EOF

chmod +x run_tests.sh
./run_tests.sh
```

## Troubleshooting Test Issues

### Common Test Failures

**1. Configuration Loading Fails**
- Check YAML syntax in config files
- Verify file paths are correct
- Ensure all required fields are present

**2. Git Commands Fail**
- Ensure you're in a Git repository
- Check if Git is installed and in PATH
- Verify branch names exist

**3. AWS Bedrock Fails**
- Check AWS credentials configuration
- Verify Bedrock permissions
- Ensure correct region is set

**4. Bitbucket API Fails**
- Verify token permissions
- Check workspace/repo names
- Ensure PR exists and is accessible

### Debug Mode

Enable verbose logging for debugging:

```bash
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from code_reviewer import CodeReviewer
reviewer = CodeReviewer()
reviews = reviewer.review_local_changes()
"
```

### Test Data Cleanup

Clean up test files after testing:

```bash
# Remove test files
git rm test_*.py
git commit -m "Remove test files"

# Reset to original state
git reset --hard HEAD~2  # Adjust number based on test commits
```
