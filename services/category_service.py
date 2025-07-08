"""
Category Service - Backend logic for category operations
"""
import pandas as pd
from utils.sqlite_storage import get_session, save_category_mapping, get_category_mappings_list, Detail
from utils.output_log import logger


class CategoryService:
    """Service class for handling category-related operations"""
    
    @staticmethod
    def get_unmapped_transactions(username: str) -> pd.DataFrame:
        """Get transactions that don't have categories assigned"""
        session = get_session()
        try:
            rows = session.query(
                Detail.id, Detail.original_category, Detail.merchant_name, Detail.description
            ).filter(
                Detail.username == username,
                (Detail.category == '')
            ).all()
            
            return pd.DataFrame(rows, columns=['id', 'original_category', 'merchant_name', 'description'])
        finally:
            session.close()
    
    @staticmethod
    def get_existing_categories() -> list:
        """Get list of existing categories"""
        mappings = get_category_mappings_list()
        categories = list({row.target_category for row in mappings if row.target_category})
        categories.sort()
        return categories
    
    @staticmethod
    def save_transaction_category(original_category: str, merchant_name: str, 
                                description: str, target_category: str):
        """Save category mapping for a transaction"""
        logger.debug(f"Saving category mapping: {original_category} -> {target_category}")
        save_category_mapping(original_category, merchant_name, description, target_category)
