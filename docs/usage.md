# Usage Guide

This guide covers common usage patterns and examples for the AI Code Review Agent.

## Command Line Interface

### Basic Syntax

```bash
python main.py [OPTIONS]
```

### Available Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `--mode` | Review mode: `local` or `bitbucket` | `local` | No |
| `--base-branch` | Base branch to compare against | `develop` | No |
| `--workspace` | Bitbucket workspace name | - | Yes (for bitbucket mode) |
| `--repo` | Bitbucket repository name | - | Yes (for bitbucket mode) |
| `--pr-id` | Pull request ID | - | Yes (for bitbucket mode) |
| `--config` | Path to review standards config | `config/review_standards.yaml` | No |

## Usage Examples

### 1. Local Code Review

Review changes in your current branch against `develop`:

```bash
python main.py --mode local --base-branch develop
```

Review against a different base branch:

```bash
python main.py --mode local --base-branch main
```

Use custom review standards:

```bash
python main.py --mode local --config config/custom_standards.yaml
```

### 2. Bitbucket Pull Request Review

Review a specific pull request:

```bash
python main.py \
  --mode bitbucket \
  --workspace mycompany \
  --repo myproject \
  --pr-id 120
```

### 3. Integration Examples

#### CI/CD Pipeline Integration

**Bamboo Build Script:**
```bash
#!/bin/bash
cd $BAMBOO_BUILD_WORKING_DIRECTORY

# Run code review on PR
python main.py \
  --mode bitbucket \
  --workspace ${bamboo.repository.git.repositoryUrl.split('/')[3]} \
  --repo ${bamboo.repository.git.repositoryUrl.split('/')[4].replace('.git', '')} \
  --pr-id ${bamboo.repository.pr.key}
```

**Jenkins Pipeline:**
```groovy
pipeline {
    agent any
    
    environment {
        BITBUCKET_TOKEN = credentials('bitbucket-token')
        AWS_ACCESS_KEY_ID = credentials('aws-access-key')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
    }
    
    stages {
        stage('Code Review') {
            when {
                changeRequest()
            }
            steps {
                script {
                    sh """
                        python main.py \
                          --mode bitbucket \
                          --workspace ${env.CHANGE_FORK} \
                          --repo ${env.JOB_NAME.split('/')[0]} \
                          --pr-id ${env.CHANGE_ID}
                    """
                }
            }
        }
    }
}
```

#### Git Hooks Integration

**Pre-push Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-push

echo "Running AI code review..."
python /path/to/codeReviewAgent/main.py --mode local --base-branch origin/develop

if [ $? -ne 0 ]; then
    echo "Code review found critical issues. Push aborted."
    exit 1
fi
```

## Output Formats

### Local Review Output

```
==================================================
CODE REVIEW RESULTS
==================================================

File: src/utils/database.py
Severity: CRITICAL
Issue: SQL injection vulnerability detected
Recommendation: Use parameterized queries instead of string concatenation
Line: 45
------------------------------

File: src/services/user_service.py
Severity: MAJOR
Issue: Inefficient database query in loop
Recommendation: Use bulk operations or optimize query with joins
Line: 78
------------------------------

File: src/models/user.py
Severity: MINOR
Issue: Missing docstring for public method
Recommendation: Add docstring describing method purpose and parameters
Line: 23
------------------------------
```

### Bitbucket Comments

Comments are automatically added to pull requests for `critical` and `major` issues:

```markdown
**CRITICAL**: SQL injection vulnerability detected

Use parameterized queries instead of string concatenation. The current implementation allows malicious users to inject SQL code through user input.

Recommended fix:
```python
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```
```

## Advanced Usage

### 1. Custom Review Standards

Create project-specific standards:

```yaml
# config/frontend_standards.yaml
code_review_standards:
  accessibility:
    - "Check for ARIA labels and roles"
    - "Validate keyboard navigation support"
    - "Ensure proper color contrast"
  
  performance:
    - "Review bundle size impact"
    - "Check for unnecessary re-renders"
    - "Validate lazy loading implementation"
  
  seo:
    - "Ensure proper meta tags"
    - "Check for semantic HTML structure"
    - "Validate structured data"
```

Usage:
```bash
python main.py --config config/frontend_standards.yaml
```

### 2. Multiple Agent Review

Modify `code_reviewer.py` to use multiple agents:

```python
def review_with_specialists(self, file_path: str):
    """Use specialized agents based on file type."""
    if file_path.endswith('.py'):
        agent = create_agent_from_config('python_specialist', self.bedrock_client)
    elif file_path.endswith(('.js', '.ts')):
        agent = create_agent_from_config('frontend_specialist', self.bedrock_client)
    elif file_path.endswith('.sql'):
        agent = create_agent_from_config('database_specialist', self.bedrock_client)
    else:
        agent = self.senior_agent
    
    return agent
```

### 3. Batch Processing

Review multiple repositories:

```bash
#!/bin/bash
# batch_review.sh

REPOS=("repo1" "repo2" "repo3")
WORKSPACE="mycompany"

for repo in "${REPOS[@]}"; do
    echo "Reviewing $repo..."
    
    # Get open PRs
    prs=$(curl -s "https://git.cnvrmedia.net/rest/api/1.0/repositories/$WORKSPACE/$repo/pullrequests?state=OPEN" \
          -H "Authorization: Bearer $BITBUCKET_TOKEN" | \
          jq -r '.values[].id')
    
    # Review each PR
    for pr in $prs; do
        python main.py \
          --mode bitbucket \
          --workspace $WORKSPACE \
          --repo $repo \
          --pr-id $pr
    done
done
```

### 4. Scheduled Reviews

Set up cron job for regular reviews:

```bash
# Add to crontab: crontab -e
# Review all open PRs daily at 9 AM
0 9 * * * /path/to/batch_review.sh >> /var/log/code_review.log 2>&1
```

## Best Practices

### 1. Review Workflow

**Recommended workflow:**
1. Run local review before pushing changes
2. Address critical and major issues
3. Push changes and create PR
4. Automated PR review runs via CI/CD
5. Address any new issues found
6. Merge after approval

### 2. Configuration Management

- Keep review standards in version control
- Use different configs for different project types
- Regularly update standards based on team feedback
- Document custom standards for team members

### 3. Performance Optimization

- Review smaller changesets for faster processing
- Use specific file patterns to limit scope
- Cache Bedrock responses for similar code patterns
- Run reviews in parallel for multiple files

### 4. Team Integration

- Set up team-wide standards and configurations
- Train team members on interpreting review feedback
- Establish process for handling review comments
- Regular review of review effectiveness

## Troubleshooting Common Issues

### 1. No Changes Detected

```bash
# Check if you're comparing against the right branch
git log --oneline develop..HEAD

# Ensure you have committed changes
git status
```

### 2. Review Takes Too Long

```bash
# Limit file types being reviewed
python main.py --mode local | grep -E "\.(py|js)$"

# Review specific files only
git diff --name-only develop..HEAD | head -5 | xargs python review_single_file.py
```

### 3. Too Many Minor Issues

Adjust severity thresholds in your configuration:

```yaml
# Only report major+ issues
severity_levels:
  critical: "Must fix before merge"
  major: "Should fix before merge"
  # Remove minor and suggestion levels
```

### 4. API Rate Limiting

Implement retry logic and delays:

```python
import time
import random

def review_with_backoff(self, retries=3):
    for attempt in range(retries):
        try:
            return self.review_local_changes()
        except Exception as e:
            if "rate limit" in str(e).lower():
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
            else:
                raise
```
