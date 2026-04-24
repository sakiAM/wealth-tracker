import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# MUST be the first Streamlit command
st.set_page_config(
    page_title="Macro Indicators",
    page_icon="📊",
    layout="wide"
)
# Hide default sidebar navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Custom navigation in sidebar
with st.sidebar:
    st.page_link("myapp.py", label="Wealth Tracker", icon="💰")
    st.page_link("pages/1_📰_Finance_News.py", label="Finance News", icon="📰")
    st.page_link("pages/2_📊_Macro_Indicators.py", label="Macro Indicators", icon="📊")
    st.divider()

st.title("📊 Macro-Economic Indicators")
st.markdown("Track key economic metrics that drive financial markets")

# Sample macro data
def get_macro_data():
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='MS')
    
    return {
        'interest_rates': pd.DataFrame({
            'date': dates,
            'fed_rate': [4.25 + i*0.25 for i in range(len(dates))],
            'ecb_rate': [2.50 + i*0.15 for i in range(len(dates))],
            'rbi_rate': [6.25 + i*0.10 for i in range(len(dates))]
        }),
        'inflation': pd.DataFrame({
            'date': dates,
            'us_cpi': [6.5 - i*0.4 for i in range(len(dates))],
            'eu_cpi': [7.0 - i*0.35 for i in range(len(dates))],
            'india_cpi': [5.8 - i*0.3 for i in range(len(dates))]
        })
    }

macro_data = get_macro_data()

# Tabs for different indicator categories
tab1, tab2 = st.tabs(["🏛️ Central Banks", "💰 Inflation"])

with tab1:
    st.subheader("Central Bank Interest Rates")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=macro_data['interest_rates']['date'], y=macro_data['interest_rates']['fed_rate'], name='US Fed Rate', line=dict(width=3)))
    fig.add_trace(go.Scatter(x=macro_data['interest_rates']['date'], y=macro_data['interest_rates']['ecb_rate'], name='ECB Rate', line=dict(width=3)))
    fig.add_trace(go.Scatter(x=macro_data['interest_rates']['date'], y=macro_data['interest_rates']['rbi_rate'], name='RBI Rate', line=dict(width=3)))
    
    fig.update_layout(title='Central Bank Policy Rates', xaxis_title='Date', yaxis_title='Interest Rate (%)')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Inflation Trends (CPI)")
    
    fig = px.line(macro_data['inflation'].melt(id_vars=['date'], var_name='Country', value_name='CPI'), 
                 x='date', y='CPI', color='Country', title='Consumer Price Inflation')
    st.plotly_chart(fig, use_container_width=True)