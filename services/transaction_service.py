"""
Transaction Service - Backend logic for transaction operations
"""
import pandas as pd
from utils.sqlite_storage import get_session, Detail
from utils.output_log import logger


class TransactionService:
    """Service class for handling transaction-related operations"""
    
    @staticmethod
    def get_user_transactions(username: str) -> pd.DataFrame:
        """Get all transactions for a specific user"""
        logger.debug(f"Fetching transactions for user: {username}")
        
        session = get_session()
        try:
            rows = session.query(
                Detail.id, Detail.account, Detail.post_date, Detail.category,
                Detail.merchant_name, Detail.description, Detail.amount
            ).filter(Detail.username == username).all()
            
            df = pd.DataFrame(rows, columns=['id', 'account', 'post_date', 'category', 'merchant_name', 'description', 'amount'])
            logger.debug(f"Fetched Result {df.to_dict(orient='records')}")
            return df
        finally:
            session.close()
    
    @staticmethod
    def get_filter_options(df: pd.DataFrame) -> dict:
        """Get unique values for filtering options"""
        return {
            'accounts': df['account'].unique().tolist(),
            'post_dates': df['post_date'].unique().tolist(),
            'categories': df['category'].dropna().unique().tolist(),
            'merchants': df['merchant_name'].unique().tolist()
        }
    
    @staticmethod
    def apply_filters(df: pd.DataFrame, selected_accounts: list, selected_dates: list, selected_categories: list, selected_merchants: list) -> pd.DataFrame:
        """Apply filters to transaction dataframe"""
        logger.debug(f"Applied filters - accounts: {selected_accounts}, post_dates: {selected_dates}, categories: {selected_categories}, merchants: {selected_merchants}")
        
        mask = (
            df['account'].isin(selected_accounts) &
            df['post_date'].isin(selected_dates) &
            df['category'].isin(selected_categories) &
            df['merchant_name'].isin(selected_merchants)
        )
        return df[mask]
