# API Reference

This document provides detailed API reference for the AI Code Review Agent components.

## Core Classes

### CodeReviewer

Main orchestrator class that coordinates the review process.

```python
class CodeReviewer:
    def __init__(self, config_path: str = 'config/review_standards.yaml')
```

#### Methods

##### `review_local_changes(base_branch: str = 'develop') -> List[Dict]`

Reviews local code changes without posting to Bitbucket.

**Parameters:**
- `base_branch` (str): Base branch to compare against

**Returns:**
- `List[Dict]`: List of review findings

**Example:**
```python
reviewer = CodeReviewer()
reviews = reviewer.review_local_changes('main')
```

##### `review_pull_request(workspace: str, repo: str, pr_id: str) -> List[Dict]`

Reviews pull request and adds comments to Bitbucket.

**Parameters:**
- `workspace` (str): Bitbucket workspace name
- `repo` (str): Repository name
- `pr_id` (str): Pull request ID

**Returns:**
- `List[Dict]`: List of review findings

**Example:**
```python
reviewer = CodeReviewer()
reviews = reviewer.review_pull_request('CTAPPS', 'imageresizer', '120')
```

##### `print_local_review(reviews: List[Dict])`

Prints review results to console in formatted output.

**Parameters:**
- `reviews` (List[Dict]): Review findings from review methods

## Utility Classes

### BedrockClient

AWS Bedrock client for AI model interactions.

```python
class BedrockClient:
    def __init__(self, region: str = 'us-east-1')
```

#### Methods

##### `invoke_model(prompt: str, max_tokens: int = 4000) -> str`

Invokes the Claude 3.5 Sonnet model for code review.

**Parameters:**
- `prompt` (str): Review prompt with code and context
- `max_tokens` (int): Maximum tokens in response

**Returns:**
- `str`: Model response with review feedback

**Example:**
```python
client = BedrockClient()
response = client.invoke_model("Review this code: def hello(): pass")
```

### BitbucketAPI

Bitbucket API client for pull request operations.

```python
class BitbucketAPI:
    def __init__(self, base_url: str, token: str)
```

#### Methods

##### `get_pull_request(workspace: str, repo: str, pr_id: str) -> Dict`

Retrieves pull request details.

**Parameters:**
- `workspace` (str): Bitbucket workspace
- `repo` (str): Repository name  
- `pr_id` (str): Pull request ID

**Returns:**
- `Dict`: Pull request data

##### `add_comment(workspace: str, repo: str, pr_id: str, content: str, file_path: str = None, line_number: int = None) -> Dict`

Adds comment to pull request.

**Parameters:**
- `workspace` (str): Bitbucket workspace
- `repo` (str): Repository name
- `pr_id` (str): Pull request ID
- `content` (str): Comment content
- `file_path` (str, optional): File path for inline comments
- `line_number` (int, optional): Line number for inline comments

**Returns:**
- `Dict`: Comment creation response

## Utility Functions

### Git Utilities (`utils/git_utils.py`)

#### `get_current_branch() -> str`

Returns the current Git branch name.

**Returns:**
- `str`: Current branch name

#### `get_changed_files(base_branch: str = 'develop') -> List[str]`

Gets list of changed files between current branch and base branch.

**Parameters:**
- `base_branch` (str): Base branch to compare against

**Returns:**
- `List[str]`: List of changed file paths

#### `get_file_diff(file_path: str, base_branch: str = 'develop') -> str`

Gets diff for a specific file.

**Parameters:**
- `file_path` (str): Path to file
- `base_branch` (str): Base branch to compare against

**Returns:**
- `str`: Git diff output

#### `get_file_content(file_path: str) -> str`

Reads file content.

**Parameters:**
- `file_path` (str): Path to file

**Returns:**
- `str`: File content

### Agent Functions (`agents/code_review_agents.py`)

#### `load_agent_config(config_path: str = 'config/agents.yaml') -> dict`

Loads agent configuration from YAML file.

**Parameters:**
- `config_path` (str): Path to agent configuration file

**Returns:**
- `dict`: Agent configuration data

#### `create_agent_from_config(agent_name: str, bedrock_client: BedrockClient, config_path: str = 'config/agents.yaml') -> Agent`

Creates CrewAI agent from YAML configuration.

**Parameters:**
- `agent_name` (str): Name of agent in config
- `bedrock_client` (BedrockClient): Bedrock client instance
- `config_path` (str): Path to agent configuration file

**Returns:**
- `Agent`: CrewAI Agent instance

### Task Functions (`tasks/review_tasks.py`)

#### `load_task_config(config_path: str = 'config/agents.yaml') -> dict`

Loads task configuration from YAML file.

**Parameters:**
- `config_path` (str): Path to task configuration file

**Returns:**
- `dict`: Task configuration data

#### `create_task_from_config(task_name: str, agent: Agent, context: Dict, config_path: str = 'config/agents.yaml') -> Task`

Creates CrewAI task from YAML configuration.

**Parameters:**
- `task_name` (str): Name of task in config
- `agent` (Agent): CrewAI agent to assign task
- `context` (Dict): Context variables for task template
- `config_path` (str): Path to task configuration file

**Returns:**
- `Task`: CrewAI Task instance

## Data Structures

### Review Finding

Structure returned by review methods:

```python
{
    "file_path": str,           # Path to reviewed file
    "severity": str,            # critical|major|minor|suggestion
    "line_number": int,         # Line number (optional)
    "issue": str,               # Description of issue found
    "recommendation": str       # Suggested fix or improvement
}
```

### Agent Configuration

YAML structure for agent configuration:

```yaml
agents:
  agent_name:
    role: str                   # Agent role description
    goal: str                   # Agent goal
    backstory: str              # Agent background context
    verbose: bool               # Enable verbose output
    allow_delegation: bool      # Allow task delegation
```

### Task Configuration

YAML structure for task configuration:

```yaml
tasks:
  task_name:
    description_template: str   # Template with {variables}
    expected_output: str        # Description of expected output
```

### Review Standards Configuration

YAML structure for review standards:

```yaml
code_review_standards:
  category_name:
    - "Standard description 1"
    - "Standard description 2"

severity_levels:
  critical: "Description"
  major: "Description"
  minor: "Description"
  suggestion: "Description"
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BITBUCKET_URL` | Bitbucket API base URL | No | `https://git.cnvrmedia.net/rest/api/1.0` |
| `BITBUCKET_TOKEN` | Bitbucket API token | Yes (for PR reviews) | - |
| `AWS_REGION` | AWS region for Bedrock | No | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes | - |

## Error Handling

### Common Exceptions

#### `ConfigurationError`

Raised when configuration files are invalid or missing.

```python
try:
    reviewer = CodeReviewer('invalid_config.yaml')
except FileNotFoundError:
    print("Configuration file not found")
```

#### `GitError`

Raised when Git operations fail.

```python
try:
    files = get_changed_files('nonexistent_branch')
except subprocess.CalledProcessError:
    print("Git operation failed")
```

#### `BedrockError`

Raised when AWS Bedrock API calls fail.

```python
try:
    response = client.invoke_model(prompt)
except ClientError as e:
    print(f"Bedrock error: {e}")
```

#### `BitbucketError`

Raised when Bitbucket API calls fail.

```python
try:
    pr = client.get_pull_request(workspace, repo, pr_id)
except requests.HTTPError as e:
    print(f"Bitbucket API error: {e}")
```

## Extension Points

### Custom Agents

Create custom agents by extending the configuration:

```python
def create_custom_agent(bedrock_client: BedrockClient) -> Agent:
    return Agent(
        role="Custom Specialist",
        goal="Perform specialized review",
        backstory="Custom agent backstory",
        llm=bedrock_client
    )
```

### Custom Tasks

Create custom tasks with specific templates:

```python
def create_custom_task(agent: Agent, context: Dict) -> Task:
    return Task(
        description=f"Custom review task for {context['file_path']}",
        agent=agent,
        expected_output="Custom output format"
    )
```

### Custom Review Logic

Extend the CodeReviewer class:

```python
class CustomCodeReviewer(CodeReviewer):
    def custom_review_method(self, file_path: str) -> Dict:
        # Custom review logic
        pass
    
    def _should_review_file(self, file_path: str) -> bool:
        # Custom file filtering logic
        return super()._should_review_file(file_path)
```
