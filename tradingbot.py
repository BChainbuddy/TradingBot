import websocket, ssl, json, pprint, talib, numpy
from datetime import datetime
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from binance.enums import *
import config

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"  # You can change the 1 minute to preferred length of a candlestick

client = Client(config.API_KEY, config.API_SECRET)

# RSI STRATEGY, here we can change our indicator parameters
RSI_PERIOD = 5
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# SUPERTREND STRATEGY, here we can change our indicator parameters
ATR_PERIOD = 10
ATR_PERIOD2 = 20
MULTIPLIER = 3
MULTIPLIER2 = 5
TRADE_SYMBOL = "btcusdt"
TRADE_QUANTITY = 0.10  # <--- need to set it up to be 0.1 of the whole account, this is for the amount of btcusd, so 0.0001*btc
LEVERAGE = 10

# ARRAYS OF CANDLESTICK STATISTICS
closes = []  # to make the closes in a list to read from
highs = []
lows = []
opens = []
# Heikin ashi candlestick
h_opens = []
h_closes = []
h_highs = []
h_lows = []
# Supertrend 10
true_range = []
atrs = []
upper_band = []
lower_band = []
final_upper_band = []
final_lower_band = []
supertrend = []
# Supertrend 20
atrs2 = []
upper_band2 = []
lower_band2 = []
final_upper_band2 = []
final_lower_band2 = []
supertrend2 = []
# BUY AND SELL SIGNALS
buys = []
sells = []
buys2 = []
sells2 = []
# RMA
atr_rma = []
pandas_rma = []
atr_rma2 = []
# STRATEGY
long = []
short = []

# ORDER DEFINITION
def order_short(quantity, slS, tpS):

    print("Placing order short...")

    client.futures_create_order(
        symbol="BTCUSDT",
        side="SELL",
        type="MARKET",
        quantity=quantity,
        isolated=True,
        positionSide="SHORT",
    )

    client.futures_create_order(
        symbol="BTCUSDT",
        side="BUY",
        type="STOP_MARKET",
        positionSide="SHORT",
        stopPrice=slS,
        closePosition="true",
        workingType="MARK_PRICE",
        timeInForce=TIME_IN_FORCE_GTC,
    )

    client.futures_create_order(
        symbol="BTCUSDT",
        side="BUY",
        type="TAKE_PROFIT_MARKET",
        positionSide="SHORT",
        stopPrice=tpS,
        closePosition="true",
        workingType="MARK_PRICE",
        timeInForce=TIME_IN_FORCE_GTC,
    )


def exit_short():  # THIS REDUCES SHORT
    client.futures_create_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity=100,  # 100 BTC REDUCTION SO IT FOR SURE EXITS POSITION
        type="MARKET",
        reduceOnly=True,
        positionSide="SHORT",
    )


def exit_short_hedge():  # THIS REDUCES SHORT
    client.futures_create_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity=100,  # 100 BTC REDUCTION SO IT FOR SURE EXITS POSITION
        type="MARKET",
        positionSide="SHORT",
    )


def order_long(quantity, tpL, slL):

    print("Placing order long...")

    client.futures_create_order(
        symbol="BTCUSDT",
        side="BUY",
        type="MARKET",
        quantity=quantity,
        isIsolated=True,
        positionSide="LONG",
    )

    client.futures_create_order(
        symbol="BTCUSDT",
        side="SELL",
        type="TAKE_PROFIT_MARKET",
        positionSide="LONG",
        stopPrice=tpL,
        closePosition="true",
        workingType="MARK_PRICE",
        timeInForce=TIME_IN_FORCE_GTC,
    )

    client.futures_create_order(
        symbol="BTCUSDT",
        side="SELL",
        type="STOP_MARKET",
        positionSide="LONG",
        stopPrice=slL,
        closePosition="true",
        workingType="MARK_PRICE",
        timeInForce=TIME_IN_FORCE_GTC,
        # priceProtect=True,
    )


def exit_long():  # THIS REDUCES LONG
    client.futures_create_order(
        symbol="BTCUSDT",
        side="SELL",
        quantity=100,  # 100 BTC REDUCTION SO IT FOR SURE EXITS POSITION
        type="MARKET",
        reduceOnly=True,
        positionSide="LONG",
    )


def exit_long_hedge():  # THIS REDUCES LONG
    client.futures_create_order(
        symbol="BTCUSDT",
        side="SELL",
        quantity=100,  # 100 BTC REDUCTION SO IT FOR SURE EXITS POSITION
        type="MARKET",
        positionSide="LONG",
    )


def get_orders():
    acc_orders = client.futures_get_open_orders(symbol=TRADE_SYMBOL)
    for check_orders in acc_orders:
        if check_orders["type"] == "STOP_MARKET":
            stop_market1 = check_orders["orderId"]
            stop_market2 = check_orders["stopPrice"]
            stop_market3 = check_orders["positionSide"]
            print("STOP LOSS:")
            print("ID:", stop_market1)
            print("Price:", stop_market2)
            print("Position side:", stop_market3)
            print("")
        if check_orders["type"] == "TAKE_PROFIT_MARKET":
            take_profit_market1 = check_orders["orderId"]
            take_profit_market2 = check_orders["stopPrice"]
            take_profit_market3 = check_orders["positionSide"]
            print("TAKE PROFIT:")
            print("ID:", take_profit_market1)
            print("Price:", take_profit_market2)
            print("Position side:", take_profit_market3)
            print("")

    # {'orderId': 83245777430, 'symbol': 'BTCUSDT', 'status': 'NEW', 'clientOrderId': '34snMR8GZI1lMhtyf9vzPV', 'price': '0', 'avgPrice': '0', 'origQty': '0', 'executedQty': '0', 'cumQuote': '0', 'timeInForce': 'GTC', 'type': 'STOP_MARKET', 'reduceOnly': True, 'closePosition': True, 'side': 'SELL', 'positionSide': 'BOTH', 'stopPrice': '17689.93'


def get_balance():
    acc_balance = client.futures_account_balance()
    for check_balance in acc_balance:
        if check_balance["asset"] == "USDT":
            usdt_balance = check_balance["balance"]
            return usdt_balance
            # We only need usdt because we are trading usdt margin trading


def change_leverage():
    client.futures_change_leverage(symbol=TRADE_SYMBOL, leverage=LEVERAGE)
    print("Leverage has been changed to:", LEVERAGE)


def cancel_all_orders_short():
    acc_orders = client.futures_get_open_orders(symbol=TRADE_SYMBOL)
    print("closing short orders...")
    for check_orders in acc_orders:
        if check_orders["positionSide"] == "SHORT":
            orderId = check_orders["orderId"]
            client.futures_cancel_order(symbol="BTCUSDT", orderId=orderId)


#    cancel_order = client.futures_cancel_order(symbol="BTCUSDT", orderId=orderId)


def cancel_all_orders_long():
    acc_orders = client.futures_get_open_orders(symbol=TRADE_SYMBOL)
    print("closing short orders...")
    for check_orders in acc_orders:
        if check_orders["positionSide"] == "LONG":
            orderId = check_orders["orderId"]
            client.futures_cancel_order(symbol="BTCUSDT", orderId=orderId)


#    cancel_order = client.futures_cancel_order(symbol="BTCUSDT", orderId=orderId)


def position_information_short():
    position_information = client.futures_position_information(symbol="BTCUSDT")
    for check_balance in position_information:
        if check_balance["positionSide"] == "SHORT":
            if check_balance["positionAmt"] != "0.000":
                symbol = check_balance["symbol"]
                quantity = check_balance["positionAmt"]
                openPrice = check_balance["entryPrice"]
                leverage = check_balance["leverage"]
                profit = check_balance["unRealizedProfit"]
                print("Short", symbol, "current quantity:", quantity)
                print("Position opened at", openPrice)
                print("Leverage:", leverage)
                print("Unrealized profit/loss", profit)
                return True
            else:
                return False


def position_information_long():
    position_information = client.futures_position_information(symbol="BTCUSDT")
    for check_balance in position_information:
        if check_balance["positionSide"] == "LONG":
            if check_balance["positionAmt"] != "0.000":
                symbol = check_balance["symbol"]
                quantity = check_balance["positionAmt"]
                openPrice = check_balance["entryPrice"]
                leverage = check_balance["leverage"]
                profit = check_balance["unRealizedProfit"]
                print("Long", symbol, "current quantity:", quantity)
                print("Position opened at", openPrice)
                print("Leverage:", leverage)
                print("Unrealized profit/loss", profit)
                return True
            else:
                return False

    #'positionAmt': '0.000'
    # [{'symbol': 'BTCUSDT', 'positionAmt': '0.000', 'entryPrice': '0.0', 'markPrice': '19172.50000000', 'unRealizedProfit': '0.00000000', 'liquidationPrice': '0', 'leverage': '1', 'maxNotionalValue': '9.223372036854776E18', 'marginType': 'isolated', 'isolatedMargin': '0.00000000', 'isAutoAddMargin': 'false', 'positionSide': 'BOTH', 'notional': '0', 'isolatedWallet': '0', 'updateTime': 1666216921737}]


def position_information_hedge():
    position_information = client.futures_position_information(symbol="BTCUSDT")
    print(position_information)


def recent_trades():
    recent_trades = client.futures_recent_trades(symbol="BTCUSDT")
    return recent_trades
    # print(recent_trades()) #POGLEJ KAJ POKAZE,Tega nerabimo ker kaže use trade ne samo tvoje, mejbi lahko pokaze navjecji trade  {'id': 2952634293, 'price': '19411.10', 'qty': '0.030', 'quoteQty': '582.33', 'time': 1665688382262, 'isBuyerMaker': False}]


def historical_trades():
    b = client.futures_historical_trades(symbol="BTCUSDT")
    print(b)


def get_asset():
    get_asset = client.get_asset_balance(asset="USDT")


def income_history():
    a = client.futures_income_history()
    print(a)


def on_open(ws):
    print("opened connection")


def on_close(ws, close_status_code, close_msg):
    print("closed connection")


def on_message(ws, message):

    # Reference to closes, highs, lows, opens
    global closes
    global highs
    global lows
    global opens
    global h_opens
    global h_closes
    global h_highs
    global h_lows

    # References to supertrend
    global true_range
    global atrs
    global atr_rma
    global lower_band
    global upper_band
    global final_upper_band
    global final_lower_band
    global supertrend

    # References to supertrend2
    global atrs2
    global atr_rma2
    global lower_band2
    global upper_band2
    global final_upper_band2
    global final_lower_band2
    global supertrend2
    global pandas_rma

    global sells
    global buys
    global start_time

    # References to short and long signals strategy
    global long
    global short
    global in_position_long
    global in_position_short

    # print("received message")
    # print("CANDLESTICK:")
    json_message = json.loads(message)
    # pprint.pprint(json_message) #<-- this outputs whole raw json message

    time = json_message["E"]
    timestamp = int(float(time)) / 1000

    candle = json_message["k"]

    is_candle_closed = candle["x"]
    close = candle["c"]
    open = candle["o"]
    high = candle["h"]
    low = candle["l"]
    c = float(close)
    o = float(open)
    h = float(high)
    l = float(low)

    # Heikin ashi close calculator
    h_closed = (c + o + h + l) / 4

    # IF WE WANT TO SEE EACH TICKER INFORMATION (Not only when it closes)
    # print("Price: ", close)
    # print("Opened:", open)
    # print("High:  ", high)
    # print("Low:   ", low)
    # print("---------------------")

    # NORMAL CANDLESTICKS
    if is_candle_closed:
        # candle_time2 = datetime.fromtimestamp(timestamp)
        # print("The candle closed at {}".format(candle_time2))
        # print("the last candle opened at {}".format(open))
        # print("candle closed at {}".format(close))
        # print("the highest point was {}".format(high))
        # print("the lowest point was {}".format(low))
        closes.append(float(close))
        highs.append(float(high))
        lows.append(float(low))
        opens.append(float(open))
        # print("Opens:")
        # print(opens)
        # print("Closes:")
        # print(closes)
        # print("Highs:")
        # print(highs)
        # print("Lows:")
        # print(lows)
        # print("------------------------------------------")

    # START TIME
    if len(closes) == 1:
        start_time = datetime.fromtimestamp(timestamp)

    # FIRST HEIKIN ASHI
    if len(closes) == 2:  # needs to be 2

        candle_time_h = datetime.fromtimestamp(timestamp)
        c_opens = numpy.array(opens)
        c_closes = numpy.array(closes)
        h_opened = (c_closes[-2] + c_opens[-2]) / 2

        if is_candle_closed:
            print("The candle closed at {}".format(candle_time_h))
            print("the heikin ashi candle opened at {}".format(h_opened))
            print("the heikin ashi candle closed at {}".format(h_closed))
            h_opens.append(float(h_opened))
            h_closes.append(float(h_closed))
            h_highs.append(float(h))
            h_lows.append(float(l))
            print("PRVI heikin ashi:")
            print("Opens:")
            print(h_opens)
            print("Closes:")
            print(h_closes)
            print("------------------------------------------")

    # HEIKIN ASHI
    if len(closes) >= 3:  # needs to be 3
        candle_time_ha = datetime.fromtimestamp(timestamp)

        if is_candle_closed:
            h_o = float(h_opens[-1])
            h_c = float(h_closes[-1])
            ha_opened = (h_o + h_c) / 2
            ha_closed = h_closed
            ha_high = max(ha_opened, ha_closed, h)
            ha_low = min(ha_opened, ha_closed, l)
            h_opens.append(float(ha_opened))
            h_closes.append(float(ha_closed))
            h_highs.append(float(ha_high))
            h_lows.append(float(ha_low))
            candle_number = len(h_closes)
            print("This is heikin ashi candle number:", candle_number)
            print("The candle closed at {}".format(candle_time_ha))

            # HEIKIN ASHI PRINT ONLY TO 20
            if len(h_closes) <= 20:
                print("the heikin ashi candle opened at {}".format(ha_opened))
                print("the heikin ashi candle closed at {}".format(ha_closed))
                print("Heikin ashi calculations")
                print("Heikin ashi opens:")
                print(h_opens)
                print("Heikin ashi closes:")
                print(h_closes)
                print("Heikin ashi highs:")
                print(h_highs)
                print("Heikin ashi lows:")
                print(h_lows)
                print("------------------------------------------")

            # TRUE RANGE
            if len(h_closes) > 10:
                tr = max(
                    abs(ha_high - ha_low),
                    abs(ha_high - h_closes[-1]),
                    abs(ha_low - h_closes[-1]),
                )
                true_range.append(float(tr))

                if len(h_closes) < 20:
                    print("True range:")
                    print(true_range)
                    print("------------------------------------------")

            # FIRST RMA ATR PERIOD 10
            if len(true_range) == 10:
                first_atr_rma = sum(true_range) / 10
                atr_rma.append(float(first_atr_rma))
                print("This is the first atr:")
                print(atr_rma)
                print("------------------------------------------")

            # VSI NASLEDNJI PERIODI 10
            if len(true_range) > 10:
                atr_rma_value = ((1 / 10) * true_range[-1]) + (
                    (1 - 1 / 10) * atr_rma[-1]
                )
                atr_rma.append(float(atr_rma_value))

                if len(supertrend2) < 1:
                    print("This is last 10 atrs:")
                    print(atr_rma[-10:])
                    print("------------------------------------------")

            # PANDAS RMA
            if len(true_range) > 20:

                df = numpy.array(true_range)
                d = pd.Series(df)
                c = pd.DataFrame(df)
                pandas_r = d.rolling(10).mean()
                pandas_nr = numpy.array(pandas_r)
                pandas_c = ta.rma(d, ATR_PERIOD)
                pandas_nc = numpy.array(pandas_c)
                # print("To so vsi pandas rmaji:")
                # print(pandas_nr[-10:])
                # print("To je zadnji pandas rma:")
                # print(pandas_nr[-1])
                # print("To je pandas ta rma:")
                # print(pandas_nc[-10:])
                # print("------------------------------------------")

            # EMA TRUE RANGE
            if len(true_range) > ATR_PERIOD:
                tr_closes = numpy.array(true_range)
                atr_ema = talib.EMA(tr_closes, ATR_PERIOD)

                # if len(h_closes) < 30:
                # print("ATR EMA IN TALIB:")
                # print(atr_ema)
                # print("------------------------------------------")

            # UPPER AND LOWER BAND
            if len(h_closes) > 25:  # NEEDS TO BE 25
                last_rma = float(atr_rma[-1])
                last_atr = float(atr_ema[-1])
                hl_average = (ha_high + ha_low) / 2
                upper_value = hl_average + (MULTIPLIER * last_rma)
                lower_value = hl_average - (MULTIPLIER * last_rma)
                upper_band.append(float(upper_value))
                lower_band.append(float(lower_value))

                if len(upper_band) < 10:
                    print("zadnji atr je:", last_rma)
                    print("Zgornji bandi:")
                    print(upper_band)
                    print("Spodnji bandi:")
                    print(lower_band)
                    print("------------------------------------------")

                # FIRST FINAL UPPER AND LOWER BAND
                if len(upper_band) == 2:  # NEEDS TO BE 2
                    final_upper_band.append(float(upper_band[-1]))
                    final_lower_band.append(float(lower_band[-1]))
                    print("prvi upper band je:", final_upper_band)
                    print("prvi lower band je:", final_lower_band)
                    print("------------------------------------------")

                # FINAL UPPER BAND
                if len(upper_band) >= 3:  # NEEDS TO BE 3
                    f_u_p = float(final_upper_band[-1])
                    previous_close = float(h_closes[-2])

                    if upper_value < f_u_p or previous_close > f_u_p:
                        final_upper_band.append(upper_band[-1])

                        if len(upper_band) < 15:
                            print("These are final_upper_bands till now:")
                            print(final_upper_band)
                            print("------------------------------------------")

                    else:
                        nov_value_h = final_upper_band[-1]
                        final_upper_band.append(nov_value_h)

                        if len(upper_band) < 15:
                            print("These are final_upper_bands till now:")
                            print(final_upper_band)
                            print("------------------------------------------")

                # FINAL LOWER BAND
                if len(lower_band) >= 3:  # NEEDS TO BE 3
                    f_l_p = float(final_lower_band[-1])
                    previous_close = float(h_closes[-2])

                    if lower_value > f_l_p or previous_close < f_l_p:
                        final_lower_band.append(lower_band[-1])

                        if len(lower_band) < 15:
                            print("These are final_lower_bands till now:")
                            print(final_lower_band)
                            print("------------------------------------------")

                    else:
                        nov_value_l = final_lower_band[-1]
                        final_lower_band.append(nov_value_l)

                        if len(lower_band) < 15:
                            print("These are final_lower_bands till now:")
                            print(final_lower_band)
                            print("------------------------------------------")

                # FIRST SUPERTREND
                if len(final_lower_band) == 2:

                    if h_closes[-1] <= final_upper_band[-1]:
                        supertrend_one = final_upper_band[-1]
                        supertrend.append(float(supertrend_one))
                        print("First super trend:")
                        print(supertrend)
                        print("------------------------------------------")

                    else:
                        supertrend_one = final_lower_band[-1]
                        supertrend.append(float(supertrend_one))
                        print("First super trend:")
                        print(supertrend)
                        print("------------------------------------------")

                # SUPERTREND
                if len(final_lower_band) > 2:
                    previous_supertrend = float(supertrend[-1])
                    previous_final_upper = float(final_upper_band[-2])
                    previous_final_lower = float(final_lower_band[-2])
                    current_close = float(h_closes[-1])
                    current_final_lower = float(final_lower_band[-1])
                    current_final_upper = float(final_upper_band[-1])

                    if (
                        previous_supertrend == previous_final_upper
                        and current_close < current_final_upper
                    ):
                        supertrend.append(float(final_upper_band[-1]))
                        # print("Currently it is final upper band")

                    elif (
                        previous_supertrend == previous_final_upper
                        and current_close > current_final_upper
                    ):
                        supertrend.append(float(final_lower_band[-1]))
                        # print("Currently it is final lower band")

                    elif (
                        previous_supertrend == previous_final_lower
                        and current_close > current_final_lower
                    ):
                        supertrend.append(float(final_lower_band[-1]))
                        # print("Currently it is final lower band")

                    elif (
                        previous_supertrend == previous_final_lower
                        and current_close < current_final_lower
                    ):
                        supertrend.append(float(final_upper_band[-1]))
                        # print("Currently it is final upper band")

                    # if len(supertrend) < 10:
                    # print("All supertrends:")
                    # print(supertrend)
                    # print("------------------------------------------")

                    # if len(supertrend) >= 10 and len(supertrend2) <= 40:
                    # print("Last 10 supertrends with atr 10:")
                    # print(supertrend[-10:])
                    # print("------------------------------------------")

                    # print("Amount of supertrends till now with atr 10:")
                    # print(len(supertrend))

                    # if len(buys) >= 1:
                    # print("Buys on atr 10 were:")
                    # print(buys)

                    # if len(sells) >= 1:
                    # print("Sells on atr 10 were:")
                    # print(sells)
                    # print("")

                # Buy and sell signals
                if len(supertrend) > 1:

                    if (
                        supertrend[-1] == final_upper_band[-1]
                        and supertrend[-2] == final_lower_band[-2]
                    ):
                        sells.append(candle_time_ha)
                        # print("------------------------------------------")
                        # print("SELL SIGNAL")
                        # print("AT: {}".format(candle_time_ha))
                        # print("------------------------------------------")

                    if (
                        supertrend[-1] == final_lower_band[-1]
                        and supertrend[-2] == final_upper_band[-2]
                    ):
                        buys.append(candle_time_ha)
                        # print("------------------------------------------")
                        # print("BUY SIGNAL")
                        # print("AT: {}".format(candle_time_ha))
                        # print("------------------------------------------")

                # ---------------------------------------------------------------------------#

                # FIRST RMA ATR PERIOD 20
                if len(true_range) == 20:
                    first_atr_rma2 = sum(true_range) / 20
                    atr_rma2.append(float(first_atr_rma2))
                    print("This is first rma2 atr:")
                    print(atr_rma2)
                    print("------------------------------------------")

                # ALL NEXT PERIODI 20
                if len(true_range) > 20:
                    atr_rma_value2 = ((1 / 20) * true_range[-1]) + (
                        (1 - 1 / 20) * atr_rma2[-1]
                    )
                    atr_rma2.append(float(atr_rma_value2))

                    if len(supertrend2) < 1:
                        print("This is first rma2 atrjov:")
                        print(atr_rma2[-10:])
                        print("------------------------------------------")

                # UPPER AND LOWER BAND
                if len(h_closes) > 35:  # NEEDS TO BE 35
                    last_rma2 = float(atr_rma2[-1])
                    hl_average2 = (ha_high + ha_low) / 2
                    upper_value2 = hl_average2 + (MULTIPLIER2 * last_rma2)
                    lower_value2 = hl_average2 - (MULTIPLIER2 * last_rma2)
                    upper_band2.append(float(upper_value2))
                    lower_band2.append(float(lower_value2))

                    if len(upper_band2) < 10:
                        print("Last atr2 is:", last_rma2)
                        print("Upper bands2:")
                        print(upper_band2)
                        print("Lower bands2:")
                        print(lower_band2)
                        print("------------------------------------------")

                # FIRST FINAL UPPER AND LOWER BAND
                if len(upper_band2) == 2:  # NEEDS TO BE 2
                    final_upper_band2.append(float(upper_band2[-1]))
                    final_lower_band2.append(float(lower_band2[-1]))
                    print("first upper band2 is:", final_upper_band2)
                    print("first lower band2 is:", final_lower_band2)
                    print("------------------------------------------")

                # FINAL UPPER BAND
                if len(upper_band2) >= 3:  # NEEDS TO BE 3
                    f_u_p2 = float(final_upper_band2[-1])
                    previous_close2 = float(h_closes[-2])

                    if upper_value2 < f_u_p2 or previous_close2 > f_u_p2:
                        final_upper_band2.append(upper_band2[-1])

                        if len(upper_band2) < 15:
                            print("These are final upper bands 2 till now:")
                            print(final_upper_band2)
                            print("------------------------------------------")

                    else:
                        nov_value_h2 = final_upper_band2[-1]
                        final_upper_band2.append(nov_value_h2)

                        if len(upper_band2) < 15:
                            print("These are final upper bands 2 till now:")
                            print(final_upper_band2)
                            print("------------------------------------------")

                # FINAL LOWER BAND
                if len(lower_band2) >= 3:  # NEEDS TO BE 3
                    f_l_p2 = float(final_lower_band2[-1])
                    previous_close2 = float(h_closes[-2])

                    if lower_value2 > f_l_p2 or previous_close2 < f_l_p2:
                        final_lower_band2.append(lower_band2[-1])

                        if len(lower_band2) < 15:
                            print("These are final lower bands 2 till now:")
                            print(final_lower_band2)
                            print("------------------------------------------")

                    else:
                        nov_value_l2 = final_lower_band2[-1]
                        final_lower_band2.append(nov_value_l2)

                        if len(lower_band2) < 15:
                            print("These are final lower bands 2 till now:")
                            print(final_lower_band2)
                            print("------------------------------------------")

                # FIRST SUPERTREND
                if len(final_lower_band2) == 2:

                    if h_closes[-1] <= final_upper_band2[-1]:
                        supertrend_one2 = final_upper_band2[-1]
                        supertrend2.append(float(supertrend_one2))
                        print("FIRST SUPER TREND2:")
                        print(supertrend2)
                        print("------------------------------------------")

                    else:
                        supertrend_one2 = final_lower_band2[-1]
                        supertrend2.append(float(supertrend_one2))
                        print("FIRST SUPER TREND2:")
                        print(supertrend2)
                        print("------------------------------------------")

                # SUPERTREND
                if len(final_lower_band2) > 2:
                    previous_supertrend2 = float(supertrend2[-1])
                    previous_final_upper2 = float(final_upper_band2[-2])
                    previous_final_lower2 = float(final_lower_band2[-2])
                    current_close2 = float(h_closes[-1])
                    current_final_lower2 = float(final_lower_band2[-1])
                    current_final_upper2 = float(final_upper_band2[-1])

                    if (
                        previous_supertrend2 == previous_final_upper2
                        and current_close2 < current_final_upper2
                    ):
                        supertrend2.append(float(final_upper_band2[-1]))
                        # print("CURRENTLY IS FINAL UPPER BAND2")

                    elif (
                        previous_supertrend2 == previous_final_upper2
                        and current_close2 > current_final_upper2
                    ):
                        supertrend2.append(float(final_lower_band2[-1]))
                        # print("CURRENTLY IS LOWER UPPER BAND2")

                    elif (
                        previous_supertrend2 == previous_final_lower2
                        and current_close2 > current_final_lower2
                    ):
                        supertrend2.append(float(final_lower_band2[-1]))
                        # print("CURRENTLY IS LOWER UPPER BAND2")

                    elif (
                        previous_supertrend2 == previous_final_lower2
                        and current_close2 < current_final_lower2
                    ):
                        supertrend2.append(float(final_upper_band2[-1]))
                        # print("CURRENTLY IS FINAL UPPER BAND2")

                    # if len(supertrend2) < 10:
                    # print("All supertrends2 till now:")
                    # print(supertrend2)
                    # print("------------------------------------------")

                    # if len(supertrend2) >= 10 and len(supertrend2) <= 40:
                    # print("Last 10 supertrends2:")
                    # print(supertrend2[-10:])
                    # print("------------------------------------------")

                    # print("Amount of supertrends2 with atr 20:")
                    # print(len(supertrend2))

                    # if len(buys2) >= 1:
                    # print("Buys with 20 atr:")
                    # print(buys2)

                    # if len(sells2) >= 1:
                    # print("Sells with 20 atr:")
                    # print(sells2)
                    # print("")

                # Buy and sell signals
                if len(supertrend2) > 1:

                    if (
                        supertrend2[-1] == final_upper_band2[-1]
                        and supertrend2[-2] == final_lower_band2[-2]
                    ):
                        sells2.append(candle_time_ha)
                        # print("------------------------------------------")
                        # print("SELL2 SIGNAL")
                        # print("AT: {}".format(candle_time_ha))
                        # print("------------------------------------------")

                    if (
                        supertrend2[-1] == final_lower_band2[-1]
                        and supertrend2[-2] == final_upper_band2[-2]
                    ):
                        buys2.append(candle_time_ha)
                        # print("------------------------------------------")
                        # print("BUY2 SIGNAL")
                        # print("AT: {}".format(candle_time_ha))
                        # print("------------------------------------------")

                ########################

                # BINANCE PART
                # TP AND SL CALCULATIONS
                # SHORT
                tpS = round(float(h_closes[-1]) * 0.99, 2)
                slS = round(float(h_closes[-1]) * 1.01, 2)

                # LONG
                tpL = round(float(h_closes[-1]) * 1.01, 2)
                slL = round(float(h_closes[-1]) * 0.99, 2)

                # POSITION SIZE
                change_leverage()
                position = float(get_balance()) * 0.21
                position_size = (position / closes[-1]) * LEVERAGE

                ########################

                # STRATEGY LONG AND SHORT
                if len(supertrend2) >= 1:

                    if (
                        supertrend2[-1] == final_lower_band2[-1]
                        and supertrend[-1] == final_lower_band[-1]
                        and supertrend[-2] == final_upper_band[-2]
                    ):
                        if position_information_long() == True:
                            print(
                                "Nothing to do, you are already in a long position..."
                            )

                        else:
                            long.append(candle_time_ha)
                            print("LONG SIGNAL at", candle_time_ha)
                            # Put long here
                            cancel_all_orders_long()
                            order_long(position_size, tpL, slL)

                    if (
                        supertrend2[-1] == final_upper_band2[-1]
                        and supertrend[-1] == final_upper_band[-1]
                        and supertrend[-2] == final_lower_band[-2]
                    ):
                        if position_information_short() == True:
                            print(
                                "Nothing to do, you are already in a short position..."
                            )

                        else:
                            short.append(candle_time_ha)
                            print("SHORT SIGNAL at", candle_time_ha)
                            # Put short here
                            cancel_all_orders_short()
                            order_short(position_size, slS, tpS)

                # OUTPUT OF STRATEGY
                print("Algorith started at:", start_time)
                print("")
                print("ALL LONG AND SHORTS TILL NOW:")
                print("LONGS(last 5):")
                print(long[-5:])
                print("SHORTS(last 5):")
                print(short[-5:])
                print("")
                print("- - - - - - - -")
                print("BINANCE OUTPUT")
                print("Current balance in usdt: ", get_balance())
                position_information_short()
                position_information_long()
                get_orders()
                print("//////////////////////////////////////////////////")

                # BINANCE API CALLS
                # Client.futures_change_leverage(symbol="BTCUSDT", leverage=LEVERAGE)
                # balance = Client.get_margin_asset(asset='USDT')
                # orders = Client.get_open_margin_orders(symbol='ethusdt')
                # all_orders = Client.get_all_margin_orders(symbol='BNBBTC', limit=10)

                # BINANCE PYTHON-API OUTPUT
                # print("CURRENT BALANCE(usdt):")
                # print(balance)
                # print("ALL OPEN ORDERS:")
                # print(orders)
                # print(all_orders)
                # print("------------------------------------------")


def on_error(ws, error):
    print(error)


ws = websocket.WebSocketApp(
    SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error
)

ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
