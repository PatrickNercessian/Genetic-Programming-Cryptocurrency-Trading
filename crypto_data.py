from typing import Union

import btalib
import pandas as pd

import datetime
import time
import random
import traceback

from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

import helper

HOUR_IN_MS = 60 * 60 * 1000
DAY_IN_MS = 24 * 60 * 60 * 1000


def setup_real_client():
    # confirm = input("THIS IS FOR REAL ACCOUNT TRADING. PLEASE CONFIRM THAT USING REAL BINANCE ACCOUNT IS INTENDED(Y/N)")
    # if confirm.lower() != 'yes':
    #     return

    # Only use this for real trading!
    api_key = '58gcz5jVNsWkFkOPW8waOSuREYRCwqoWajauyP9pk2EV2hlXzoYgZDhUtLOW2TSr'
    api_secret = 'gnygNoB3VSWiO4z2uo72onzVgOZQX0QrchNtefMj0tgY6FYS2HW5Sqq3114X0rsz'

    # Issue with syncing pycharm and system environments
    # api_key = os.environ.get('binance_api')
    # api_secret = os.environ.get('binance_secret')

    c = Client(api_key, api_secret)

    # API URL for real trading
    c.API_URL = 'https://api.binance.us/api'

    return c


def setup_testing_client():
    # Demo account keys
    api_key = 'LOl1MfZUlVcg7d7glYaHqybp2CmttFrvTqTDFcXWUlkEYx5aNTrVJ7odsPUtFWAM'
    api_secret = 'toJXbhZdhui7oVVLEUPsQOAQhmbWRRRKq0eEg7B6hbi3fr74o2VWk0f9G2EtXyzP'

    c = Client(api_key, api_secret)
    c.API_URL = 'https://testnet.binance.vision/api'

    return c


def get_crypto_data_online(csv_file: str, c: Client, symbol: str, interval: str, start: Union[str, int], end: Union[str, int] = None):
    # request historical candle (klines) data
    bars = c.get_historical_klines(symbol, interval, start_str=start, end_str=end)

    # Only use the first 5 columns, listed in pd.DataFrame call
    for line in bars:
        del line[5:]
    df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])

    df.set_index('date', inplace=True)  # Sets the date column AS the row index (rather than 0, 1, 2, 3, etc.)
    df.to_csv(csv_file)  # Need to save to CSV and load from CSV for some damn reason

    csv_df = get_crypto_data_csv(csv_file)

    return csv_df


def get_all_crypto_data_online(csv_file: str, symbol: str, interval: str):
    client = setup_real_client()
    earliest_time = client._get_earliest_valid_timestamp(symbol, interval)  # interval e.g. '3m'

    return get_crypto_data_online(csv_file, client, symbol, interval, earliest_time)


def get_crypto_data_csv(csv_file: str):
    # Just for printing settings
    pd.set_option('display.width', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 6)

    csv_df = pd.read_csv(csv_file, index_col=0)
    csv_df.index = pd.to_datetime(csv_df.index, unit='ms')

    # split_date = datetime.datetime(2020, 4, 27)
    # print(csv_df.loc[csv_df.index <= split_date])

    # Convert Strings to Floats
    csv_df['open'] = pd.to_numeric(csv_df.open)
    csv_df['high'] = pd.to_numeric(csv_df.high)
    csv_df['low'] = pd.to_numeric(csv_df.low)
    csv_df['close'] = pd.to_numeric(csv_df.close)

    return csv_df


def get_random_df(crypto_symbol, interval):
    try:
        client = setup_real_client()
        earliest_time = client._get_earliest_valid_timestamp(crypto_symbol, interval)

        data_start_time = random.randint(
            earliest_time + (2 * DAY_IN_MS),  # Ignore first 2 days as they're wonky
            int(time.time() * 1000) - (30 * DAY_IN_MS)  # Ignore last month so that we can test on it later
        )
        data_end_time = data_start_time + (65 * helper.get_interval_in_min(interval) * 60 * 1000)  # 65 total rows

        df = None
        while df is None or df.size <= 0:
            df = add_indicators(
                get_crypto_data_online('btc_bars.csv', client, crypto_symbol, interval, data_start_time, data_end_time)
            )
        print(df)
        return df
    except:
        print(traceback.print_exc())
        # Definite possibility for infinite recursion, but no solution to that
        return get_random_df(crypto_symbol, interval)


def add_indicators(csv_df: pd.DataFrame):

    # # noinspection PyArgumentList
    # sma = btalib.sma(csv_df, period=5)
    # # noinspection PyArgumentList
    # ema = btalib.ema(csv_df, period=5)
    # # noinspection PyArgumentList
    # rsi = btalib.rsi(csv_df, period=5)
    # # noinspection PyArgumentList
    # macd = btalib.macd(csv_df, pfast=20, pslow=50, psignal=13)

    # noinspection PyArgumentList
    sma = btalib.sma(csv_df)
    # noinspection PyArgumentList
    ema = btalib.ema(csv_df)
    # noinspection PyArgumentList
    rsi = btalib.rsi(csv_df)
    # noinspection PyArgumentList
    macd = btalib.macd(csv_df)

    # add to DataFrame
    csv_df = csv_df.join([sma.df, ema.df, rsi.df, macd.df])
    return csv_df
