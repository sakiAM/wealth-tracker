How to install and run streamlit: https://www.youtube.com/watch?v=ZZ4B0QUHuNc&list=PLtqF5YXg7GLmCvTswG32NqQypOuYkPRUE&index=1
How to run stuff in VS Code, activating conda: https://www.youtube.com/watch?v=bf7pCxj6mEg&t=1s
Error to be resolved: Setting up env variable
Streamlit Documentation: https://docs.streamlit.io/
YFinance may not be the best-maintained library since it scrapes data from the official Yahoo Finance site

Requirements
- Something that can read from csv/excels and add stuff into tables or showcase in charts
- Pick up stocks data from YFinance/NSE
	- Store them in a DB Table. Should have metrics like daily High, daily Low, Open, Close, 52 Week High, 52 Week Low, 
	- Look at Top Gainers, Only Buyers, 52 Week High, Price Shockers, Volume Shockers
	- Have these in a dashboard with filters for time period (last 1 day, last 1 week, last one month)
- Login Page and Credentials
- Menu Navigation and state information retained (remember inPharmative?)

So, just set up a website with login and credentials. The home page just shows you the dashboard for Top Gainers (Top 10), Only Buyers (Top 10), 52 Week High, Price Shocks, Volume Shocks. Once you have these details shown on the UI, you can go to a separate tab that shows recent trends based on the dashboard.


AI Agents using phiDATA and Streamlit:https://www.youtube.com/watch?v=65j0-C4e_G4

1- A simple wealth dashboard app built using Streamlit
