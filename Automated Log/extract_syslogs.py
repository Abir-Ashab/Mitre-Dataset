import os
import time
from datetime import datetime, timedelta, timezone
from elasticsearch import Elasticsearch
import json
import sys
from dotenv import load_dotenv  # Import dotenv to load environment variables

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

def query_and_save_logs(es, index_pattern, start_time, end_time, output_file):
    """Fetch all logs in the given time range and write directly to file."""
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

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        with open(output_file, 'w') as f:
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
                    json.dump(hit["_source"], f)
                    f.write("\n")
                    total_logs += 1

                page = es.scroll(scroll_id=sid, scroll="2m")
                sid = page["_scroll_id"]
                hits = page["hits"]["hits"]

            es.clear_scroll(scroll_id=sid)

        print(f"Saved {total_logs} logs to: {output_file}")

    except Exception as e:
        print(f"Error fetching logs: {e}")

def main():

    es_host = get_env_or_fail("ELASTIC_HOST")
    es_port = int(get_env_or_fail("ELASTIC_PORT"))
    index_pattern = get_env_or_fail("ELASTIC_INDEX_PATTERN")
    interval_minutes = int(get_env_or_fail("SYSLOGS_INTERVAL_MINUTES"))

    es = get_elasticsearch_client(es_host, es_port)

    if len(sys.argv) > 2:
        output_folder = sys.argv[1]
        timestamp = sys.argv[2]
        print(f"log script time: {timestamp}")

        interval_start_local = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")

        interval_start = interval_start_local - timedelta(hours=LOCAL_OFFSET)
        interval_end = interval_start + timedelta(minutes=interval_minutes)

        print(f"Extracting logs from {interval_start} to {interval_end}")

        output_file = os.path.join(output_folder, f"syslogs_{timestamp}.json")
        query_and_save_logs(es, index_pattern, interval_start, interval_end, output_file)
    else:
        current_time = datetime.utcnow()
        interval_start = current_time - timedelta(seconds=current_time.second, microseconds=current_time.microsecond)
        interval_start -= timedelta(minutes=interval_start.minute % interval_minutes)
        interval_end = interval_start + timedelta(minutes=interval_minutes)
        timestamp = interval_start.strftime("%Y%m%d_%H%M%S")
        base_output_dir = get_env_or_fail("BASE_OUTPUT_DIR")
        output_file = os.path.join(base_output_dir, f"syslogs_{timestamp}.json")
        query_and_save_logs(es, index_pattern, interval_start, interval_end, output_file)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Log extraction stopped by user")