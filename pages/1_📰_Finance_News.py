import streamlit as st
import pandas as pd

# MUST be the first Streamlit command
st.set_page_config(
    page_title="Finance News",
    page_icon="📰",
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

st.title("📰 Financial News Dashboard")
st.markdown("Stay updated with market-moving news")

# Sample news data
def get_sample_news():
    return [
        {
            'title': 'Fed Holds Rates Steady, Signals Possible Future Cuts',
            'source': 'Financial Times',
            'date': '2024-01-15',
            'impact': 'High',
            'category': 'Central Banks',
            'summary': 'Federal Reserve maintains current interest rates while hinting at potential cuts in the coming months based on inflation data.'
        },
        {
            'title': 'Tech Stocks Rally on Strong Earnings Reports',
            'source': 'Bloomberg',
            'date': '2024-01-14',
            'impact': 'Medium',
            'category': 'Equities',
            'summary': 'Major technology companies exceed earnings expectations, driving NASDAQ to record highs.'
        },
        {
            'title': 'Oil Prices Volatile Amid Middle East Tensions',
            'source': 'Reuters',
            'date': '2024-01-13',
            'impact': 'High',
            'category': 'Commodities',
            'summary': 'Brent crude fluctuates as geopolitical tensions raise supply concerns.'
        }
    ]

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Latest Market News")
    
    news_data = get_sample_news()
    
    for news in news_data:
        with st.container():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**{news['title']}**")
                st.write(news['summary'])
                st.caption(f"Source: {news['source']} | {news['date']}")
            with col_b:
                impact_color = "red" if news['impact'] == 'High' else "orange" if news['impact'] == 'Medium' else "green"
                st.markdown(f"<p style='color: {impact_color}; font-weight: bold;'>{news['impact']} Impact</p>", unsafe_allow_html=True)
                st.write(f"**{news['category']}**")
            
            st.divider()

with col2:
    st.subheader("🔍 News Filter")
    
    selected_impact = st.multiselect(
        "Impact Level",
        ["High", "Medium", "Low"],
        default=["High", "Medium"]
    )
    
    selected_categories = st.multiselect(
        "Categories",
        ["Central Banks", "Equities", "Commodities", "Economy", "Bonds", "Currency"],
        default=["Central Banks", "Equities", "Economy"]
    )