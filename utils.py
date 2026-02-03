from google.cloud import storage
import os


def parse_gcs_uri(uri):
    """
    Parse a GCS URI into bucket name and blob name.

    Args:
        uri (str): GCS URI in format gs://bucket-name/path/to/object

    Returns:
        tuple: (bucket_name, blob_name)
    """
    if not uri.startswith("gs://"):
        raise ValueError("URI must start with 'gs://'")

    # Remove 'gs://' prefix
    path = uri[5:]

    # Split into bucket and blob path
    parts = path.split("/", 1)
    bucket_name = parts[0]
    blob_name = parts[1] if len(parts) > 1 else ""

    return bucket_name, blob_name


def upload_file_to_gcs(local_file_path, gcs_uri, credentials_path=None):
    """
    Upload a local file to Google Cloud Storage.

    Args:
        local_file_path (str): Path to the local file to upload
        gcs_uri (str): Destination GCS URI (e.g., gs://my-bucket/path/to/file.txt)
        credentials_path (str, optional): Path to service account JSON key file

    Returns:
        bool: True if upload successful, False otherwise
    """
    try:
        # Verify local file exists
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")

        # Parse the GCS URI
        bucket_name, blob_name = parse_gcs_uri(gcs_uri)

        if not blob_name:
            raise ValueError("GCS URI must include a blob name (path after bucket)")

        # Initialize the storage client
        if credentials_path:
            client = storage.Client.from_service_account_json(credentials_path)
        else:
            # Uses default credentials (Application Default Credentials)
            client = storage.Client()

        # Get the bucket
        bucket = client.bucket(bucket_name)

        # Create a blob object
        blob = bucket.blob(blob_name)

        # Upload the file
        print(f"Uploading {local_file_path} to {gcs_uri}...")
        blob.upload_from_filename(local_file_path)

        return True

    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return False
