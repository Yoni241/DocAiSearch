#!/bin/bash

# Exit on any error
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/venv"

# Step 1: Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Step 2: Activate virtual environment
echo "📦 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Step 3: Install dependencies using venv's pip
echo "📥 Installing dependencies..."
"$VENV_DIR/bin/python" -m pip install -r "$PROJECT_ROOT/requirements.txt"

# Step 4: Run the searcher script
echo "🔍 Running search_documents.py..."
"$VENV_DIR/bin/python" "$SCRIPT_DIR/search_documents.py"

# Step 5: Deactivate virtual environment
deactivate
