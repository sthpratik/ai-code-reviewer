# Installation Guide

## Install as Global Package

### From PyPI (Recommended)
```bash
# Install globally
pip install ai-code-reviewer

# Or install with server capabilities
pip install ai-code-reviewer[server]

# Or install development version
pip install ai-code-reviewer[dev]
```

### From Source
```bash
# Clone repository
git clone https://github.com/sthpratik/ai-code-reviewer.git
cd ai-code-reviewer

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Using pipx (Isolated Installation)
```bash
# Install with pipx for isolated environment
pipx install ai-code-reviewer

# Install with extras
pipx install ai-code-reviewer[server]
```

## Global Usage

Once installed globally, you can use the tool from any directory:

### Basic Commands
```bash
# Show help
ai-code-reviewer --help

# Show version
ai-code-reviewer version

# Review local changes
ai-code-reviewer local --base develop

# Review PR (with environment variables set)
ai-code-reviewer pr --pr-id 120

# Review PR (with explicit parameters)
ai-code-reviewer pr --workspace TEAM --repo PROJECT --pr-id 120

# Start web server
ai-code-reviewer server --port 8080
```

### Short Alias
The package also installs a short alias `acr`:

```bash
# Same functionality with shorter command
acr local --base main
acr pr --pr-id 120
acr server
```

## Configuration

### Global Configuration
Create a global configuration directory:

```bash
# Create global config directory
mkdir -p ~/.config/ai-code-reviewer

# Copy default configuration
cp config/review_standards.yaml ~/.config/ai-code-reviewer/

# Set environment variables globally
echo 'export BITBUCKET_WORKSPACE=your_workspace' >> ~/.bashrc
echo 'export BITBUCKET_REPO=your_default_repo' >> ~/.bashrc
echo 'export BITBUCKET_TOKEN=your_token' >> ~/.bashrc
```

### Project-Specific Configuration
For project-specific settings, create `.env` file in your project root:

```bash
# In your project directory
cat > .env << 'EOF'
BITBUCKET_WORKSPACE=project_workspace
BITBUCKET_REPO=project_repo
BITBUCKET_TOKEN=your_token
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
EOF
```

### Custom Guidelines
Create project-specific coding standards:

```bash
# In your project directory
mkdir -p .amazonq/rules
cat > .amazonq/rules/coding-standards.md << 'EOF'
# Project Coding Standards

## Python Guidelines
- Use type hints for all functions
- Follow PEP 8 conventions
- Maximum line length: 88 characters

## Security Requirements
- Never commit secrets or API keys
- Validate all external inputs
- Use HTTPS for all API calls
EOF
```

## Verification

Test the installation:

```bash
# Check installation
ai-code-reviewer version

# Test with help
ai-code-reviewer --help

# Test local review (in a git repository)
cd /path/to/your/git/repo
ai-code-reviewer local --base main
```

## Uninstallation

```bash
# Uninstall package
pip uninstall ai-code-reviewer

# Or with pipx
pipx uninstall ai-code-reviewer
```

## Troubleshooting

### Command Not Found
If `ai-code-reviewer` command is not found after installation:

```bash
# Check if pip bin directory is in PATH
python -m pip show -f ai-code-reviewer

# Add pip bin directory to PATH
export PATH="$PATH:$(python -m site --user-base)/bin"

# Or use python -m to run
python -m ai_code_reviewer.cli --help
```

### Permission Issues
If you get permission errors during installation:

```bash
# Install for current user only
pip install --user ai-code-reviewer

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install ai-code-reviewer
```

### Dependencies Issues
If you encounter dependency conflicts:

```bash
# Create isolated environment with pipx
pipx install ai-code-reviewer

# Or use conda
conda create -n ai-code-reviewer python=3.9
conda activate ai-code-reviewer
pip install ai-code-reviewer
```
