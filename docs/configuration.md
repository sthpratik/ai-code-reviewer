# Configuration

The AI Code Review Agent uses YAML configuration files to customize review standards and agent behavior.

## Review Standards Configuration

### File: `config/review_standards.yaml`

```yaml
code_review_standards:
  performance:
    - "Check for inefficient loops and nested iterations"
    - "Identify potential memory leaks"
    - "Review database query optimization"
    - "Validate caching strategies"
  
  scalability:
    - "Assess code modularity and separation of concerns"
    - "Review error handling and resilience patterns"
    - "Check for hardcoded limits and configurations"
    - "Validate async/await usage"
  
  code_quality:
    - "Ensure proper naming conventions"
    - "Check for code duplication (DRY principle)"
    - "Validate function size and complexity"
    - "Review proper use of design patterns"
  
  readability:
    - "Check for clear and meaningful comments"
    - "Validate consistent code formatting"
    - "Ensure logical code organization"
    - "Review variable and function naming clarity"
  
  security:
    - "Check for input validation"
    - "Review authentication and authorization"
    - "Validate sensitive data handling"
    - "Check for SQL injection vulnerabilities"

severity_levels:
  critical: "Must fix before merge"
  major: "Should fix before merge"
  minor: "Consider fixing"
  suggestion: "Optional improvement"
```

## Custom Project Guidelines

### File: `.amazonq/rules/coding-standards.md`

Create this file to add project-specific coding standards that will be automatically included in all code reviews. The system automatically detects and loads this file when it exists.

**Example structure:**

```markdown
# Project-Specific Coding Standards

## General Guidelines
- Use meaningful variable names that clearly express intent
- Keep functions small and focused on a single responsibility
- Avoid deep nesting (max 3-4 levels)
- Remove commented-out code and debug statements

## Language-Specific Guidelines

### Python
- Use type hints for all function parameters and return values
- Follow PEP 8 naming conventions strictly
- Prefer f-strings over .format() or % formatting
- Use dataclasses for simple data containers

### JavaScript/TypeScript
- Use const/let instead of var
- Prefer async/await over Promise chains
- Use TypeScript strict mode when available
- Follow consistent naming conventions (camelCase)

### Java
- Follow standard naming conventions
- Use appropriate access modifiers
- Prefer composition over inheritance
- Handle checked exceptions appropriately

## Security Requirements
- Never commit secrets, API keys, or sensitive data
- Validate and sanitize all external inputs
- Use secure communication protocols (HTTPS, TLS)
- Follow principle of least privilege for access controls

## Testing Standards
- Write tests for critical business logic
- Include both positive and negative test scenarios
- Use descriptive test names that explain the expected behavior
- Mock external dependencies to ensure test isolation
```

**Key Features:**
- **Automatic Detection**: The system automatically checks for this file during code reviews
- **Language Agnostic**: Supports guidelines for any programming language
- **Team Collaboration**: Can be version controlled and shared across the team
- **Flexible Format**: Use standard Markdown formatting for easy readability

### Customizing Review Standards

You can modify the base standards to match your team's requirements:

```yaml
code_review_standards:
  # Add custom categories
  documentation:
    - "Ensure all public methods have docstrings"
    - "Check for README updates"
    - "Validate API documentation"
  
  testing:
    - "Verify unit test coverage"
    - "Check for integration tests"
    - "Validate test naming conventions"
  
  # Language-specific standards
  python_specific:
    - "Follow PEP 8 style guidelines"
    - "Use type hints where appropriate"
    - "Validate import organization"
```

## Agent Configuration

### File: `config/agents.yaml`

```yaml
agents:
  senior_reviewer:
    role: "Senior Software Engineer"
    goal: "Perform comprehensive code review focusing on scalability, performance, and quality"
    backstory: |
      You are a senior software engineer with 10+ years of experience. 
      You have expertise in code architecture, performance optimization, and best practices.
      You provide constructive feedback that helps teams improve code quality.
    verbose: true
    allow_delegation: false
    
  security_reviewer:
    role: "Security Engineer"
    goal: "Identify security vulnerabilities and ensure secure coding practices"
    backstory: |
      You are a security engineer specializing in application security.
      You focus on identifying potential security risks, vulnerabilities, and 
      ensuring compliance with security best practices.
    verbose: true
    allow_delegation: false

tasks:
  code_review:
    description_template: |
      Review the code changes in file: {file_path}
      
      File Content:
      {file_content}
      
      Changes (diff):
      {diff_content}
      
      Review Standards:
      {standards}
      
      Provide detailed feedback on:
      1. Code quality and readability
      2. Performance implications
      3. Scalability concerns
      4. Security issues
      5. Best practices adherence
      
      Format your response as JSON with:
      - file_path: string
      - severity: critical|major|minor|suggestion
      - line_number: int (if applicable)
      - issue: string
      - recommendation: string
    expected_output: "JSON formatted code review feedback"
```

### Creating Custom Agents

Add new agents for specific review focuses:

```yaml
agents:
  # Frontend specialist
  frontend_reviewer:
    role: "Frontend Specialist"
    goal: "Review frontend code for accessibility, performance, and user experience"
    backstory: |
      You are a frontend specialist with expertise in modern web technologies,
      accessibility standards, and user experience optimization.
    verbose: true
    allow_delegation: false
  
  # Database specialist  
  database_reviewer:
    role: "Database Engineer"
    goal: "Review database-related code for performance and data integrity"
    backstory: |
      You are a database engineer with deep knowledge of SQL optimization,
      data modeling, and database performance tuning.
    verbose: true
    allow_delegation: false
```

## Environment Configuration

### File: `.env`

```bash
# Bitbucket Configuration
BITBUCKET_URL=https://git.cnvrmedia.net/rest/api/1.0
BITBUCKET_TOKEN=your_bitbucket_token_here

# AWS Configuration (for Bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Optional: Custom model configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
MAX_TOKENS=4000

# Optional: Review configuration
REVIEW_FILE_EXTENSIONS=.py,.js,.ts,.java,.go,.rb,.php,.cs
MIN_SEVERITY_FOR_COMMENTS=major
```

## File Type Configuration

Configure which file types should be reviewed by modifying the `_should_review_file` method in `code_reviewer.py`:

```python
def _should_review_file(self, file_path: str) -> bool:
    """Check if file should be reviewed based on extension."""
    review_extensions = {
        '.py',    # Python
        '.js',    # JavaScript
        '.ts',    # TypeScript
        '.java',  # Java
        '.go',    # Go
        '.rb',    # Ruby
        '.php',   # PHP
        '.cs',    # C#
        '.cpp',   # C++
        '.c',     # C
        '.swift', # Swift
        '.kt',    # Kotlin
        '.rs',    # Rust
    }
    return any(file_path.endswith(ext) for ext in review_extensions)
```

## Advanced Configuration

### Custom Task Templates

Create specialized task templates for different review types:

```yaml
tasks:
  security_review:
    description_template: |
      Perform a security-focused review of: {file_path}
      
      Focus on:
      - Input validation and sanitization
      - Authentication and authorization
      - Data encryption and protection
      - Potential injection vulnerabilities
      - Secure coding practices
      
      Code: {file_content}
      Changes: {diff_content}
    expected_output: "Security assessment with risk levels"
  
  performance_review:
    description_template: |
      Analyze performance implications of changes in: {file_path}
      
      Evaluate:
      - Algorithm complexity
      - Memory usage patterns
      - Database query efficiency
      - Caching opportunities
      - Async/await usage
      
      Code: {file_content}
      Changes: {diff_content}
    expected_output: "Performance analysis with optimization suggestions"
```

### Multi-Agent Workflows

Configure multiple agents to work together:

```python
# In code_reviewer.py
def review_with_multiple_agents(self, file_path: str) -> List[Dict]:
    """Use multiple specialized agents for comprehensive review."""
    agents = [
        create_agent_from_config('senior_reviewer', self.bedrock_client),
        create_agent_from_config('security_reviewer', self.bedrock_client),
        create_agent_from_config('performance_reviewer', self.bedrock_client)
    ]
    
    tasks = []
    for agent in agents:
        task = create_task_from_config('code_review', agent, context)
        tasks.append(task)
    
    crew = Crew(agents=agents, tasks=tasks)
    return crew.kickoff()
```

## Configuration Validation

The application validates configuration files on startup. Common validation errors:

- **Missing required fields**: Ensure all agent properties are defined
- **Invalid YAML syntax**: Check indentation and formatting
- **Template variable mismatches**: Verify template variables match context keys
- **Invalid severity levels**: Use only defined severity levels
