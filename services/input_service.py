"""
Input Service - Backend logic for file upload and data import operations
"""
import pandas as pd
import tempfile
import os
from utils.sqlite_storage import (
    get_all_accounts, get_input_mappings, save_input_mappings, save_transactions
)
from utils.minio_storage import upload_file
from utils.output_log import logger


class InputService:
    """Service class for handling data input and file processing operations"""
    
    @staticmethod
    def get_accounts() -> list:
        """Get all available accounts"""
        return get_all_accounts()
    
    @staticmethod
    def process_csv_upload(uploaded_file, account: str) -> pd.DataFrame:
        """Process uploaded CSV file and return dataframe"""
        df = pd.read_csv(uploaded_file)
        logger.debug(f"CSV uploaded with {len(df)} rows for account: {account}")
        return df
    
    @staticmethod
    def get_saved_mappings(account: str) -> dict:
        """Get saved field mappings for an account"""
        return get_input_mappings(account)
    
    @staticmethod
    def save_mappings_and_import(account: str, mappings: dict, uploaded_file, username: str):
        """Save field mappings and import transaction data"""
        # Save mappings
        save_input_mappings(account, mappings)
        
        # Save file to minio
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            temp_file.write(uploaded_file.getvalue())
            temp_file.flush()
            
            minio_path = f"uploads/{username}/{uploaded_file.name}"
            upload_file(temp_file.name, minio_path)
            logger.debug(f"File uploaded to minio: {minio_path}")
            
            # Process and save transactions
            uploaded_file.seek(0)  # Reset file pointer again
            df = pd.read_csv(uploaded_file)
            processed_data = InputService._process_mappings(df, mappings, account, username)
            save_transactions(username, account, processed_data, mappings)
            
            return len(processed_data)
        finally:
            os.unlink(temp_file.name)
    
    def transaction_amount_conversion(amount, currency):
        from currency_converter import CurrencyConverter
        debit_credit = 1
        if amount[0] == '-':
            debit_credit = -1
            amount = amount[1:]
        if amount[0] in ['$', '€', '£', '¥']:
            amount = amount[1:]
        try:
            amount = float(amount)
        except ValueError:
            logger.error(f"Invalid amount format: {amount}")
            return 0.0
        if currency != 'CAD':
            amount = CurrencyConverter().convert(amount, currency, 'CAD')
        return amount * debit_credit


    @staticmethod
    def _process_mappings(df: pd.DataFrame, mappings: dict, account: str, username: str) -> list:
        """Process field mappings and prepare data for saving"""
        processed = []
        for _, row in df.iterrows():
            transaction = {'account': account, 'username': username}
            for field, source in mappings.items():
                if ';' in source:
                    # Multiple columns selected - join their values
                    columns = source.split(';')
                    values = []
                    for col in columns:
                        if col in df.columns:
                            value = str(row[col]) if pd.notna(row[col]) else ''
                            logger.debug(f"Processing field '{field}' with value '{value}' from column '{col}'")
                            if value:
                                values.append(value)
                    logger.debug(f"Field '{field}' combined values: {values}")
                    transaction[field] = ';'.join(values)
                elif field == 'amount':
                    amount = str(row.get(source, '0'))
                    currency = row.get('currency', 'CAD')
                    transaction[field] = InputService.transaction_amount_conversion(amount, currency)
                elif source in df.columns:
                    # Single column selected
                    transaction[field] = row[source]
                else:
                    # Manual/fixed value
                    transaction[field] = source
            processed.append(transaction)
        return pd.DataFrame(processed)
