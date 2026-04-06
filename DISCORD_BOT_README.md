# Discord Bot

A Discord bot that queries cryptocurrency data from Google Cloud BigQuery.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your:
- **DISCORD_BOT_TOKEN**: Get from [Discord Developer Portal](https://discord.com/developers/applications)
- **GCP_CREDENTIALS_PATH**: Path to your GCP service account JSON file
- **GCP_PROJECT_ID**: Your GCP project ID
- **BQ_DATASET_ID**: Your BigQuery dataset ID (default: `crypto_bot`)

### 3. Run the Bot

```bash
python discord_bot.py
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!ping` | Check if bot is responsive | `!ping` |
| `!crypto <id>` | Get latest price data for a cryptocurrency | `!crypto bitcoin` |
| `!community <id>` | Get community stats for a cryptocurrency | `!community ethereum` |
| `!developer <id>` | Get developer activity for a cryptocurrency | `!developer dogecoin` |
| `!list` | List all available cryptocurrencies | `!list` |
| `!query <sql>` | Run custom SQL query (admin only) | `!query SELECT * FROM crypto_bot.market_data LIMIT 5` |

## BigQuery Table Schema

The bot expects the following tables in your BigQuery dataset:

### market_data
- `timestamp`, `batch_id`, `crypto_id`, `currency`, `current_price`, `market_cap`, `total_volume`

### community_data
- `timestamp`, `batch_id`, `crypto_id`, `facebook_likes`, `reddit_average_posts_48h`, `reddit_average_comments_48h`, `reddit_subscribers`, `reddit_accounts_active_48h`

### developer_data
- `timestamp`, `batch_id`, `crypto_id`, `forks`, `stars`, `subscribers`, `total_issues`, `closed_issues`, `pull_requests_merged`, `pull_request_contributors`, `code_additions_deletions_4_weeks`, `commit_count_4_weeks`
