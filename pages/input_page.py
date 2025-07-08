"""
Input Page - Frontend UI for uploading and mapping transaction data
"""
import streamlit as st
from services.input_service import InputService
from services.navigation_service import NavigationService
from utils.output_log import logger


def main():
    # Check authentication
    if NavigationService.redirect_to_login_if_not_authenticated():
        st.warning('Please login first.')
        return

    username = st.session_state['username']
    
    st.header('Import Transactions')

    # Account selection
    accounts = InputService.get_accounts()
    account = st.selectbox('Select Account', ['New Account'] + accounts)
    if account == 'New Account':
        account = st.text_input('Enter new account name')

    # File upload
    uploaded = st.file_uploader('Upload CSV', type=['csv'])
    if uploaded:
        try:
            df = InputService.process_csv_upload(uploaded, account)
            
            st.success(f'File uploaded successfully! Found {len(df)} transactions.')
            st.write('Preview of uploaded data:')
            st.dataframe(df.head(), use_container_width=True)
            
            # Field mapping section
            st.subheader('Field Mapping')
            st.write('Required fields: date, post_date, original_category, merchant_name, description, amount')
            
            mappings = {}
            saved = InputService.get_saved_mappings(account)
            
            required_fields = ['account_type', 'date', 'post_date', 'original_category', 'merchant_name', 'description', 'currency', 'amount']
            
            # Create mapping interface
            col1, col2 = st.columns(2)
            
            for i, field in enumerate(required_fields):
                csv_columns = df.columns.tolist()
                saved_value = saved.get(field, '')
                
                # Parse saved value to handle multiple selections or manual input
                if saved_value and saved_value not in ['USD', 'CAD'] and saved_value != '<manual>':
                    if ';' in saved_value:
                        # Multiple columns were previously selected
                        default_columns = [col for col in saved_value.split(';') if col in csv_columns]
                        default_manual = '' if default_columns else saved_value
                    else:
                        # Single column or manual value
                        default_columns = [saved_value] if saved_value in csv_columns else []
                        default_manual = saved_value if saved_value not in csv_columns else ''
                elif saved_value in ['USD', 'CAD']:
                    default_columns = []
                    default_manual = saved_value
                else:
                    default_columns = []
                    default_manual = ''
                
                with col1 if i % 2 == 0 else col2:
                    if field == 'account_type':
                        # Account type selection
                        account_type = st.selectbox(
                            'Select Account Type',
                            ['debit', 'credit'],
                            index=0 if saved_value == 'debit' else 1,
                            key=f"account_type_{field}",
                            help="Select the type of account for this mapping"
                        )
                        mappings[field] = account_type
                        continue
                    # Multi-select for CSV columns
                    selected_columns = st.multiselect(
                        f'Select column(s) for {field}',
                        csv_columns,
                        default=default_columns,
                        key=f"multiselect_{field}",
                        help=f"Select one or more columns for {field}. Multiple columns will be joined with ';'"
                    )
                    
                    # Manual input option
                    use_manual = False  # Initialize for non-currency fields
                    if field == 'currency':
                        manual_options = ['', 'USD', 'CAD', '<manual>']
                        # Determine default selection for currency
                        if default_manual in ['USD', 'CAD', '']:
                            manual_default = default_manual
                        else:
                            manual_default = '<manual>'
                        
                        manual_selection = st.selectbox(
                            f'Or use fixed value for {field}',
                            manual_options,
                            index=manual_options.index(manual_default) if manual_default in manual_options else 0,
                            key=f"manual_select_{field}",
                            help="Use a fixed value for all transactions"
                        )
                        
                        if manual_selection == '<manual>':
                            manual_value = st.text_input(
                                f'Enter custom value for {field}',
                                value=default_manual if default_manual not in ['USD', 'CAD', ''] else '',
                                key=f"manual_input_{field}"
                            )
                        else:
                            manual_value = manual_selection
                    else:
                        # For other fields, show manual input option
                        use_manual = st.checkbox(
                            f'Use fixed value for {field}',
                            value=bool(default_manual and not selected_columns),
                            key=f"use_manual_{field}",
                            help="Check to enter a fixed value for all transactions"
                        )
                        
                        if use_manual:
                            manual_value = st.text_input(
                                f'Enter fixed value for {field}',
                                value=default_manual,
                                key=f"manual_{field}",
                                help="This value will be used for all transactions"
                            )
                        else:
                            manual_value = ''
                    
                    # Determine final mapping value
                    if selected_columns:
                        mappings[field] = ';'.join(selected_columns)
                    elif field == 'currency' and manual_value:
                        mappings[field] = manual_value
                    elif field != 'currency' and use_manual and manual_value:
                        mappings[field] = manual_value
                    else:
                        mappings[field] = ''

            # Import button
            if st.button('Save Mapping & Import', type='primary'):
                if not account:
                    st.error('Please select or enter an account name.')
                elif not all(mappings.values()):
                    st.error('Please map all required fields.')
                else:
                    try:
                        with st.spinner('Processing and importing transactions...'):
                            count = InputService.save_mappings_and_import(account, mappings, uploaded, username)
                        
                        st.success(f'Successfully imported {count} transactions!')
                        
                        # Offer to navigate to home page
                        if st.button('View Transactions'):
                            st.session_state['page'] = 'home'
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f'Error importing transactions: {str(e)}')
                        logger.error(f"Import error for user {username}: {str(e)}")

        except Exception as e:
            st.error(f'Error processing file: {str(e)}')
            logger.error(f"File processing error: {str(e)}")


if __name__ == '__main__':
    main()
