from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "peng-finance")
    DB_S3_PATH = os.getenv("DB_S3_PATH")  # path in S3 to sqlite file
    LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH", "data/main.db")
    JWT_SECRET = os.getenv("JWT_SECRET")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ENV = os.getenv("ENV", "development")
