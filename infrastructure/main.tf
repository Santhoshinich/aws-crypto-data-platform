terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-2"
}

# -----------------------------
# S3 Data Lake Bucket
# -----------------------------
resource "aws_s3_bucket" "data_lake" {
  bucket = "coinbase-data-lake-ss-2026"
}
resource "aws_s3_bucket_versioning" "data_lake_versioning" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake_encryption" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    bucket_key_enabled = true

    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# -----------------------------
# Lambda Function
# -----------------------------
resource "aws_lambda_function" "coinbase_ingestion" {
  function_name = "coinbase-trade-ingestion"
  role          = "arn:aws:iam::972108900082:role/service-role/coinbase-trade-ingestion-role-1jztd1cr"

  handler = "lambda_function.lambda_handler"
  runtime = "python3.10"

  filename         = "../lambda.zip"
  source_code_hash = filebase64sha256("../lambda.zip")

  lifecycle {
    ignore_changes = [
      filename,
      source_code_hash
    ]
  }
}

