import pandas as pd
import ta

def load_data(filename):
    data = pd.read_csv(filename)
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)
    return data

def apply_indicators(df):
    # RSI
    df['rsi'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    # MACD
    macd = ta.trend.MACD(close=df['Close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    return df

def generate_signals(df, invest_amount=5, max_budget=1000):
    signals = []
    position_sizes = []
    cumulative_invested = 0

    for i in range(1, len(df)):
        buy = (
            df['rsi'].iloc[i] < 30 and
            df['macd'].iloc[i] > df['macd_signal'].iloc[i] and
            df['Close'].iloc[i] < df['bb_low'].iloc[i]
        )
        sell = (
            df['rsi'].iloc[i] > 70 and
            df['macd'].iloc[i] < df['macd_signal'].iloc[i] and
            df['Close'].iloc[i] > df['bb_high'].iloc[i]
        )

        # Stop trading if budget exceeded
        if cumulative_invested + invest_amount > max_budget:
            signals.append('Hold')
            position_sizes.append(0)
            continue

        if buy:
            signals.append('Buy')
            position_size = invest_amount / df['Close'].iloc[i]
            cumulative_invested += invest_amount
        elif sell:
            signals.append('Sell')
            position_size = invest_amount / df['Close'].iloc[i]
            cumulative_invested += invest_amount
        else:
            signals.append('Hold')
            position_size = 0

        position_sizes.append(position_size)

    # Pad the first signal and position size
    signals = ['Hold'] + signals
    position_sizes = [0] + position_sizes
    df['signal'] = signals
    df['position_size'] = position_sizes
    return df

if __name__ == "__main__":
    # Replace 'your_data.csv' with your actual data file path
    df = load_data('your_data.csv')
    df = apply_indicators(df)
    df = generate_signals(df, invest_amount=5, max_budget=1000)
    print(df[['Close', 'rsi', 'macd', 'macd_signal', 'bb_high', 'bb_low', 'signal', 'position_size']].tail(10))
