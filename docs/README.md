# AI Code Review Agent

> A CrewAI-powered code review agent that uses AWS Bedrock (Claude 3.5 Sonnet) to perform intelligent code reviews.

## Overview

The AI Code Review Agent is designed to help development teams maintain high code quality by providing automated, intelligent code reviews. It acts like a senior software engineer, analyzing code changes for:

- **Performance** - Loop efficiency, memory usage, caching strategies
- **Scalability** - Modularity, error handling, async patterns  
- **Code Quality** - Naming conventions, DRY principle, complexity
- **Readability** - Comments, formatting, organization
- **Security** - Input validation, authentication, data handling

## Key Features

✅ **Local Review Mode** - Review code changes locally without posting comments  
✅ **Bitbucket Integration** - Automatically review pull requests and add comments  
✅ **Configurable Standards** - Customize review criteria via YAML configuration  
✅ **Senior Engineer Perspective** - AI agent trained to think like an experienced developer  
✅ **KISS Principle** - Simple, modular design with clear separation of concerns  

## Architecture

```
codeReviewAgent/
├── agents/           # CrewAI agent definitions
├── config/           # YAML configurations
├── docs/             # Documentation
├── tasks/            # CrewAI task definitions
├── utils/            # Utility modules
├── code_reviewer.py  # Main orchestrator
└── main.py          # CLI interface
```

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your credentials
   ```

3. **Run local review**
   ```bash
   python main.py --mode local --base-branch develop
   ```

## Next Steps

- [Installation Guide](installation.md) - Detailed setup instructions
- [Configuration](configuration.md) - Customize review standards and agents
- [Bitbucket Integration](bitbucket.md) - Set up PR reviews with Bamboo/Bitbucket
- [Usage Examples](usage.md) - Common use cases and commands
