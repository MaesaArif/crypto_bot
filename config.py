import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_ADMIN_ROLE = os.getenv("DISCORD_ADMIN_ROLE", "admin")

# GCP Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")

# BigQuery Configuration
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "crypto_bot")
BQ_MARKET_TABLE = os.getenv("BQ_MARKET_TABLE", "market_data")
BQ_COMMUNITY_TABLE = os.getenv("BQ_COMMUNITY_TABLE", "community_data")
BQ_DEVELOPER_TABLE = os.getenv("BQ_DEVELOPER_TABLE", "developer_data")

# CoinGecko API
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

# GCS Configuration
GCS_BUCKET = os.getenv("GCS_BUCKET", "crypto_bot_staging")
