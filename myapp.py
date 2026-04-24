import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
#from database import WealthDatabase  # Import our working database class
from supabase_db import SupabaseDB
db = SupabaseDB()

# Initialize database (local)
# db = WealthDatabase()

# =============================================
# SESSION STATE INITIALIZATION
# =============================================
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"

# =============================================
# PAGE CONFIG
# =============================================
st.set_page_config(
    page_title="Wealth Tracker",
    page_icon="💰",
    layout="wide"
)

# =============================================
# CUSTOM CSS
# =============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        color: #0f5132;
        background-color: #d1e7dd;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        color: #842029;
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    /* Hide default sidebar navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# LOGIN PAGE
# =============================================
def show_login_page():
    """Display login/signup page"""
    st.markdown('<div class="main-header">💰 Wealth Tracker</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if username and password:
                        user_id = db.authenticate_user(username, password)
                        if user_id:
                            st.session_state.user_id = user_id
                            st.session_state.username = username
                            st.session_state.current_page = "dashboard"
                            st.success(f"Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter both username and password")
        
        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                email = st.text_input("Email (optional)")
                
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not new_username or not new_password:
                        st.warning("Username and password are required")
                    elif new_password != confirm_password:
                        st.error("Passwords don't match!")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        user_id = db.create_user(new_username, new_password, email)
                        if user_id:
                            st.session_state.user_id = user_id
                            st.session_state.username = new_username
                            st.session_state.current_page = "dashboard"
                            st.success(f"Account created successfully! Welcome, {new_username}!")
                            st.rerun()
                        else:
                            st.error("Username already exists. Please choose another.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# CALCULATION FUNCTIONS
# =============================================
def calculate_metrics(df):
    """Calculate financial metrics from dataframe"""
    if df.empty:
        return df
    
    df = df.copy()
    df['total_assets'] = df[['cash', 'equities', 'debt_instruments', 'real_estate']].sum(axis=1)
    df['net_worth'] = df['total_assets'] + df['loans']
    df['emergency_fund_months'] = df['cash'] / df['monthly_expenses']
    
    # Allocation percentages
    df['equity_allocation'] = (df['equities'] / df['total_assets'] * 100).round(1)
    df['debt_allocation'] = (df['debt_instruments'] / df['total_assets'] * 100).round(1)
    df['cash_allocation'] = (df['cash'] / df['total_assets'] * 100).round(1)
    df['real_estate_allocation'] = (df['real_estate'] / df['total_assets'] * 100).round(1)
    
    return df

def calculate_rebalancing(current_data, target_allocations):
    """Calculate rebalancing suggestions"""
    total_assets = current_data['total_assets']
    suggestions = []
    
    asset_mapping = {
        'equities': 'Equities',
        'debt_instruments': 'Debt', 
        'cash': 'Cash',
        'real_estate': 'Real Estate'
    }
    
    for data_column, display_name in asset_mapping.items():
        current_value = current_data[data_column]
        current_percentage = (current_value / total_assets) * 100
        target_percentage = target_allocations[data_column]
        target_value = (target_percentage / 100) * total_assets
        difference = target_value - current_value
        
        # Get user's currency preference (default to ₹)
        currency = st.session_state.get('currency', '₹')
        
        suggestions.append({
            'Asset': display_name,
            'Current %': round(current_percentage, 1),
            'Target %': target_percentage,
            'Current Value': f"{currency}{current_value:,.0f}",
            'Target Value': f"{currency}{target_value:,.0f}",
            'Action Needed': f"{currency}{abs(difference):,.0f}",
            'Action': 'BUY' if difference > 0 else 'SELL' if difference < 0 else 'HOLD'
        })
    
    return pd.DataFrame(suggestions)

# =============================================
# MAIN DASHBOARD
# =============================================
def show_dashboard():
    """Display main wealth tracker dashboard"""

    # Load user data FIRST (before sidebar)
    user_data = db.get_user_entries(st.session_state.user_id)

    
    
    # Sidebar - User info and controls
    with st.sidebar:
        # Custom navigation
        st.page_link("myapp.py", label="Wealth Tracker", icon="💰")
        st.page_link("pages/1_📰_Finance_News.py", label="Finance News", icon="📰")
        st.page_link("pages/2_📊_Macro_Indicators.py", label="Macro Indicators", icon="📊")
        st.divider()
        st.write(f"👋 **Welcome, {st.session_state.username}!**")
        
        if st.button("🚪 Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.current_page = "login"
            st.rerun()
        
        st.divider()
        
        # Load user preferences
        prefs = db.get_user_preferences(st.session_state.user_id)
        if prefs:
            currency = prefs.get('currency_symbol', '₹')
            st.session_state.currency = currency
        else:
            currency = '₹'


           # Target allocations - Simple number inputs
        st.subheader("🎯 Target Allocations")
        
        # Initialize target values from preferences
        if prefs:
            default_equity = prefs.get('target_equity', 60)
            default_debt = prefs.get('target_debt', 25)
            default_cash = prefs.get('target_cash', 10)
            default_re = prefs.get('target_real_estate', 5)
        else:
            default_equity, default_debt, default_cash, default_re = 60, 25, 10, 5
        
        # Use columns for better layout
        col_e, col_d, col_c, col_re = st.columns(4)
        
        with col_e:
            equity_target = st.number_input(
                "Equity %", 
                min_value=0, 
                max_value=100, 
                value=default_equity,
                step=5,
                key="equity_target"
            )
        
        with col_d:
            debt_target = st.number_input(
                "Debt %", 
                min_value=0, 
                max_value=100, 
                value=default_debt,
                step=5,
                key="debt_target"
            )
        
        with col_c:
            cash_target = st.number_input(
                "Cash %", 
                min_value=0, 
                max_value=100, 
                value=default_cash,
                step=5,
                key="cash_target"
            )
        
        with col_re:
            real_estate_target = st.number_input(
                "Real Estate %", 
                min_value=0, 
                max_value=100, 
                value=default_re,
                step=5,
                key="re_target"
            )
        
        # Calculate total
        total_target = equity_target + debt_target + cash_target + real_estate_target
        
        if total_target != 100:
            st.warning(f"⚠️ Total: {total_target}% (should be 100%)")
            st.caption("💡 Adjust the numbers above to sum to 100%")
        else:
            st.success("✅ Allocation: 100%")
        
        # Save preferences when changed and total is 100
        if prefs and total_target == 100:
            if (equity_target != prefs.get('target_equity', 60) or 
                debt_target != prefs.get('target_debt', 25) or 
                cash_target != prefs.get('target_cash', 10) or
                real_estate_target != prefs.get('target_real_estate', 5)):
                db.update_preferences(
                    st.session_state.user_id,
                    target_equity=equity_target,
                    target_debt=debt_target,
                    target_cash=cash_target,
                    target_real_estate=real_estate_target
                )
                st.success("✅ Targets updated!")
        
       
        # ===== MANUAL ENTRY SECTION =====
        st.divider()
        
        # Initialize session state for manual entry
        if 'manual_entry_expanded' not in st.session_state:
            st.session_state.manual_entry_expanded = False
        if 'manual_entry_message' not in st.session_state:
            st.session_state.manual_entry_message = None
        if 'manual_entry_message_type' not in st.session_state:
            st.session_state.manual_entry_message_type = None
        
        # Show success/error message if exists (outside expander)
        if st.session_state.manual_entry_message:
            if st.session_state.manual_entry_message_type == "success":
                st.success(st.session_state.manual_entry_message)
                st.balloons()
            else:
                st.error(st.session_state.manual_entry_message)
            
            if st.button("✓ OK", key="dismiss_manual_msg", use_container_width=True):
                st.session_state.manual_entry_message = None
                st.session_state.manual_entry_message_type = None
                st.rerun()
        
        # Get count of entries
        entry_count = len(user_data) if not user_data.empty else 0
        
        # Create expander with summary in title
        with st.expander(f"➕ Add New Entry ({entry_count} entries)", expanded=st.session_state.manual_entry_expanded):
            
            with st.form("manual_entry_form"):
                entry_date = st.date_input("Date", datetime.now())
                cash = st.number_input("Cash", min_value=0.0, value=50000.0, step=1000.0)
                equities = st.number_input("Equities", min_value=0.0, value=300000.0, step=1000.0)
                debt = st.number_input("Debt Instruments", min_value=0.0, value=150000.0, step=1000.0)
                real_estate = st.number_input("Real Estate", min_value=0.0, value=400000.0, step=1000.0)
                loans = st.number_input("Loans (negative)", max_value=0.0, value=-200000.0, step=1000.0)
                expenses = st.number_input("Monthly Expenses", min_value=0.0, value=10000.0, step=500.0)
                notes = st.text_area("Notes (optional)")
                
                submitted = st.form_submit_button("💾 Save Entry", use_container_width=True)
                
                if submitted:
                    if entry_date > datetime.now().date():
                        st.session_state.manual_entry_message = "❌ Date cannot be in the future"
                        st.session_state.manual_entry_message_type = "error"
                        st.session_state.manual_entry_expanded = True
                        st.rerun()
                    else:
                        success = db.add_wealth_entry(
                            user_id=st.session_state.user_id,
                            date=entry_date,
                            cash=cash,
                            equities=equities,
                            debt_instruments=debt,
                            real_estate=real_estate,
                            loans=loans,
                            monthly_expenses=expenses,
                            notes=notes
                        )
                        
                        if success:
                            st.session_state.manual_entry_message = f"✅ Entry for {entry_date.strftime('%Y-%m-%d')} saved successfully!"
                            st.session_state.manual_entry_message_type = "success"
                            st.session_state.manual_entry_expanded = False
                            st.rerun()
                        else:
                            st.session_state.manual_entry_message = "❌ Failed to save entry. Please try again."
                            st.session_state.manual_entry_message_type = "error"
                            st.session_state.manual_entry_expanded = True
                            st.rerun()
        
        # ===== ADD SPREADSHEET UPLOAD HERE =====
                # ===== BULK UPLOAD DATA =====
        # Initialize session state for bulk upload
        if 'upload_expanded' not in st.session_state:
            st.session_state.upload_expanded = False  # Default to collapsed
        if 'upload_success_message' not in st.session_state:
            st.session_state.upload_success_message = None
        if 'upload_error_message' not in st.session_state:
            st.session_state.upload_error_message = None
        
        # Show success message if exists (outside expander)
        if st.session_state.upload_success_message:
            st.success(st.session_state.upload_success_message)
            st.balloons()
            if st.button("✓ Got it", key="clear_upload_success", use_container_width=True):
                st.session_state.upload_success_message = None
                st.rerun()
        
        # Show error message if exists
        if st.session_state.upload_error_message:
            st.error(st.session_state.upload_error_message)
            if st.button("✗ Dismiss", key="clear_upload_error", use_container_width=True):
                st.session_state.upload_error_message = None
                st.rerun()
        
        # Create expander with controlled state
        with st.expander("📤 Bulk Upload Data", expanded=st.session_state.upload_expanded):
            st.write("Upload a CSV file with multiple entries at once")
            st.info("📅 **Date format:** Use `DD/MM/YYYY` (e.g., `15/01/2026` for 15th January 2026)")
            
            # Template download
            with st.container():
                st.markdown("**📥 Download Template**")
                template_df = pd.DataFrame({
                    'date': ['15/01/2026', '15/02/2026', '15/03/2026'],  # DD/MM/YYYY format
                    'cash': [50000, 52000, 55000],
                    'equities': [300000, 310000, 325000],
                    'debt_instruments': [150000, 152000, 155000],
                    'real_estate': [400000, 402000, 405000],
                    'loans': [-200000, -198000, -195000],
                    'monthly_expenses': [10000, 10200, 10500],
                    'notes': ['Quarter start', 'Mid quarter', 'Quarter end']
                })
                
                csv_template = template_df.to_csv(index=False)
                st.download_button(
                    label="📋 Download CSV Template",
                    data=csv_template,
                    file_name="wealth_upload_template.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_template_btn"
                )
            
            st.markdown("---")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose a CSV file", 
                type=['csv'],
                key="bulk_uploader",
                help="File must match the template format"
            )
            
            if uploaded_file is not None:
                try:
                    # Read the uploaded file
                    upload_df = pd.read_csv(uploaded_file)
                    
                    # Show preview
                    st.markdown(f"**Preview:** {len(upload_df)} rows found")
                    st.dataframe(upload_df.head(), use_container_width=True)
                    
                    # Validate columns
                    required_cols = ['date', 'cash', 'equities', 'debt_instruments', 
                                    'real_estate', 'loans', 'monthly_expenses']
                    
                    missing_cols = [col for col in required_cols if col not in upload_df.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
                        st.info("Please use the template format")
                    else:
                        # Validate data types
                        try:
                                                        # Convert date column
                            try:
                                upload_df['date'] = pd.to_datetime(upload_df['date'], dayfirst=True)
                            except Exception as e:
                                st.error(f"❌ Date error: {e}")
                                st.info("Please use DD/MM/YYYY format (e.g., 15/01/2026)")
                                st.stop()
                            
                            # Check for negative values where they shouldn't be
                            asset_cols = ['cash', 'equities', 'debt_instruments', 'real_estate', 'monthly_expenses']
                            for col in asset_cols:
                                if (upload_df[col] < 0).any():
                                    st.warning(f"⚠️ {col} has negative values. Assets should be positive.")
                            
                            # Loans should be negative or zero
                            if (upload_df['loans'] > 0).any():
                                st.warning("⚠️ Loans should be negative or zero. Converting positive values to negative.")
                                upload_df['loans'] = -upload_df['loans'].abs()
                            
                            # Summary of what will be imported
                            st.success("✅ File validation passed!")
                            
                            # Show import summary
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Rows to import", len(upload_df))
                            with col2:
                                date_range = f"{upload_df['date'].min().strftime('%Y-%m-%d')} to {upload_df['date'].max().strftime('%Y-%m-%d')}"
                                st.metric("Date range", date_range)
                            
                            # Import button
                            if st.button("📥 Import Data", type="primary", use_container_width=True, key="import_btn"):
                                success_count = 0
                                error_count = 0
                                error_details = []
                                
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for idx, row in upload_df.iterrows():
                                    try:
                                        # Update progress
                                        progress = (idx + 1) / len(upload_df)
                                        progress_bar.progress(progress)
                                        status_text.text(f"Importing row {idx + 1} of {len(upload_df)}: {row['date']}...")
                                        
                                        # Check if entry already exists for this date
                                        existing_entries = db.get_user_entries(st.session_state.user_id)
                                        date_str = row['date'].strftime('%Y-%m-%d')
                                        
                                        if not existing_entries.empty and date_str in existing_entries['date'].dt.strftime('%Y-%m-%d').values:
                                            # Update existing entry
                                            entry_id = existing_entries[existing_entries['date'].dt.strftime('%Y-%m-%d') == date_str]['entry_id'].iloc[0]
                                            db.delete_wealth_entry(st.session_state.user_id, entry_id)
                                        
                                        # Add to database
                                        success = db.add_wealth_entry(
                                            user_id=st.session_state.user_id,
                                            date=row['date'],
                                            cash=float(row['cash']),
                                            equities=float(row['equities']),
                                            debt_instruments=float(row['debt_instruments']),
                                            real_estate=float(row['real_estate']),
                                            loans=float(row['loans']),
                                            monthly_expenses=float(row['monthly_expenses']),
                                            notes=row.get('notes', '') if pd.notna(row.get('notes', '')) else ''
                                        )
                                        
                                        if success:
                                            success_count += 1
                                        else:
                                            error_count += 1
                                            error_details.append(f"Row {idx+1}: Failed to save")
                                            
                                    except Exception as e:
                                        error_count += 1
                                        error_details.append(f"Row {idx+1}: {str(e)}")
                                        print(f"Error importing row {idx}: {e}")
                                
                                progress_bar.empty()
                                status_text.empty()
                                
                                if error_count == 0:
                                    st.session_state.upload_success_message = f"✅ Successfully imported all {success_count} entries!"
                                    st.session_state.upload_expanded = False
                                    # Clear the file uploader by resetting the key
                                    st.rerun()
                                else:
                                    error_msg = f"⚠️ Imported {success_count} entries with {error_count} errors.\n"
                                    if error_details:
                                        error_msg += "\n" + "\n".join(error_details[:3])
                                        if len(error_details) > 3:
                                            error_msg += f"\n... and {len(error_details)-3} more errors"
                                    st.session_state.upload_error_message = error_msg
                                    st.session_state.upload_expanded = True
                                    if success_count > 0:
                                        st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Error processing file: {e}")
                            
                except Exception as e:
                    st.error(f"❌ Error reading file: {e}")
        
    
    # Main content
    st.title(f"💰 {st.session_state.username}'s Wealth Tracker")
    
    # Load user data
    user_data = db.get_user_entries(st.session_state.user_id)
    
    if user_data.empty:
        # No data yet - show welcome message and instructions
        st.info("👋 Welcome to your Wealth Tracker! Let's get started:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📝 Quick Start Guide
            
            1. **Add your first entry** using the form in the sidebar
            2. **Enter your current financial snapshot** (cash, investments, loans)
            3. **Set your target allocations** using the sliders
            4. **Watch your wealth grow** over time!
            """)
        
        with col2:
            st.markdown("""
            ### 💡 Pro Tips
            
            - Add entries **quarterly** to track progress
            - Update when you **rebalance** your portfolio
            - Use the **Rebalancing** tab for suggestions
            - Check **Emergency Fund** status regularly
            """)
        
        # Show sample data option
        if st.button("📥 Load Sample Data (for testing)"):
            # Add sample data
            today = datetime.now()
            last_q = today - timedelta(days=90)
            two_q_ago = today - timedelta(days=180)
            
            db.add_wealth_entry(st.session_state.user_id, two_q_ago,
                cash=45000, equities=280000, debt_instruments=145000,
                real_estate=400000, loans=-205000, monthly_expenses=10000,
                notes="Sample Q1")
            
            db.add_wealth_entry(st.session_state.user_id, last_q,
                cash=48000, equities=310000, debt_instruments=148000,
                real_estate=400000, loans=-202000, monthly_expenses=10000,
                notes="Sample Q2")
            
            db.add_wealth_entry(st.session_state.user_id, today,
                cash=50000, equities=300000, debt_instruments=150000,
                real_estate=400000, loans=-200000, monthly_expenses=10000,
                notes="Sample Q3")
            
            st.success("✅ Sample data loaded!")
            st.rerun()
    
    else:
        # Calculate metrics
        data = calculate_metrics(user_data)
        latest = data.iloc[-1]
        
        # Target allocations dictionary
        target_allocations = {
            'equities': equity_target,
            'debt_instruments': debt_target,
            'cash': cash_target,
            'real_estate': real_estate_target
        }
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            net_worth_change = ((latest['net_worth'] - data.iloc[-2]['net_worth']) / data.iloc[-2]['net_worth'] * 100) if len(data) > 1 else 0
            st.metric(
                "Net Worth",
                f"{currency}{latest['net_worth']:,.0f}",
                f"{net_worth_change:+.1f}%" if len(data) > 1 else None
            )
        
        with col2:
            emergency_status = "✅ Adequate" if latest['emergency_fund_months'] >= 6 else "⚠️ Build More"
            st.metric(
                "Emergency Fund",
                f"{latest['emergency_fund_months']:.1f} months",
                emergency_status
            )
        
        with col3:
            st.metric(
                "Equity Allocation",
                f"{latest['equity_allocation']:.1f}%",
                f"Target: {equity_target}%"
            )
        
        with col4:
            debt_ratio = (abs(latest['loans']) / latest['total_assets']) * 100
            st.metric(
                "Debt to Assets",
                f"{debt_ratio:.1f}%",
                "Good" if debt_ratio < 30 else "High"
            )
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Overview", "💰 Net Worth", "🥧 Allocation", 
            "📊 Growth", "🔄 Rebalancing", "📋 History"
        ])
        
        with tab1:
            st.subheader("📈 Financial Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Current allocation pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=['Equities', 'Debt', 'Cash', 'Real Estate'],
                    values=[
                        latest['equities'],
                        latest['debt_instruments'],
                        latest['cash'],
                        latest['real_estate']
                    ],
                    hole=0.4
                )])
                fig.update_layout(title="Current Asset Allocation")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Asset values over time
                fig = go.Figure()
                for asset in ['equities', 'debt_instruments', 'cash', 'real_estate']:
                    fig.add_trace(go.Scatter(
                        x=data['date'],
                        y=data[asset],
                        name=asset.replace('_', ' ').title(),
                        mode='lines'
                    ))
                fig.update_layout(title="Asset Growth Over Time")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("💰 Net Worth Over Time")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data['date'],
                y=data['net_worth'],
                mode='lines+markers',
                name='Net Worth',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ))
            fig.update_layout(
                title="Your Net Worth Journey",
                xaxis_title="Date",
                yaxis_title=f"Net Worth ({currency})"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("🥧 Asset Allocation Over Time")
            
            # Stacked area chart
            alloc_data = data.melt(
                id_vars=['date'],
                value_vars=['equities', 'debt_instruments', 'cash', 'real_estate'],
                var_name='Asset',
                value_name='Value'
            )
            alloc_data['Asset'] = alloc_data['Asset'].str.replace('_', ' ').str.title()
            
            fig = px.area(
                alloc_data,
                x='date',
                y='Value',
                color='Asset',
                title="How Your Wealth is Distributed"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.subheader("📊 Performance Analysis")
            
            if len(data) > 1:
                # Calculate growth metrics
                first_worth = data['net_worth'].iloc[0]
                latest_worth = data['net_worth'].iloc[-1]
                total_growth = ((latest_worth / first_worth) - 1) * 100
                
                # Time span
                first_date = data['date'].iloc[0]
                last_date = data['date'].iloc[-1]
                days = (last_date - first_date).days
                years = days / 365.25
                
                # Annualized return
                if years > 0:
                    annualized_return = ((latest_worth / first_worth) ** (1/years) - 1) * 100
                else:
                    annualized_return = 0
                
                # Key metrics at the top
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Growth", f"{total_growth:.1f}%", 
                             delta_color="normal" if total_growth > 0 else "inverse")
                
                with col2:
                    st.metric("Annualized Return", f"{annualized_return:.1f}%" if years > 0 else "N/A")
                
                with col3:
                    best_month = data['net_worth'].pct_change().max() * 100
                    st.metric("Best Period", f"{best_month:.1f}%")
                
                with col4:
                    worst_month = data['net_worth'].pct_change().min() * 100
                    st.metric("Worst Period", f"{worst_month:.1f}%")
                
                # Growth rate chart (different from net worth chart)
                st.subheader("📈 Period-over-Period Growth Rates")
                
                # Calculate growth rates
                data_growth = data.copy()
                data_growth['growth_rate'] = data_growth['net_worth'].pct_change() * 100
                data_growth['period_label'] = data_growth['date'].dt.strftime('%Y-%m')
                
                # Color based on positive/negative
                colors = ['green' if x > 0 else 'red' for x in data_growth['growth_rate'].iloc[1:]]
                
                fig = go.Figure()
                
                # Add bar chart for growth rates
                fig.add_trace(go.Bar(
                    x=data_growth['period_label'].iloc[1:],
                    y=data_growth['growth_rate'].iloc[1:],
                    marker_color=colors,
                    text=data_growth['growth_rate'].iloc[1:].round(1),
                    textposition='outside',
                    texttemplate='%{text}%',
                    name='Growth Rate'
                ))
                
                # Add horizontal line at 0
                fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)
                
                fig.update_layout(
                    title="Period Growth Rates",
                    xaxis_title="Period",
                    yaxis_title="Growth (%)",
                    yaxis=dict(ticksuffix="%", gridcolor='lightgray'),
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Rolling returns (if enough data)
                if len(data) >= 4:
                    st.subheader("📊 Rolling Returns")
                    
                    # Calculate rolling returns
                    data['rolling_3m'] = data['net_worth'].pct_change(periods=min(3, len(data)-1)) * 100
                    
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=data['date'],
                        y=data['rolling_3m'],
                        mode='lines',
                        name='3-Period Rolling Return',
                        line=dict(color='orange', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(255,165,0,0.1)'
                    ))
                    
                    fig2.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig2.update_layout(
                        title="Rolling Returns (3-period moving average)",
                        xaxis_title="Date",
                        yaxis_title="Return (%)",
                        height=350,
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Performance insights
                st.subheader("💡 Performance Insights")
                
                insight_col1, insight_col2 = st.columns(2)
                
                with insight_col1:
                    st.markdown("**Positive Periods**")
                    positive_periods = (data_growth['growth_rate'] > 0).sum()
                    total_periods = len(data_growth) - 1
                    positive_pct = (positive_periods / total_periods) * 100 if total_periods > 0 else 0
                    st.progress(positive_pct/100, text=f"{positive_periods}/{total_periods} periods ({positive_pct:.0f}%)")
                
                with insight_col2:
                    st.markdown("**Volatility**")
                    volatility = data_growth['growth_rate'].std()
                    st.metric("Standard Deviation", f"{volatility:.2f}%")
                
                # Compare with targets
                st.subheader("🎯 Progress Toward Goals")
                
                # Simple goal setting
                goal_amount = st.number_input("Set a net worth goal", 
                                             min_value=float(latest_worth), 
                                             value=float(latest_worth * 1.5),
                                             step=100000.0)
                
                progress_pct = (latest_worth / goal_amount) * 100
                st.progress(progress_pct/100, text=f"{currency}{latest_worth:,.0f} of {currency}{goal_amount:,.0f} ({progress_pct:.1f}%)")
                
                # Time to goal (simple projection)
                if total_growth > 0 and years > 0:
                    annual_growth_rate = total_growth / years
                    years_to_goal = ((goal_amount / latest_worth) - 1) / (annual_growth_rate/100) if annual_growth_rate > 0 else 0
                    
                    if years_to_goal > 0 and years_to_goal < 100:
                        st.info(f"⏱️ At current growth rate, you'll reach your goal in approximately **{years_to_goal:.1f} years**")
            
            else:
                st.info("📭 Need at least 2 data points to show performance analysis. Add more entries!")
        with tab5:
            st.subheader("🔄 Portfolio Rebalancing")
            
            rebalancing_df = calculate_rebalancing(latest, target_allocations)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Current vs Target chart
                comp_data = pd.DataFrame({
                    'Asset': ['Equities', 'Debt', 'Cash', 'Real Estate'],
                    'Current': [
                        latest['equity_allocation'],
                        latest['debt_allocation'],
                        latest['cash_allocation'],
                        latest['real_estate_allocation']
                    ],
                    'Target': [equity_target, debt_target, cash_target, real_estate_target]
                })
                
                fig = px.bar(
                    comp_data,
                    x='Asset',
                    y=['Current', 'Target'],
                    title='Current vs Target Allocation',
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Rebalancing actions
                def color_actions(val):
                    if 'BUY' in str(val):
                        return 'background-color: #d4f8d4'
                    elif 'SELL' in str(val):
                        return 'background-color: #f8d4d4'
                    return ''
                
                st.dataframe(
                    rebalancing_df.style.applymap(color_actions, subset=['Action']),
                    use_container_width=True
                )
        
        with tab6:
            st.subheader("📋 Historical Data")
            
            # Prepare display data
            display_data = data.copy()
            display_data['date'] = display_data['date'].dt.strftime('%Y-%m-%d')
            display_data['net_worth_display'] = display_data['net_worth'].apply(lambda x: f"{currency}{x:,.0f}")
            display_data['cash_display'] = display_data['cash'].apply(lambda x: f"{currency}{x:,.0f}")
            display_data['equities_display'] = display_data['equities'].apply(lambda x: f"{currency}{x:,.0f}")
            display_data['debt_display'] = display_data['debt_instruments'].apply(lambda x: f"{currency}{x:,.0f}")
            display_data['real_estate_display'] = display_data['real_estate'].apply(lambda x: f"{currency}{x:,.0f}")
            display_data['loans_display'] = display_data['loans'].apply(lambda x: f"{currency}{x:,.0f}")
            
            # Custom CSS for table-like appearance
            st.markdown("""
            <style>
                .table-header {
                    background-color: #4a4a4a;
                    color: white;
                    padding: 10px;
                    border-radius: 5px 5px 0 0;
                    font-weight: bold;
                    text-align: center;
                }
                .table-row {
                    background-color: #2d2d2d;
                    padding: 8px;
                    border-bottom: 1px solid #4a4a4a;
                }
                .table-row:hover {
                    background-color: #3d3d3d;
                }
                .edit-mode {
                    background-color: #1e3a5f;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 5px 0;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # HEADERS ROW (at the top)
            header_cols = st.columns([1.2, 1.2, 0.8, 0.8, 0.8, 0.8, 0.8, 1.2])
            headers = ['Date', 'Net Worth', 'Cash', 'Equities', 'Debt', 'Real Estate', 'Loans', 'Actions']
            
            for col, header in zip(header_cols, headers):
                with col:
                    st.markdown(f"**{header}**")
            
            st.markdown("---")  # Separator line after headers
            
            # DATA ROWS
            for idx, row in display_data.iterrows():
                # Regular row view
                if not st.session_state.get(f"editing_{row['entry_id']}", False) and not st.session_state.get(f"deleting_{row['entry_id']}", False):
                    row_cols = st.columns([1.2, 1.2, 0.8, 0.8, 0.8, 0.8, 0.8, 1.2])
                    
                    with row_cols[0]:
                        st.write(row['date'])
                    with row_cols[1]:
                        st.write(row['net_worth_display'])
                    with row_cols[2]:
                        st.write(row['cash_display'])
                    with row_cols[3]:
                        st.write(row['equities_display'])
                    with row_cols[4]:
                        st.write(row['debt_display'])
                    with row_cols[5]:
                        st.write(row['real_estate_display'])
                    with row_cols[6]:
                        st.write(row['loans_display'])
                    with row_cols[7]:
                        col_edit, col_del = st.columns(2)
                        with col_edit:
                            if st.button("✏️", key=f"edit_{row['entry_id']}", help="Edit this entry"):
                                st.session_state[f"editing_{row['entry_id']}"] = True
                                st.rerun()
                        with col_del:
                            if st.button("🗑️", key=f"del_{row['entry_id']}", help="Delete this entry"):
                                st.session_state[f"deleting_{row['entry_id']}"] = True
                                st.rerun()
                
                # EDIT MODE (expands below the row)
                if st.session_state.get(f"editing_{row['entry_id']}", False):
                    with st.container():
                        st.markdown('<div class="edit-mode">', unsafe_allow_html=True)
                        st.markdown(f"**✏️ Editing Entry for {row['date']}**")
                        
                        with st.form(key=f"edit_form_{row['entry_id']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                edit_cash = st.number_input("Cash", value=float(row['cash']), min_value=0.0, step=1000.0)
                                edit_equities = st.number_input("Equities", value=float(row['equities']), min_value=0.0, step=1000.0)
                                edit_debt = st.number_input("Debt Instruments", value=float(row['debt_instruments']), min_value=0.0, step=1000.0)
                            
                            with col2:
                                edit_real_estate = st.number_input("Real Estate", value=float(row['real_estate']), min_value=0.0, step=1000.0)
                                edit_loans = st.number_input("Loans", value=float(row['loans']), max_value=0.0, step=1000.0)
                                edit_expenses = st.number_input("Monthly Expenses", value=float(row['monthly_expenses']), min_value=0.0, step=500.0)
                            
                            edit_notes = st.text_area("Notes", value=row['notes'] if pd.notna(row['notes']) else "")
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                                    # Delete old entry and add new one
                                    db.delete_wealth_entry(st.session_state.user_id, row['entry_id'])
                                    db.add_wealth_entry(
                                        user_id=st.session_state.user_id,
                                        date=pd.to_datetime(row['date']),
                                        cash=edit_cash,
                                        equities=edit_equities,
                                        debt_instruments=edit_debt,
                                        real_estate=edit_real_estate,
                                        loans=edit_loans,
                                        monthly_expenses=edit_expenses,
                                        notes=edit_notes
                                    )
                                    st.session_state[f"editing_{row['entry_id']}"] = False
                                    st.success("✅ Entry updated!")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel", use_container_width=True):
                                    st.session_state[f"editing_{row['entry_id']}"] = False
                                    st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # DELETE CONFIRMATION MODE
                if st.session_state.get(f"deleting_{row['entry_id']}", False):
                    with st.container():
                        st.warning(f"⚠️ Delete entry for {row['date']}?")
                        st.write(f"**Net Worth:** {row['net_worth_display']}")
                        
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("✅ Yes, Delete", key=f"confirm_del_{row['entry_id']}", type="primary", use_container_width=True):
                                if db.delete_wealth_entry(st.session_state.user_id, row['entry_id']):
                                    st.session_state[f"deleting_{row['entry_id']}"] = False
                                    st.success("✅ Entry deleted!")
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ No, Keep", key=f"cancel_del_{row['entry_id']}", use_container_width=True):
                                st.session_state[f"deleting_{row['entry_id']}"] = False
                                st.rerun()
                
                # Add a thin line between rows for better readability
                if idx < len(display_data) - 1:
                    st.markdown("<hr style='margin: 5px 0; opacity: 0.3;'>", unsafe_allow_html=True)
            
            # Summary section
            if not display_data.empty:
                st.markdown("---")
                st.subheader("📊 Summary Statistics")
                
                sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
                with sum_col1:
                    avg_net_worth = display_data['net_worth'].mean()
                    st.metric("Avg Net Worth", f"{currency}{avg_net_worth:,.0f}")
                
                with sum_col2:
                    total_entries = len(display_data)
                    st.metric("Total Entries", total_entries)
                
                with sum_col3:
                    date_range = (pd.to_datetime(display_data['date'].max()) - pd.to_datetime(display_data['date'].min())).days
                    st.metric("Time Span", f"{date_range} days")
                
                with sum_col4:
                    best_net_worth = display_data['net_worth'].max()
                    st.metric("Peak Net Worth", f"{currency}{best_net_worth:,.0f}")
# =============================================
# MAIN APP LOGIC
# =============================================
def main():
    """Main app controller"""
    if st.session_state.user_id is None:
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()