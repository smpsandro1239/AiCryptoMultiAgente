import plotly.graph_objects as go
import pandas as pd

def create_trade_plot(price_history, trades):
    """
    Creates an interactive Plotly chart with price history and trade markers.
    price_history: DataFrame with 'timestamp' and 'close'
    trades: List of execution entries from memory
    """
    fig = go.Figure()

    # Price Line
    fig.add_trace(go.Scatter(
        x=price_history['timestamp'],
        y=price_history['close'],
        mode='lines',
        name='Price',
        line=dict(color='gray', width=1)
    ))

    # Buy Markers
    buys = [t for t in trades if t['side'] == 'BUY']
    if buys:
        fig.add_trace(go.Scatter(
            x=[t.get('timestamp', 0) for t in buys], # We might need to ensure timestamp is saved in execution
            y=[t['price'] for t in buys],
            mode='markers',
            name='BUY',
            marker=dict(symbol='triangle-up', size=12, color='green')
        ))

    # Sell Markers
    sells = [t for t in trades if t['side'] == 'SELL']
    if sells:
        fig.add_trace(go.Scatter(
            x=[t.get('timestamp', 0) for t in sells],
            y=[t['price'] for t in sells],
            mode='markers',
            name='SELL',
            marker=dict(symbol='triangle-down', size=12, color='red')
        ))

    fig.update_layout(
        title="Price History & Trade Execution",
        xaxis_title="Time",
        yaxis_title="Price",
        template="plotly_dark",
        height=600
    )

    return fig
