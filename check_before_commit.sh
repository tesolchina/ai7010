#!/bin/bash
# Security check before git commit
# Ensures APIkey.md is not accidentally staged

echo "🔍 Checking for API key security..."
echo ""

# Check if APIkey.md exists
if [ -f "APIkey.md" ]; then
    echo "✓ APIkey.md exists"
else
    echo "⚠️  Warning: APIkey.md not found"
fi

# Check if .gitignore has APIkey.md
if grep -q "APIkey.md" .gitignore 2>/dev/null; then
    echo "✓ APIkey.md is in .gitignore"
else
    echo "❌ ERROR: APIkey.md is NOT in .gitignore!"
    exit 1
fi

# Check if APIkey.md is staged
if git ls-files --error-unmatch APIkey.md 2>/dev/null; then
    echo "❌ ERROR: APIkey.md is tracked by git!"
    echo "   Run: git rm --cached APIkey.md"
    exit 1
else
    echo "✓ APIkey.md is not tracked by git"
fi

# Check for hardcoded keys in Python files
if grep -r "sk-or-v1-[a-zA-Z0-9]\\{50,\\}" --include="*.py" . 2>/dev/null | grep -v "api_key_loader.py" | grep -v "#"; then
    echo "❌ ERROR: Found hardcoded API keys in Python files!"
    exit 1
else
    echo "✓ No hardcoded API keys in Python files"
fi

echo ""
echo "✅ Security check passed! Safe to commit."
echo ""
echo "Git status:"
git status --short

