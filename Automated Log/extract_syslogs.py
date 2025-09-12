import os
import time
from datetime import datetime, timedelta, timezone
from elasticsearch import Elasticsearch
import json
import sys
from dotenv import load_dotenv  # Import dotenv to load environment variables
from upload_to_gdrive import upload_json_logs, create_folder, get_main_folder_id

# Load environment variables from .env file
load_dotenv()

LOCAL_OFFSET = 6  

def get_env_or_fail(var):
    value = os.environ.get(var)
    if value is None:
        print(f"Environment variable '{var}' is required but not set.")
        sys.exit(1)
    return value

def get_elasticsearch_client(host, port):
    username = get_env_or_fail("ELASTIC_USERNAME")
    password = get_env_or_fail("ELASTIC_PASSWORD")
    es = Elasticsearch(
        [{'host': host, 'port': port, 'scheme': 'http'}],
        basic_auth=(username, password)
    )
    if not es.ping():
        raise ConnectionError("Failed to connect to Elasticsearch")
    return es

def query_and_save_logs(es, index_pattern, start_time, end_time, folder_id, filename):
    """Fetch all logs in the given time range and upload directly to Google Drive."""
    print(f"Querying logs from {start_time.isoformat()} to {end_time.isoformat()}")
    query = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start_time.isoformat(),
                                "lte": end_time.isoformat()
                            }
                        }
                    }
                ]
            }
        }
    }

    try:
        logs_data = []
        page = es.search(
            index=index_pattern,
            body=query,
            scroll="2m",
            size=5000
        )

        sid = page["_scroll_id"]
        hits = page["hits"]["hits"]

        total_logs = 0

        while hits:
            for hit in hits:
                logs_data.append(hit["_source"])
                total_logs += 1

            page = es.scroll(scroll_id=sid, scroll="2m")
            sid = page["_scroll_id"]
            hits = page["hits"]["hits"]

        es.clear_scroll(scroll_id=sid)

        # Upload logs directly to Google Drive
        upload_json_logs(logs_data, folder_id, filename)
        print(f"Uploaded {total_logs} logs to Google Drive: {filename}")

    except Exception as e:
        print(f"Error fetching logs: {e}")

def main():

    es_host = get_env_or_fail("ELASTIC_HOST")
    es_port = int(get_env_or_fail("ELASTIC_PORT"))
    index_pattern = get_env_or_fail("ELASTIC_INDEX_PATTERN")
    interval_minutes = int(get_env_or_fail("SYSLOGS_INTERVAL_MINUTES"))

    es = get_elasticsearch_client(es_host, es_port)

    if len(sys.argv) > 2:
        folder_id = sys.argv[1]  # Now receiving folder_id instead of output_folder
        timestamp = sys.argv[2]
        print(f"log script time: {timestamp}")

        interval_start_local = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")

        interval_start = interval_start_local - timedelta(hours=LOCAL_OFFSET)
        interval_end = interval_start + timedelta(minutes=interval_minutes)

        print(f"Extracting logs from {interval_start} to {interval_end}")

        filename = f"syslogs_{timestamp}.json"
        query_and_save_logs(es, index_pattern, interval_start, interval_end, folder_id, filename)
    else:
        current_time = datetime.utcnow()
        interval_start = current_time - timedelta(seconds=current_time.second, microseconds=current_time.microsecond)
        interval_start -= timedelta(minutes=interval_start.minute % interval_minutes)
        interval_end = interval_start + timedelta(minutes=interval_minutes)
        timestamp = interval_start.strftime("%Y%m%d_%H%M%S")
        
        # Create main folder and timestamp subfolder
        main_folder_id = get_main_folder_id()
        timestamp_folder_id = create_folder(timestamp, main_folder_id)
        filename = f"syslogs_{timestamp}.json"
        query_and_save_logs(es, index_pattern, interval_start, interval_end, timestamp_folder_id, filename)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Log extraction stopped by user")