CREATE EXTERNAL TABLE gold_trades (
  event_hour timestamp,
  trade_count bigint,
  avg_price double,
  total_volume double
)
PARTITIONED BY (product_id string)
STORED AS PARQUET
LOCATION 's3://coinbase-data-lake-ss-2026/gold/';
