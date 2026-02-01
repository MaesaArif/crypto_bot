#!/usr/bin/env bash
set -e  # Exit immediately if a command fails

VENV_DIR=".venv"
GITIGNORE=".gitignore"

# Ensure we’re in the script’s directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🐍 Creating virtual environment if it doesn't exist..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
else
    echo "ℹ️ Virtual environment already exists"
fi

echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing dependencies from requirements.txt..."
# pip is smart: it skips what's already installed and ignores standard libs
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found, skipping installation."
fi

# Add venv to .gitignore logic
if [ ! -f "$GITIGNORE" ] || ! grep -qx "$VENV_DIR/" "$GITIGNORE"; then
    echo -e "\n# Python virtual environment\n$VENV_DIR/" >> "$GITIGNORE"
    echo "➕ Added $VENV_DIR/ to .gitignore"
else
    echo "ℹ️ $VENV_DIR/ already in .gitignore"
fi

echo "✅ Setup complete!"
echo "👉 Activate with: source $VENV_DIR/bin/activate"