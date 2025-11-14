# AI Code Review Agent

A CrewAI-powered code review agent that uses AWS Bedrock (Claude 3.5 Sonnet) to perform intelligent code reviews.

## Features

- **Local Review**: Review code changes locally without posting comments
- **Bitbucket Integration**: Review pull requests directly from server and add comments automatically
- **Web API Interface**: REST API and web UI for easy integration
- **Docker Support**: Containerized deployment with docker-compose
- **Configurable Standards**: Customizable code review criteria via YAML
- **Senior Engineer Perspective**: Reviews focus on scalability, performance, and quality
- **KISS Principle**: Simple, modular design with separate concerns

## Quick Start with Docker

1. **Clone and configure:**
   ```bash
   git clone <repository-url>
   cd codeReviewAgent
   cp .env.template .env
   # Edit .env with your credentials
   ```

2. **Start the application:**
   ```bash
   ./start.sh
   ```

3. **Access the web interface:**
   - Web UI: http://localhost
   - API docs: http://localhost/docs
   - Health check: http://localhost/health

## Manual Setup

1. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.template .env
# Edit .env with your credentials
```

3. Configure AWS credentials for Bedrock access

## Usage

### Simple CLI (Recommended)

**Review local changes:**
```bash
./review local                    # Compare with develop branch
./review local --base main       # Compare with main branch
```

**Review Bitbucket PR:**
```bash
./review pr --workspace CTAPPS --repo imageresizer --pr-id 120
```

### Web Interface

Access the web interface at `http://localhost` to:
- Submit local code reviews
- Review Bitbucket pull requests
- View review results in real-time

### REST API

#### Local Code Review
```bash
curl -X POST http://localhost/review/local \
  -H "Content-Type: application/json" \
  -d '{"base_branch": "develop"}'
```

#### Bitbucket Pull Request Review
```bash
curl -X POST http://localhost/review/bitbucket \
  -H "Content-Type: application/json" \
  -d '{
    "workspace": "CTAPPS",
    "repo": "imageresizer",
    "pr_id": "120"
  }'
```

### Advanced CLI Interface

#### Local Code Review
```bash
python main.py --mode local --base-branch develop
```

#### Bitbucket Pull Request Review
```bash
python main.py --mode bitbucket --workspace CTAPPS --repo imageresizer --pr-id 120
```

### Custom Configuration
```bash
python main.py --config custom_standards.yaml --base-branch main
```

## Two Review Modes

### Local Mode
- **What it does**: Compares your current working directory with a base branch
- **Use case**: Review your changes before committing/pushing
- **Requirements**: Must be in a git repository with changes
- **Command**: `./review local --base develop`

### PR Mode  
- **What it does**: Fetches PR changes directly from Bitbucket Server
- **Use case**: Review any PR without checking out code locally
- **Requirements**: Valid Bitbucket credentials and PR access
- **Command**: `./review pr --workspace PROJECT --repo REPO --pr-id ID`

## Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## Configuration

### Environment Variables (.env)
```bash
# Bitbucket Server Configuration
BITBUCKET_URL=https://git.cnvrmedia.net/rest/api/1.0
BITBUCKET_TOKEN=your_server_token_here

# AWS Configuration (for Bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Optional: Custom model
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

### Review Standards
Edit `config/review_standards.yaml` to customize review criteria:

- **Performance**: Loop efficiency, memory usage, caching
- **Scalability**: Modularity, error handling, async patterns
- **Code Quality**: Naming, DRY principle, complexity
- **Readability**: Comments, formatting, organization
- **Security**: Input validation, authentication, data handling

## Architecture

- `utils/`: Git, Bitbucket, and Bedrock utilities
- `agents/`: CrewAI agent definitions (YAML-configured)
- `tasks/`: CrewAI task definitions (YAML-configured)
- `config/`: Review standards and agent configurations
- `static/`: Web interface files
- `code_reviewer.py`: Main orchestrator
- `api_server.py`: FastAPI web server
- `main.py`: Advanced CLI interface
- `review`: Simple CLI script

## Bitbucket Server vs Cloud

This application is configured for **Bitbucket Server** (on-premises). Key differences:

| Feature | Server (1.0 API) | Cloud (2.0 API) |
|---------|------------------|------------------|
| URL | `https://your-server.com/rest/api/1.0` | `https://api.bitbucket.org/2.0` |
| Projects | `/projects/{PROJECT}/repos/{REPO}` | `/repositories/{workspace}/{repo}` |
| Auth | Bearer token | OAuth/App passwords |

## Troubleshooting

### Common Issues

**401 Unauthorized**: Check your Bitbucket token permissions
```bash
python test_token.py  # Test token validity
```

**No files found**: 
- Local mode: Ensure you have git changes (`git status`)
- PR mode: Verify PR exists and has changes

**Connection errors**: Check your Bitbucket URL and network access

### Debug Commands
```bash
python test_token.py                              # Test Bitbucket access
python debug_pr.py CTAPPS imageresizer 120      # Debug specific PR
python test_pr_diff.py CTAPPS imageresizer 120  # Test PR diff fetch
```

## API Documentation

See [API Examples](api_examples.md) for detailed usage examples.

Interactive API documentation available at: http://localhost/docs
