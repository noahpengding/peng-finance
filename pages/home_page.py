"""
Home Page - Frontend UI for displaying transactions with filters
"""
import streamlit as st
from services.transaction_service import TransactionService
from services.navigation_service import NavigationService
from utils.sqlite_storage import remove_duplicates


def main():
    # Check authentication
    if NavigationService.redirect_to_login_if_not_authenticated():
        return

    # After authentication check
    username = st.session_state['username']
    
    # Get transactions using service
    df = TransactionService.get_user_transactions(username)
    
    if df.empty:
        st.info('No transactions found.')
        return

    # Get filter options
    filter_options = TransactionService.get_filter_options(df)

    # Sidebar filters
    st.sidebar.header('Filters')
    
    # Account filter with "All" option
    account_options = ['All'] + filter_options['accounts']
    selected_accounts_raw = st.sidebar.multiselect('Account', account_options, default=['All'])
    selected_accounts = filter_options['accounts'] + [""] if 'All' in selected_accounts_raw else selected_accounts_raw
    
    # Post Date filter with "All" option
    date_options = ['All'] + filter_options['post_dates']
    selected_dates_raw = st.sidebar.multiselect('Post Date', date_options, default=['All'])
    selected_dates = filter_options['post_dates'] + [""] if 'All' in selected_dates_raw else selected_dates_raw
    
    # Category filter with "All" option
    category_options = ['All'] + filter_options['categories']
    selected_categories_raw = st.sidebar.multiselect('Category', category_options, default=['All'])
    selected_categories = filter_options['categories'] + [""] if 'All' in selected_categories_raw else selected_categories_raw
    
    # Merchant filter with "All" option
    merchant_options = ['All'] + filter_options['merchants']
    selected_merchants_raw = st.sidebar.multiselect('Merchant', merchant_options, default=['All'])
    selected_merchants = filter_options['merchants'] + [""] if 'All' in selected_merchants_raw else selected_merchants_raw

    # Apply filters
    filtered_df = TransactionService.apply_filters(df, selected_accounts, selected_dates, selected_categories, selected_merchants) 

    # Display summary
    st.subheader('Transaction Summary')
    total_transactions = len(filtered_df)
    total_amount = filtered_df['amount'].sum()
    st.metric("Total Transactions", total_transactions)
    st.metric("Total Amount", f"${total_amount:,.2f}")

    # Display transactions
    st.subheader('Transactions')
    if not filtered_df.empty:
        # Remove ID column and display without row numbers
        display_df = filtered_df.drop(columns=['id'], errors='ignore')
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        if st.button('Remove Duplication'):
            remove_duplicates(username)
            st.success('Duplicates removed successfully!')
    else:
        st.info('No transactions match the selected filters.')


if __name__ == '__main__':
    main()
