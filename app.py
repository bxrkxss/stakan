import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import time

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="live-update-graph"),
        dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
    ]
)

def get_order_book(symbol):
    url = f"https://api.bybit.com/v2/public/orderBook/L2?symbol={symbol}"
    response = requests.get(url)
    return response.json()

def get_last_trade(symbol):
    url = f"https://api.bybit.com/v2/public/trading-records?symbol={symbol}"
    response = requests.get(url)
    return response.json()["result"][0]

def create_figure(order_book, last_trade):
    bids = []
    asks = []

    for item in order_book["result"]:
        price = float(item["price"])
        quantity = int(item["size"])
        if item["side"] == "Buy":
            bids.append((price, quantity))
        else:
            asks.append((price, quantity))

    bids = sorted(bids, key=lambda x: x[0], reverse=True)
    asks = sorted(asks, key=lambda x: x[0])

    bid_prices, bid_volumes = zip(*bids)
    ask_prices, ask_volumes = zip(*asks)

    last_trade_price = float(last_trade["price"])

    fig = go.Figure()

    fig.add_trace(go.Bar(x=bid_prices, y=bid_volumes, name="Bid Volume", marker_color="green"))
    fig.add_trace(go.Bar(x=ask_prices, y=ask_volumes, name="Ask Volume", marker_color="red"))
    fig.add_shape(type="line", x0=last_trade_price, x1=last_trade_price, y0=0, y1=1, yref="paper", xref="x", line=dict(color="blue", width=2, dash="dash"))

    fig.update_layout(title="Bybit Order Book Visualization", xaxis_title="Price", yaxis_title="Volume")
    return fig

@app.callback(Output("live-update-graph", "figure"), [Input("interval-component", "n_intervals")])
def update_graph(n):
    symbol = "BTCUSD"
    order_book = get_order_book(symbol)
    last_trade = get_last_trade(symbol)
    fig = create_figure(order_book, last_trade)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
