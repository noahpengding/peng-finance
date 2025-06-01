"""
Category Page - Frontend UI for categorizing transactions
"""
import streamlit as st
from services.category_service import CategoryService
from services.navigation_service import NavigationService
from utils.output_log import logger


def main():
    # Check authentication
    if NavigationService.redirect_to_login_if_not_authenticated():
        st.warning('Please login first.')
        return

    username = st.session_state['username']
    
    st.header('Categorize Transactions')

    # Get unmapped transactions
    df = CategoryService.get_unmapped_transactions(username)

    if df.empty:
        st.success('All transactions are categorized!')
        st.info('No transactions need categorization at this time.')
        return

    st.info(f'Found {len(df)} transactions that need categorization.')

    # Get existing categories
    categories = CategoryService.get_existing_categories()

    # Progress tracking
    if 'categorized_count' not in st.session_state:
        st.session_state['categorized_count'] = 0

    progress_bar = st.progress(0)
    progress_text = st.empty()

    # Category assignment interface
    st.subheader('Assign Categories')
    
    for idx, row in df.iterrows():
        with st.container():
            st.divider()
            
            # Transaction details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Transaction ID:** {row['id']}")
                st.write(f"**Original Category:** {row['original_category']}")
                st.write(f"**Merchant:** {row['merchant_name']}")
                st.write(f"**Description:** {row['description']}")
            
            with col2:
                # Category selection
                options = [''] + categories + ['<New Category>']
                choice = st.selectbox(
                    'Select Category', 
                    options, 
                    key=f"cat_{row['id']}",
                    help="Choose an existing category or create a new one"
                )
                
                if choice == '<New Category>':
                    choice = st.text_input(
                        'Enter new category', 
                        key=f"new_cat_{row['id']}",
                        help="This will create a new category"
                    )
                
                # Save button
                if st.button('Save Category', key=f"save_{row['id']}", type='primary'):
                    if choice and choice != '':
                        try:
                            CategoryService.save_transaction_category(
                                row['original_category'],
                                row['merchant_name'],
                                row['description'],
                                choice
                            )
                            st.success(f'Category "{choice}" saved successfully!')
                            st.session_state['categorized_count'] += 1
                            
                            # Update progress
                            progress = st.session_state['categorized_count'] / len(df)
                            progress_bar.progress(min(progress, 1.0))
                            progress_text.text(f'Progress: {st.session_state["categorized_count"]}/{len(df)} transactions categorized')
                            
                            # Refresh page after a short delay
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f'Error saving category: {str(e)}')
                            logger.error(f"Category save error: {str(e)}")
                    else:
                        st.warning('Please select or enter a category.')

    # Bulk operations section
    if len(df) > 1:
        st.subheader('Bulk Operations')
        with st.expander('Apply category to multiple transactions'):
            bulk_category = st.selectbox('Select category for bulk assignment', [''] + categories + ['<New Category>'], key='bulk_category')
            if bulk_category == '<New Category>':
                bulk_category = st.text_input('Enter new category for bulk assignment', key='bulk_new_category')
            
            selected_transactions = st.multiselect(
                'Select transactions',
                options=df['id'].tolist(),
                format_func=lambda x: f"ID {x}: {df[df['id']==x]['merchant_name'].iloc[0]} - {df[df['id']==x]['description'].iloc[0][:50]}..."
            )
            
            if st.button('Apply to Selected', key='bulk_save') and bulk_category and selected_transactions:
                try:
                    for transaction_id in selected_transactions:
                        row = df[df['id'] == transaction_id].iloc[0]
                        CategoryService.save_transaction_category(
                            row['original_category'],
                            row['merchant_name'],
                            row['description'],
                            bulk_category
                        )
                    st.success(f'Applied category "{bulk_category}" to {len(selected_transactions)} transactions!')
                    st.rerun()
                except Exception as e:
                    st.error(f'Error in bulk categorization: {str(e)}')


if __name__ == '__main__':
    main()
