import sys
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType
from awsglue.context import GlueContext
from awsglue.job import Job

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

bronze_path = "s3://coinbase-data-lake-ss-2026/bronze/"
silver_path = "s3://coinbase-data-lake-ss-2026/silver/"
gold_path = "s3://coinbase-data-lake-ss-2026/gold/"

df = spark.read.json(bronze_path)

silver_df = (
    df
    .withColumn("price", F.col("price").cast(DoubleType()))
    .withColumn("size", F.col("size").cast(DoubleType()))
    .withColumn("event_time", F.to_timestamp("event_time"))
    .withColumn("ingestion_time", F.to_timestamp("ingestion_time"))
    .dropDuplicates(["product_id", "event_time", "price", "size"])
)

(
    silver_df
    .write
    .mode("overwrite")
    .partitionBy("product_id")
    .parquet(silver_path)
)

gold_df = (
    silver_df
    .withColumn("event_hour", F.date_trunc("hour", "event_time"))
    .groupBy("product_id", "event_hour")
    .agg(
        F.count("*").alias("trade_count"),
        F.avg("price").alias("avg_price"),
        F.sum("size").alias("total_volume")
    )
)

(
    gold_df
    .write
    .mode("overwrite")
    .partitionBy("product_id")
    .parquet(gold_path)
)

job.commit()
