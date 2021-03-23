import helper
from tree import *

from binance.client import Client
import time
import multiprocessing
import traceback

TIMEOUT = 3  # seconds


class Individual:
    def __init__(self, tree: Tree, crypto_symbol: str, interval: str):
        self.tree = tree
        self.crypto_symbol = crypto_symbol

        self.interval = interval
        self.interval_in_min = helper.get_interval_in_min(interval)

        self.code = decode_in_order(self.tree.root)
        self.fitness = 0  # AKA how much money we ended up with

    def evaluate(self, df):  # TODO penalize bloated trees
        print('\n' + self.code + '\n')
        balance = 1000.00  # starting balance

        window_start_index = 35  # Start when signal and histogram are no longer NaN (26 + 9)
        window_end_index = 55  # 20 rows at at time (for 3m intervals, this is a 60min window)

        df_window = df.iloc[window_start_index:window_end_index]

        return_dict = self.run_code(df_window)

        if return_dict['exception_occurred']:
            print('Exception occurred... Fitness defaulted to 0.')
            return 0

        if return_dict['should_buy'] is None:# or return_dict['confidence'] is None or return_dict['stop_loss'] is None:
            print("Didn't make a decision")
            return balance / 2

        if return_dict['should_buy'] and return_dict['confidence'] > 0:
            dollars_to_spend = balance * return_dict['confidence']
            balance -= dollars_to_spend
            amount_owned = dollars_to_spend / df_window.close[-1]
            print('Bought', amount_owned, self.crypto_symbol, 'for $' + str(dollars_to_spend))

            original_stop_loss = return_dict['stop_loss']

            while return_dict['should_buy'] and window_end_index < len(df):
                # print('Holding...', str(return_dict))
                window_start_index += 1
                window_end_index += 1
                df_window = df.iloc[window_start_index:window_end_index]
                return_dict = self.run_code(df_window)

                if return_dict['exception_occurred']:
                    print('Exception occurred... Fitness defaulted to 0.')
                    return 0

                if df_window.close[-1] < original_stop_loss:
                    print('Stop Loss at (' + str(original_stop_loss) + ') triggered')
                    break

            dollars_to_receive = amount_owned * df_window.close[-1]
            print('Sold', amount_owned, self.crypto_symbol, 'for $' + str(dollars_to_receive))
            balance += amount_owned * df_window.close[-1]
        else:
            print('Did not buy.')

        return balance

    def run_code(self, df_window):
        recent_rsi = df_window.rsi[-1]
        should_buy, stop_loss, confidence = True, 0.0, 1.0

        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        # TODO give entire dataframe, not just recent RSI
        return_dict.update({'recent_rsi': recent_rsi, 'should_buy': None, 'stop_loss': 0.0,
                            'confidence': 1.0, 'exception_occurred': False})

        process = multiprocessing.Process(target=thread_run, args=(self.code, return_dict))
        process.start()
        process_start_time = time.time()

        while process.is_alive():
            if time.time() - process_start_time > TIMEOUT:
                process.terminate()
                print('Code timed out...')
                return_dict['exception_occurred'] = True
            time.sleep(0.01)  # TODO this may be slowing down evaluation

        if return_dict['confidence'] is None:
            return_dict['confidence'] = 1.0
        else:
            return_dict['confidence'] = max(min(return_dict['confidence'], 1.0), 0.0)

        if return_dict['stop_loss'] is None:
            return_dict['stop_loss'] = 0.0

        return return_dict


def thread_run(code, return_dict):
    env = dict(return_dict)  # Because return_dict is some dict wrapper from manager.dict()

    try:
        # print('pre env', env)
        exec(code, env)
        # print('post env', env)
        return_dict.update(env)
        del return_dict['__builtins__']
    except:
        print(traceback.print_exc())
        return_dict['exception_occurred'] = True
