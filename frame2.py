import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from nsepython import *
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.utils import ImageReader
import plotly.express as px

sns.set_theme(style="darkgrid")

def generate_pdf_report(portfolio_data, start_date, end_date):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(30, 750, "Portfolio Analysis Report")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(30, 730, f"Date Range: {start_date} to {end_date}")
    
    y = 700

    for portfolio_name, data in portfolio_data.items():
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30, y, f"{portfolio_name}")
        pdf.setFont("Helvetica", 12)
        y -= 25
 
        pdf.drawString(50, y, "Holdings Summary:")
        y -= 20
        pdf.drawString(50, y, "Ticker   |   Weight   |   Latest Price")
        y -= 15
        weights = data['weights']
        latest_prices = data['prices'].iloc[-1]
        
        for ticker, weight in weights.items():
            pdf.drawString(50, y, f"{ticker}   |   {weight:.2%}   |   {latest_prices[ticker]:.2f}")
            y -= 15

        portfolio_value = calculate_portfolio_value(data['prices'], data['weights'])

        fig, ax = plt.subplots(figsize=(8, 4))
        portfolio_value.plot(ax=ax)
        ax.set_title(f"{portfolio_name} - Value Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Portfolio Value")

        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)

        y -= 20
        pdf.drawImage(ImageReader(img_buffer), 50, y - 300, width=500, height=250)
        plt.close(fig)
        
        y -= 320 

        if y < 100:
            pdf.showPage()
            y = 750
        
        y -= 20
    
    pdf.save()
    buffer.seek(0)
    return buffer

def calculate_custom_weights(tickers, num_stocks):
    total_stocks = sum(num_stocks.values())
    weights = {ticker: num_stocks[ticker] / total_stocks for ticker in tickers}
    return weights

def fetch_historical_data(tickers, start_date, end_date):
    all_data = {}
    for ticker in tickers:
        try:
            dates = pd.date_range(start_date, end_date)
            prices = np.random.uniform(100, 150, len(dates))
            data = pd.DataFrame({'Close': prices}, index=dates)
            if isinstance(data, dict):
                if data['status'] == 'success':
                    df = pd.DataFrame(data['data'])
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    all_data[ticker] = df[['close']]
            else:
                all_data[ticker] = data
                all_data[ticker].rename(columns={'Close':'close'}, inplace=True)

        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
    return all_data


def calculate_initial_weights(tickers):
    return {ticker: 1 / len(tickers) for ticker in tickers}


def apply_market_stress(prices, stress_factor):
  stressed_prices = prices.copy()
  for ticker in prices.columns:
      stressed_prices[ticker] = prices[ticker] * (1 - stress_factor)
  return stressed_prices


def calculate_portfolio_value(prices, weights):
  portfolio_value = (prices * pd.Series(weights)).sum(axis=1)
  return portfolio_value

def rebalance_portfolio(prices, target_weights, initial_weights, trade_threshold=0.02):
  # Rebalance weights towards target based on price change
    current_weights = {}
    for ticker in prices.columns:
       current_weights[ticker] = (prices[ticker].iloc[-1] * initial_weights[ticker])/sum([prices[t].iloc[-1]* initial_weights[t] for t in prices.columns])


    updated_weights = current_weights.copy()
    for ticker in prices.columns:
      if abs(updated_weights[ticker]- target_weights[ticker]) > trade_threshold:
          updated_weights[ticker] = target_weights[ticker]


    return updated_weights


def display_portfolio_summary(portfolio_data, title):
    st.subheader(title)
    if not portfolio_data:
        st.write("No portfolio data to display.")
        return

    portfolio_tables = []
    for key, values in portfolio_data.items():
        weights = values['weights']
        latest_prices = values['prices'].iloc[-1]

        df = pd.DataFrame({
            'Ticker': weights.keys(),
            'Weight': weights.values(),
            'Latest Price': latest_prices.values
        }).set_index('Ticker')
        portfolio_tables.append((key, df))

    for name, table in portfolio_tables:
        st.write(f"### {name}")
        st.dataframe(table)
    st.write("---")

    portfolio_values = {}
    for key, values in portfolio_data.items():
        portfolio_values[key] = calculate_portfolio_value(values['prices'], values['weights'])

    if portfolio_values:
        df_plot = pd.DataFrame()
        for key, pval in portfolio_values.items():
            df_plot[key] = pval
        df_plot.reset_index(inplace=True)
        df_plot_melt = pd.melt(df_plot, id_vars=['index'], var_name='Portfolio', value_name='Value')
        
        # Replace scatter plot with a line plot
        fig = px.line(
            df_plot_melt,
            x='index',
            y='Value',
            color='Portfolio',
            title="Portfolio Value Over Time (Line Plot)",
            labels={'index': 'Date', 'Value': 'Portfolio Value'},
            hover_data=['Portfolio', 'Value']
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig)
        
def main():
    st.title("Portfolio Rebalancing - Market Stress Simulator")

    st.sidebar.header("Portfolio Input")
    sample_tickers = ['TCS.NS', 'INFY.NS', 'RELIANCE.NS']
    tickers_str = st.sidebar.text_input(
        "Enter stock tickers separated by commas (e.g., TCS.NS, INFY.NS)",
        value=",".join(sample_tickers)
    )
    tickers = [ticker.strip().upper() for ticker in tickers_str.split(",")]
    start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.date.today())
    stress_factor = st.sidebar.slider("Stress Factor (Market Drop %)", 0.0, 1.0, 0.1)

    # Customizing number of stocks for each ticker
    num_stocks = {}
    st.sidebar.write("Set the number of stocks for each ticker:")
    for ticker in tickers:
        num_stocks[ticker] = st.sidebar.number_input(
            f"Number of stocks for {ticker}", min_value=1, value=10, step=1
        )

    if st.sidebar.button("Run Simulation"):
        with st.spinner("Fetching data and running simulation..."):
            prices = fetch_historical_data(tickers, start_date, end_date)

            if prices:
                # Initial portfolio with custom weights
                custom_weights = calculate_custom_weights(tickers, num_stocks)
                portfolio_data = {
                    'Initial Portfolio': {
                        'prices': pd.concat([d['close'] for d in prices.values()], axis=1),
                        'weights': custom_weights
                    }
                }
                portfolio_data['Initial Portfolio']['prices'].columns = tickers
                display_portfolio_summary(portfolio_data, "Initial Portfolio Summary")

                # Stressed Portfolio
                stressed_prices = apply_market_stress(portfolio_data['Initial Portfolio']['prices'], stress_factor)
                portfolio_data['Stressed Portfolio'] = {
                    'prices': stressed_prices,
                    'weights': portfolio_data['Initial Portfolio']['weights']
                }
                display_portfolio_summary(portfolio_data, 'Stressed Portfolio Summary')

                # Rebalanced Portfolio
                target_weights = custom_weights
                rebalanced_weights = rebalance_portfolio(stressed_prices, target_weights, custom_weights)
                portfolio_data['Rebalanced Portfolio'] = {
                    'prices': stressed_prices,
                    'weights': rebalanced_weights
                }
                display_portfolio_summary(portfolio_data, 'Rebalanced Portfolio Summary')

                # PDF Report
                pdf_report = generate_pdf_report(portfolio_data, start_date, end_date)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_report,
                    file_name="Portfolio_Analysis_Report.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
  main()
