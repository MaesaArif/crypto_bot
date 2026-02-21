#!/bin/bash
cd "$(dirname "$0")"
echo "Running from: $(pwd)"

source .venv/bin/activate

python3 daily_price_task.py --batch 7PM

deactivate