# 💰 Wealth Tracker

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://wealth-tracker-demo.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

A full-stack personal wealth management platform with multi-user authentication, portfolio rebalancing, and interactive data visualizations. Track your net worth, monitor asset allocation, and make data-driven investment decisions.

## 🚀 Live Demo

**[Click here to view the live app](https://wealth-tracker-demo.streamlit.app)**

Test credentials (or create your own):
- Username: `demo` 
- Password: `demo123`

## ✨ Features

### Core Functionality
- 🔐 **Multi-User Authentication** - Secure login/signup with password hashing
- 📊 **Net Worth Tracking** - Visualize wealth growth over time
- 🥧 **Asset Allocation** - Pie charts and stacked area views
- 📈 **Performance Analysis** - Growth rates, rolling returns, volatility metrics
- 🔄 **Portfolio Rebalancing** - Automated BUY/SELL recommendations
- 📋 **Data Management** - Add, edit, delete wealth entries

### Data Features
- 📤 **Bulk CSV Upload** - Import multiple entries at once
- 📥 **CSV Export** - Download your data for backup
- 📅 **Quarterly Analysis** - Period-over-period growth tracking
- 🎯 **Custom Targets** - Set and track allocation goals

### Technical Architecture
- ☁️ **Cloud Database** - Supabase PostgreSQL for persistent storage
- 🔄 **Version Control** - Git/GitHub integration
- 🚀 **Live Deployment** - Streamlit Cloud with CI/CD
- 🔒 **Secure Secrets Management** - Environment variables for credentials

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.12 |
| **Database** | Supabase (PostgreSQL) |
| **Visualization** | Plotly, Plotly Express |
| **Data Processing** | Pandas |
| **Deployment** | Streamlit Cloud |
| **Version Control** | Git, GitHub |

## 🏗️ Future Roadmap
| Indian currency formatting (lakhs/crores)
| Real-time stock price integration
| Email notifications for quarterly check-ins
| Goal tracking with progress bars
| Mobile-responsive design
| Rate limiting