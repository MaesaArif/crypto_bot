#!/bin/bash

cd /Users/appfuxion/repo/crypto/crypto_bot

source .venv/bin/activate

python3 daily_price_task.py --batch 7AM

deactivate