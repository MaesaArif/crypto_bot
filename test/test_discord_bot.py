import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import bigquery


# Add project root to sys.path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

# from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv("secret/.env")


def get_bigquery_client(credentials_path=None):
    """Initialize BigQuery client using service account credentials."""
    # credentials_path = os.getenv("GCP_CREDENTIALS_PATH")
    if credentials_path and os.path.exists(credentials_path):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        return bigquery.Client(credentials=credentials, project=credentials.project_id)
    else:
        return bigquery.Client()


def query_bigquery(client, query: str, limit: int = 10):
    """Execute a BigQuery SQL query and return results."""
    query_with_limit = f"{query}\nLIMIT {limit}"

    try:
        query_job = client.query(query_with_limit)
        results = query_job.result()

        rows = []
        for row in results:
            rows.append(dict(row))

        return rows, None
    except Exception as e:
        return None, str(e)


async def query():
    """Get latest crypto price data from BigQuery."""
    project_id = os.getenv("GCP_PROJECT_ID", "discord-bot-484904")
    dataset_id = os.getenv("BQ_DATASET_ID", "crypto_bot")
    table_name = os.getenv("BQ_MARKET_TABLE", "market_data")

    query = f"""
        SELECT *
        FROM `{project_id}.{dataset_id}.{table_name}`
        WHERE crypto_id = '{crypto_id}'
        ORDER BY timestamp DESC
    """


if __name__ == "__main__":
    client = get_bigquery_client("secret/discord-bot-484904-2dc07a5b046e.json")
    with open(
        "/Users/appfuxion/repo/crypto/crypto_bot/query/Discord Crypto Bot Data Pull v1.sql"
    ) as f:
        loaded_query = f.read()
    # print(loaded_query)

    output = query_bigquery(client, loaded_query, 5)
    print(output)
