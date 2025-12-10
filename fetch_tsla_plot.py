import yfinance as yf
import mplfinance as mpf
import pandas as pd

# Fetch TSLA data
print("Fetching TSLA data...")
ticker = "TSLA"
period = "5y"
df = yf.download(ticker, period=period)

if df.empty:
    print("Error: No data fetched.")
    exit(1)

print(f"Fetched {len(df)} rows of data.")
print(df.head())
print(df.info())

# Flatten MultiIndex columns if necessary
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Create candle plot
print("Generating candle plot...")
output_file = "tsla_candle_plot.png"
mpf.plot(
    df,
    type="candle",
    style="yahoo",
    title=f"{ticker} - {period} Daily Candle Chart",
    ylabel="Price ($)",
    savefig=output_file
)

print(f"Plot saved to {output_file}")
