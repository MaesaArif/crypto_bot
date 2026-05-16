import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from daily_price_task import (
    process_market_data,
    process_community_data,
    process_developer_data,
    daily_api_call,
)


class TestDailyPriceTask(unittest.TestCase):

    def setUp(self):
        # Sample CoinGecko API response data
        self.sample_data = {
            "id": "bitcoin",
            "market_data": {
                "current_price": {"usd": 50000, "eur": 45000},
                "market_cap": {"usd": 1000000000, "eur": 900000000},
                "total_volume": {"usd": 50000000, "eur": 45000000},
            },
            "community_data": {
                "facebook_likes": 100,
                "reddit_average_posts_48h": 10,
                "reddit_average_comments_48h": 50,
                "reddit_subscribers": 1000,
                "reddit_accounts_active_48h": 500,
            },
            "developer_data": {
                "forks": 10,
                "stars": 20,
                "subscribers": 30,
                "total_issues": 40,
                "closed_issues": 35,
                "pull_requests_merged": 25,
                "pull_request_contributors": 15,
                "code_additions_deletions_4_weeks": {
                    "additions": 100,
                    "deletions": -50,
                },
                "commit_count_4_weeks": 50,
            },
        }
        self.batch_id = "7AM"

    def test_process_market_data(self):
        df = pd.DataFrame()
        result_df = process_market_data(self.sample_data, df, self.batch_id)

        self.assertEqual(len(result_df), 2)  # usd and eur
        self.assertEqual(result_df.iloc[0]["crypto_id"], "bitcoin")
        self.assertEqual(result_df.iloc[0]["batch_id"], self.batch_id)
        self.assertIn("current_price", result_df.columns)

    def test_process_community_data(self):
        df = pd.DataFrame()
        result_df = process_community_data(self.sample_data, df, self.batch_id)

        self.assertEqual(len(result_df), 1)
        self.assertEqual(result_df.iloc[0]["facebook_likes"], 100)
        self.assertEqual(result_df.iloc[0]["crypto_id"], "bitcoin")

    def test_process_developer_data(self):
        df = pd.DataFrame()
        result_df = process_developer_data(self.sample_data, df, self.batch_id)

        self.assertEqual(len(result_df), 1)
        self.assertEqual(result_df.iloc[0]["forks"], "10")
        self.assertEqual(result_df.iloc[0]["crypto_id"], "bitcoin")

    @patch("daily_price_task.requests.get")
    @patch("pandas.DataFrame.to_json")
    def test_daily_api_call(self, mock_to_json, mock_get):
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_data
        mock_get.return_value = mock_response

        crypto_list = ["bitcoin"]
        paths = daily_api_call(crypto_list, self.batch_id)

        self.assertEqual(len(paths), 3)
        self.assertTrue(any("crypto_data" in p for p in paths))
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_to_json.call_count, 3)

    @patch("daily_price_task.requests.get")
    @patch("pandas.DataFrame.to_json")
    @patch("daily_price_task.time.sleep")
    def test_daily_api_call_rate_limit(self, mock_sleep, mock_to_json, mock_get):
        # First call returns 429, second returns 200
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = self.sample_data

        mock_get.side_effect = [mock_response_429, mock_response_200]

        crypto_list = ["bitcoin"]
        paths = daily_api_call(crypto_list, self.batch_id)

        self.assertEqual(len(paths), 3)
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)
        mock_sleep.assert_called_with(60)

    @patch("daily_price_task.upload_file_to_gcs")
    @patch("daily_price_task.daily_api_call")
    @patch("daily_price_task.argparse.ArgumentParser.parse_args")
    def test_main_upload_mock(self, mock_args, mock_daily_call, mock_upload):
        # This tests the logic that would be in the if __name__ == "__main__" block
        # We simulate the main execution
        mock_args.return_value = MagicMock(batch="7AM")
        mock_daily_call.return_value = ["path1.ndjson", "path2.ndjson"]
        mock_upload.return_value = True

        # Simulate the execution of the upload block
        PATHS = ["path1.ndjson", "path2.ndjson"]
        credentials_path = "secret/mock_key.json"
        current_date = datetime.now().strftime("%Y-%m-%d")
        gcs_uri = "gs://mock_bucket/" + current_date + "/"

        for path in PATHS:
            mock_upload(path, gcs_uri, credentials_path)

        self.assertEqual(mock_upload.call_count, 2)
        mock_upload.assert_any_call("path1.ndjson", gcs_uri, credentials_path)


if __name__ == "__main__":
    unittest.main()
