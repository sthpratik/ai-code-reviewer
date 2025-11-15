#!/bin/bash

# Build script for ai-code-reviewer package

set -e

echo "🏗️  Building ai-code-reviewer package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade build twine

# Build the package
echo "🔨 Building package..."
python -m build

# Check the package
echo "🔍 Checking package..."
twine check dist/*

echo "✅ Package built successfully!"
echo "📁 Files created:"
ls -la dist/

echo ""
echo "🚀 To install locally:"
echo "   pip install dist/ai_code_reviewer-*.whl"
echo ""
echo "📤 To upload to PyPI:"
echo "   twine upload dist/*"
echo ""
echo "🧪 To test install:"
echo "   pip install --index-url https://test.pypi.org/simple/ ai-code-reviewer"
