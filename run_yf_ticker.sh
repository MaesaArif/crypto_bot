#!/bin/bash
cd "$(dirname "$0")"
echo "Running from: $(pwd)"

source .venv/bin/activate

# Execute the ticker pull script
python3 crypto_backtesting/yf_ticker.py

deactivate
