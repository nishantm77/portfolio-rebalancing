# Portfolio Rebalancing - Market Stress Simulator

## Overview
This application is designed to analyze and simulate the performance of a stock portfolio under market stress conditions. It allows users to input stock tickers, set the number of stocks for each ticker, and apply a stress factor to simulate market drops. The application generates a comprehensive report that includes portfolio summaries and visualizations.

## Features
- **Portfolio Input**: Users can enter stock tickers and specify the number of stocks for each ticker.
- **Market Stress Simulation**: Apply a stress factor to simulate market drops and observe the impact on portfolio value.
- **Portfolio Rebalancing**: Automatically rebalance the portfolio based on target weights after applying market stress.
- **Visualizations**: Interactive line plots to visualize portfolio values over time.
- **PDF Report Generation**: Generate and download a PDF report summarizing the portfolio analysis.

## Technologies Used
- **Streamlit**: For building the web application interface.
- **Pandas**: For data manipulation and analysis.
- **NumPy**: For numerical operations.
- **Seaborn & Matplotlib**: For data visualization.
- **Plotly**: For interactive plotting.
- **ReportLab**: For generating PDF reports.
- **NSEPython**: For fetching historical stock data (simulated in this code).

## Installation
To run this application, ensure you have Python installed along with the required libraries. You can install the necessary packages using pip:

```bash
pip install streamlit pandas numpy seaborn matplotlib plotly reportlab nsepython
```

## Usage 
1. Clone the repository or download the code files.
2. Navigate to the directory containing frame2.py.
3. Run the Streamlit application using the following command:

```bash
streamlit run frame2.py
```
4. Open the provided local URL in your web browser.
5. Input the stock tickers, set the number of stocks, and adjust the stress factor as desired.
6. Click on "Run Simulation" to see the results.
7. Download the PDF report for a detailed analysis of your portfolio.

## Functions
1. Generates a PDF report summarizing the portfolio analysis.
   
```bash
generate_pdf_report(portfolio_data, start_date, end_date)
```

2. Calculates custom weights based on the number of stocks for each ticker.

```bash
calculate_custom_weights(tickers, num_stocks)
```

3. Fetches historical stock data for the specified tickers and date range.

```bash
fetch_historical_data(tickers, start_date, end_date)
```

4. Calculates initial equal weights for the portfolio.

```bash
calculate_initial_weights(tickers)
```

5. Applies a market stress factor to the portfolio prices.

```bash
apply_market_stress(prices, stress_factor)
```

6. Calculates the total value of the portfolio based on prices and weights.

```bash
calculate_portfolio_value(prices, weights)
```

7. Rebalances the portfolio towards target weights based on price changes.

```bash
rebalance_portfolio(prices, target_weights, initial_weights, trade_threshold)
```

8. Displays a summary of the portfolio data in the Streamlit app.

```bash
display_portfolio_summary(portfolio_data, title)
```


   
