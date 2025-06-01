from minio import Minio
from config.configure import Config
from utils.output_log import logger


client = Minio(
    Config.MINIO_ENDPOINT,
    access_key=Config.MINIO_ACCESS_KEY,
    secret_key=Config.MINIO_SECRET_KEY,
    secure=True
)

def download_db():
    try:
        logger.info(f"Downloading DB from {Config.MINIO_BUCKET}:/{Config.DB_S3_PATH} to {Config.LOCAL_DB_PATH}")
        client.fget_object(Config.MINIO_BUCKET, Config.DB_S3_PATH + "/main.db", Config.LOCAL_DB_PATH)
        logger.info("Database downloaded successfully.")
    except Exception as e:
        logger.error(f"Failed to download DB: {e}")


def upload_file(local_path: str, object_name: str):
    try:
        client.fput_object(Config.MINIO_BUCKET, object_name, local_path)
        logger.info(f"Uploaded {local_path} to {Config.MINIO_BUCKET}/{Config.DB_S3_PATH}/{object_name}")
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
