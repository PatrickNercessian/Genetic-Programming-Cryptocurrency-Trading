import helper
from tree import *

from binance.client import Client
import time
import multiprocessing
import traceback
import numpy

TIMEOUT = 0.5  # seconds


class Individual:
    def __init__(self, tree: Tree, crypto_symbol: str, interval: str):
        self.tree = tree
        self.crypto_symbol = crypto_symbol

        self.interval = interval
        self.interval_in_min = helper.get_interval_in_min(interval)

        self.code = decode_in_order(self.tree.root)
        self.fitness = 0  # AKA how much money we ended up with

    def evaluate(self, df_list):  # TODO penalize bloated trees
        print('\n' + self.code + '\n')

        confidence_vals = []
        sum_balances = 0

        for df in df_list:
            coins_owned = 0.0
            usd_owned = 1000.00  # starting balance

            window_start_index = 34  # Start when signal and histogram are no longer NaN (26 + 9)
            window_end_index = 54  # 20 rows at a time (for 3m intervals, this is a 60min window)
            df_window = df.iloc[window_start_index:window_end_index]  # only here to initialize df_window out of 'while'

            while window_end_index < len(df):
                window_start_index += 1
                window_end_index += 1
                df_window = df.iloc[window_start_index:window_end_index]
                return_dict = self.run_code(df_window)

                if return_dict['exception_occurred']:
                    print('Exception occurred... Fitness defaulted to 0.')
                    return 0

                confidence_vals.append(return_dict['confidence'])
                coins_owned, usd_owned = update_holdings(coins_owned, usd_owned,
                                                         return_dict['confidence'], df_window.close[-1])

            portfolio_balance = (coins_owned * df_window.close[-1]) + usd_owned

            print("Total Portfolio Balance in USD: $", portfolio_balance)
            print("Holdings:", '$' + str(usd_owned) + ',', str(coins_owned) + self.crypto_symbol)

            sum_balances += portfolio_balance

        # stdev = statistics.stdev(confidence_vals)
        # fitness = sum_balances * (1 + stdev) / len(df_list)

        # 2/10 distinct vals: 1.01       3/10 distinct: 1.02       4/10 distinct: 1.03...   ...10/10 distinct: 1.09
        # multiplier = 1 + (len(set(confidence_vals))-1) / pow(len(confidence_vals), 2)

        multiplier = 1.0
        if len(set(confidence_vals)) > 1:
            multiplier = 1.2
        fitness = sum_balances * multiplier / len(df_list)
        print('Fitness:', fitness)
        # print("Standard Deviation:", stdev)
        return fitness

    def run_code(self, df_window):
        recent_rsi = df_window.rsi[-1]

        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        # TODO give entire dataframe, not just recent RSI
        # return_dict.update({'recent_rsi': recent_rsi, 'should_buy': None, 'stop_loss': 0.0,
        #                     'confidence': 1.0, 'exception_occurred': False})
        return_dict.update({'recent_rsi': recent_rsi, 'confidence': 1.0, 'exception_occurred': False})

        # pre_process_start_time = time.time()
        process = multiprocessing.Process(target=thread_run, args=(self.code, return_dict))
        process.start()
        process_start_time = time.time()
        # print("Creating and starting Process took", pre_process_start_time - process_start_time, 'seconds')

        while process.is_alive():
            if time.time() - process_start_time > TIMEOUT:
                process.terminate()
                print('Code timed out...')
                return_dict['exception_occurred'] = True
            time.sleep(0.001)  # TODO this may be slowing down evaluation

        # print('Completing Process took', process_start_time - time.time(), 'seconds')

        if return_dict['confidence'] is None:
            return_dict['confidence'] = 0.0
        elif isinstance(return_dict['confidence'], numpy.bool_):
            return_dict['confidence'] = max(min(float(return_dict['confidence']), 1.0), 0.0)
        else:
            return_dict['confidence'] = max(min(return_dict['confidence'], 1.0), 0.0)

        return return_dict


def thread_run(code, return_dict):
    env = dict(return_dict)  # Because return_dict is some dict wrapper from manager.dict()

    try:
        exec(code, env)
        return_dict.update(env)
        del return_dict['__builtins__']
    except:
        print(traceback.print_exc())
        return_dict['exception_occurred'] = True


def update_holdings(coins_owned, usd_owned, confidence, closing_price):
    coins_owned_usd = coins_owned * closing_price
    desired_usd_investment = (usd_owned + coins_owned_usd) * confidence

    difference_usd = coins_owned_usd - desired_usd_investment
    difference_coins = - difference_usd / closing_price
    coins_owned += difference_coins
    usd_owned += difference_usd

    return coins_owned, usd_owned
