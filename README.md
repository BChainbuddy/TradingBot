# Trading Bot with Double Supertrend and Heikin Ashi Candles

This README provides an overview of the Python trading bot, which combines double Supertrend indicators with Heikin Ashi candles to facilitate cryptocurrency trading on the Binance exchange. The bot executes both long and short orders based on the trading signals generated by these indicators.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Bot Configuration](#bot-configuration)
- [Bot Strategies](#bot-strategies)
- [Customization](#customization)
- [Running the Bot](#running-the-bot)
- [Monitoring Trades](#monitoring-trades)
- [License](#license)

## Overview

The trading bot is designed to execute cryptocurrency trades on the Binance exchange by utilizing the following strategies:

1. **Double Supertrend Indicator**: The Supertrend indicator is used to identify potential trend changes in the price of a cryptocurrency. The bot calculates Supertrend values for two different periods (10 and 20) to generate buy and sell signals.

2. **Heikin Ashi Candles**: The bot uses Heikin Ashi candlesticks to smooth out price data and reduce noise. This results in a more visually clear representation of the price movement, which can help improve trading decisions.

The bot will execute trades, including long and short positions, based on the buy and sell signals generated by these indicators. It also includes functions for managing positions, setting leverage, and displaying key trade-related information.

## Prerequisites

Before running the bot, ensure that you have the following prerequisites in place:

- Python 3 installed on your system.
- Required Python packages installed. You can install them using pip:
  ```
  pip install websocket-client pandas pandas-ta binance-client numpy talib
  ```
- An active Binance account with API key and API secret. Make sure to keep your API credentials secure.

## Getting Started

1. Clone the repository containing your trading bot code.

2. Make sure your Binance API credentials are ready. You will need your API key and API secret for the bot to interact with the exchange.

3. Configure your bot settings by editing the `config.py` file with your API key and API secret:

   ```python
   API_KEY = 'your_api_key'
   API_SECRET = 'your_api_secret'
   ```

## Bot Configuration

In the `tradingbot.py` script, you can configure several parameters to customize your trading bot:

- `SOCKET`: The WebSocket URL for receiving real-time cryptocurrency price data. You can change the trading pair and candlestick interval to match your preferences.

- **RSI Strategy Parameters**: These parameters define the Relative Strength Index (RSI) strategy. It is not included in the strategy currently but could be a great addition for the future.

  - `RSI_PERIOD`: The RSI period for the strategy.
  - `RSI_OVERBOUGHT`: The RSI level considered overbought.
  - `RSI_OVERSOLD`: The RSI level considered oversold.

- **Supertrend Strategy Parameters**: These parameters define the Supertrend strategy.

  - `ATR_PERIOD`: The Average True Range (ATR) period for the 10-period Supertrend.
  - `ATR_PERIOD2`: The ATR period for the 20-period Supertrend.
  - `MULTIPLIER`: The multiplier for the 10-period Supertrend.
  - `MULTIPLIER2`: The multiplier for the 20-period Supertrend.
  - `TRADE_SYMBOL`: The trading pair you want to trade.
  - `TRADE_QUANTITY`: The quantity to trade.
  - `LEVERAGE`: The leverage for your trade.

## Bot Strategies

The trading bot implements two primary strategies:

1. **Supertrend Strategy**: The Supertrend strategy uses the Supertrend indicator with two different periods (10 and 20) to generate buy and sell signals. The indicator considers trend changes based on the ATR and multiplier parameters. The bot places trades when buy or sell signals are generated by this strategy.

2. **Heikin Ashi Candles**: The bot uses Heikin Ashi candles to smooth the price data and improve signal quality. Heikin Ashi candles are calculated from the open, close, high, and low prices, and they provide a clearer representation of price trends.

## Customization

You can customize the bot by changing the trading pair, trading quantity, leverage, and other strategy-related parameters. Be cautious when modifying these parameters, as they can significantly impact your trading results.

## Running the Bot

To run the trading bot, execute the following command:

```
python tradingbot.py
```

The bot will connect to the Binance WebSocket, retrieve price data, and execute trades based on the specified strategies and parameters. It will print trade information and relevant details, such as open positions, balances, and orders.

## Monitoring Trades

The trading bot is designed to provide insights into the current state of your trading account. You can monitor open positions, orders, and trade history using functions like `position_information_short()`, `position_information_long()`, `get_orders()`, `get_balance()`, and more.

Additionally, you can view trade history and order status in your Binance account to keep track of your trades.

## License

This trading bot is provided under an open-source license. You can use, modify, and distribute it in accordance with the terms of the provided license. Be sure to review the license file included with the code for details.

---

**Disclaimer:** Trading cryptocurrencies involves risks, and this bot is intended for educational and informational purposes only. You should always conduct your research and consider your risk tolerance before engaging in real-world trading. The authors and maintainers of this bot are not responsible for any financial losses or consequences resulting from its use."
