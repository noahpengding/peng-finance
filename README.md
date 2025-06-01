# Peng Finance

A Python application for personal finance management.

## Features

- Financial reporting
- User management
- Data import and mapping
- Category management

## Setup

```bash
# Create and activate virtual environment using uv
uv install
uv run bash  # to enter the virtual environment shell (optional)

# Set environment variables
export MINIO_ENDPOINT=...
export MINIO_ACCESS_KEY=...
export MINIO_SECRET_KEY=...
export DB_S3_PATH=finance.db
export LOCAL_DB_PATH=data/finance.db
export JWT_SECRET=...
export ADMIN_PASSWORD=...

# Run the app
uv run streamlit run app.py
```
