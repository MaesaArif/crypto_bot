#!/bin/bash

source .venv/bin/activate

python3 daily_price_task.py --batch 7PM

deactivate