# AWS Serverless Crypto Data Platform
# Executive Summary

This project implements a serverless, end-to-end crypto trade analytics platform on AWS, ingesting live market data from Coinbase, transforming it using PySpark (AWS Glue), and enabling SQL analytics via Athena.

It follows a modern Bronze → Silver → Gold lakehouse architecture and includes CI/CD automation for Lambda deployment, secure IAM design, and cost governance controls.

# Architecture
High-Level Architecture

<img width="1536" height="1024" alt="ChatGPT Image Feb 12, 2026, 03_27_06 PM" src="https://github.com/user-attachments/assets/391f2787-c8f4-46c9-8f4b-314e91844458" />


# Logical Flow
<img width="402" height="330" alt="image" src="https://github.com/user-attachments/assets/399e00f3-b691-4333-9344-d116ebd99ac2" />

# CI/CD Flow
<img width="317" height="186" alt="549079720-ff987b9b-98a7-43c4-a6b2-34d45037c5e5" src="https://github.com/user-attachments/assets/2af34e3a-a6f6-46fa-b7dd-fed1dd9f2772" />

# Data Pipeline Design
## 1. Ingestion Layer (Serverless)

AWS Lambda polls Coinbase REST API (near-real-time ingestion)

Writes immutable raw events to S3 Bronze

Partitioned by:

source=coinbase/product=BTC-USD/date=YYYY-MM-DD

Why REST Polling?

Lambda does not support long-lived WebSocket connections reliably.
REST polling ensures:

Stateless execution

Cost predictability

Operational simplicity

## 2. Silver Layer (Data Normalization)

Implemented using AWS Glue (PySpark):

Cast numeric fields (price, size)

Parse timestamps

Remove duplicates

Write columnar Parquet

Partition by product_id

Silver guarantees:

Typed schema

Cleaned records

Query efficiency

## 3. Gold Layer (Business Aggregations)

Aggregations performed:

Trade count per hour

Average price per hour

Total traded volume per hour

This layer represents:

Analytics-ready, business-consumable data.

## 4. Analytics Layer

Athena external table over Gold Parquet

Partition discovery using MSCK REPAIR TABLE

SQL-based analytics on S3 without a data warehouse

# IAM & Security Model

The project implements role separation:

Component	Permission Scope
Lambda Role	Write to Bronze only
Glue Role	Read Bronze, write Silver/Gold
CI/CD User	Update Lambda + upload Glue script only

## This demonstrates:

Least privilege enforcement

Scoped resource ARNs

Region-specific access control

# CI/CD Implementation

Deployment is automated using GitHub Actions:

On every push to main:

Lambda package is created

aws lambda update-function-code is executed

Glue ETL script is synced to S3

Manual console edits are eliminated.

## This ensures:

Reproducibility

Deployment consistency

Infrastructure discipline

# Cost Governance Strategy

Cost control is intentionally designed:

EventBridge disabled when not ingesting

Parquet format reduces Athena scan size

Partition pruning minimizes query cost

Glue jobs run on-demand (no continuous DPU usage)

No persistent compute clusters

Athena cost model:

Billed per TB scanned — minimized via Parquet + partitioning.

# Repository Structure

<img width="552" height="152" alt="549081916-9488a53a-93ea-45ae-9dc5-0742f3d13835" src="https://github.com/user-attachments/assets/2476a67d-987f-4cea-bcd6-e76a03a3ce41" />


# Design Principles Demonstrated

Serverless ingestion

Lakehouse architecture

PySpark ETL modeling

IAM debugging and scoping

Region-aware AWS operations

CI/CD automation

Cost-aware data engineering

# Current Capabilities

 Live ingestion from Coinbase
 Bronze/Silver/Gold lake layers
 Parquet-based analytics
 Athena SQL queries
 Automated Lambda deployment via CI/CD
 IAM least-privilege enforcement

# Future Enhancements

Incremental Glue processing (bookmarks)

Infrastructure as Code (Terraform)

Multi-product ingestion (ETH-USD)

Automated Glue job trigger in CI

Data quality validation layer
