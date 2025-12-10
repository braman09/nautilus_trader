import asyncio
import datetime
import pandas as pd
import mplfinance as mpf
from nautilus_trader.adapters.interactive_brokers.common import IBContract
from nautilus_trader.adapters.interactive_brokers.historical import HistoricInteractiveBrokersClient
from nautilus_trader.model.data import BarType, BarSpecification

import pytz

async def fetch_and_plot():
    print("Connecting to Interactive Brokers Gateway on port 4002...")
    # Initialize the historic client
    # client_id=10 is arbitrary but must be unique
    client = HistoricInteractiveBrokersClient(host="127.0.0.1", port=4002, client_id=10)
    
    try:
        await client.connect()
        print("Connected.")
        
        # Allow some time for connection to stabilize
        await asyncio.sleep(2)

        # Define the contract for TSLA
        contract = IBContract(
            secType="STK",
            symbol="TSLA",
            exchange="SMART",
            primaryExchange="NASDAQ"
        )
        instrument_id = "TSLA.NASDAQ"

        # Request Instrument definition first (good practice)
        print("Requesting instrument definition...")
        instruments = await client.request_instruments(
            contracts=[contract],
            instrument_ids=[instrument_id]
        )
        if not instruments:
            print("Error: Could not find instrument.")
            return

        print(f"Found instrument: {instruments[0].id}")

        # Request 5 years of daily bars
        # Handle timezone: Convert UTC now to NY, then strip tz info for the API
        ny = pytz.timezone("America/New_York")
        now_ny = datetime.datetime.now(ny)
        end_time = now_ny.replace(tzinfo=None)
        start_time = end_time - datetime.timedelta(days=5*365)
        
        print(f"Requesting daily bars from {start_time.date()} to {end_time.date()} (NY Time)...")
        
        bars = await client.request_bars(
            bar_specifications=["1-DAY-MID"], # Daily bars, midpoint
            start_date_time=start_time,
            end_date_time=end_time,
            contracts=[contract],
            instrument_ids=[instrument_id],
            use_rth=True, # Regular Trading Hours
            tz_name="America/New_York",
            timeout=120
        )

        if not bars:
            print("Error: No bars returned.")
            return

        print(f"Fetched {len(bars)} bars.")

        # Convert to DataFrame
        data = []
        for bar in bars:
            # Timestamp is in nanoseconds, convert to datetime
            dt = datetime.datetime.fromtimestamp(bar.ts_event / 1e9)
            data.append({
                "Date": dt,
                "Open": float(bar.open),
                "High": float(bar.high),
                "Low": float(bar.low),
                "Close": float(bar.close),
                "Volume": float(bar.volume) if hasattr(bar, 'volume') and bar.volume else 0
            })
            
        df = pd.DataFrame(data)
        df.set_index("Date", inplace=True)
        
        print(df.head())
        print(df.info())

        # Plot
        print("Generating plot...")
        output_file = "tsla_ib_candle_plot.png"
        mpf.plot(
            df,
            type="candle",
            style="yahoo",
            title="TSLA - 5y Daily (Source: Interactive Brokers)",
            ylabel="Price ($)",
            savefig=output_file,
            volume=False # Midpoint data often doesn't have consistent volume in IB or might be separate
        )
        print(f"Plot saved to {output_file}")

    finally:
        print("Done.")

if __name__ == "__main__":
    asyncio.run(fetch_and_plot())
