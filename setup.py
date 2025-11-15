#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-code-reviewer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered code review agent using AWS Bedrock and Bitbucket integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/sthpratik/ai-code-reviewer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ai-code-reviewer=ai_code_reviewer.cli:main",
            "acr=ai_code_reviewer.cli:main",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "ai_code_reviewer": [
            "config/*.yaml",
            "static/*",
            "templates/*",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "server": [
            "uvicorn>=0.15.0",
            "gunicorn>=20.0.0",
        ],
    },
    keywords="code-review ai aws-bedrock bitbucket automation quality-assurance",
    project_urls={
        "Bug Reports": "https://github.com/sthpratik/ai-code-reviewer/issues",
        "Source": "https://github.com/sthpratik/ai-code-reviewer",
        "Documentation": "https://github.com/sthpratik/ai-code-reviewer/docs",
    },
)
