main.py 

Functions:

- initialize discord client
- load config
- register scheduled jobs
- start the bot


config.py

Functions:

- load env variables
- centralize config values


.env

Functions:

- DISCORD_TOKEN
    
- CHANNEL_ID
    
- CRYPTO_IDS (comma-separated)
    
- POST_TIME_UTC
    
- GCP_PROJECT_ID
    
- BQ_DATASET
    
- BQ_TABLE
    
- GOOGLE_APPLICATION_CREDENTIALS


crypto_service.py

Function: 

- fetch prices from CoinGecko
- normalize API responses
- return structured price records


bigquery_repo.py

Function:
- init BQ client
- batch insert daily price records
-enforce idempotency using date and coin_id
- query data


daily_price_task.py

Function 

- orchestrate daily scheduled workflow 
- fetch prices 
- enrich with timestamps


formatter.py

Function: 

- conveet database records into readable discord messages
- handle formatting, currency, and emojis
- support future comparison and summaries