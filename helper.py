import os

def get_interval_in_min(interval: str):
    if interval.endswith('m'):
        return int(interval[:-1])
    elif interval.endswith('h'):
        return int(interval[:-1]) * 60
    elif interval.endswith('d'):
        return int(interval[:-1]) * 60 * 24
    else:
        raise ValueError('interval does not end in m, h, or d')


def create_run_folder():
    directory_name = 'run_1'
    directory_count = 1

    while os.path.isdir(directory_name):
        directory_count += 1
        directory_name = 'run_' + str(directory_count)

    os.mkdir(directory_name)
    return directory_name
