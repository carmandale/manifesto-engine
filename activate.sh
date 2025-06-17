#!/bin/bash
source .venv/bin/activate
echo "✅ Manifesto environment activated"
echo "📍 Location: $VIRTUAL_ENV"
echo "🐍 Python: $(python --version)"

# Check if dependencies are installed
if ! python -c "import click" 2>/dev/null; then
    echo "⚠️  Dependencies not installed. Run: uv pip install -r requirements.txt"
fi
alias manifesto="python manifesto"
