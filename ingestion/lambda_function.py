import json
import boto3
import urllib.request
from datetime import datetime, timezone

S3_BUCKET = "coinbase-data-lake-ss-2026"
PRODUCT_ID = "BTC-USD"
SOURCE = "coinbase"

s3 = boto3.client("s3")

def fetch_trades():
    url = f"https://api.exchange.coinbase.com/products/{PRODUCT_ID}/trades"
    
    headers = {
        "User-Agent": "aws-lambda-data-ingestion",
        "Accept": "application/json"
    }

    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())

def transform(trade):
    return {
        "event_type": trade.get("side"),
        "product_id": trade.get("product_id", PRODUCT_ID),
        "price": float(trade["price"]),
        "size": float(trade["size"]),
        "side": trade["side"],
        "event_time": trade["time"],
        "ingestion_time": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE
    }

def lambda_handler(event, context):
    trades = fetch_trades()
    transformed = [transform(t) for t in trades]

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    s3_key = (
        f"bronze/source=coinbase/"
        f"product={PRODUCT_ID}/"
        f"date={date_str}/"
        f"trades_{timestamp}.json"
    )

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=json.dumps(transformed),
        ContentType="application/json"
    )

    return {
        "statusCode": 200,
        "records_written": len(transformed),
        "s3_key": s3_key
    }
