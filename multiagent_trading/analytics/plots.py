import plotly.graph_objects as go
import pandas as pd

class TradeVisualizer:
    """
    Gera gráficos interativos utilizando Plotly.
    """
    @staticmethod
    def plot_price_with_trades(df: pd.DataFrame, trades: list):
        """
        Cria um gráfico de preços com marcadores de compra e venda.
        """
        fig = go.Figure()

        # Linha de Preço
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Preço', line=dict(color='blue')))

        # Marcadores de Trades
        for trade in trades:
            color = 'green' if trade['side'] == 'BUY' else 'red'
            symbol = 'triangle-up' if trade['side'] == 'BUY' else 'triangle-down'
            fig.add_trace(go.Scatter(
                x=[trade['timestamp']],
                y=[trade['price']],
                mode='markers',
                marker=dict(color=color, symbol=symbol, size=12),
                name=trade['side']
            ))

        fig.update_layout(title='Análise de Preço e Execuções', xaxis_title='Tempo', yaxis_title='Preço')
        return fig
