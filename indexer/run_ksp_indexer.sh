#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "📦 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "📥 Installing dependencies..."
"$VENV_DIR/bin/python" -m pip install -r "$PROJECT_ROOT/requirements.txt"

echo "🚀 Running index_documents.py..."
"$VENV_DIR/bin/python" "$SCRIPT_DIR/index_documents.py"

deactivate
