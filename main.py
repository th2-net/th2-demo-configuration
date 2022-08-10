from __future__ import print_function

import contextlib
import datetime
import logging
import os
from pathlib import Path
import pickle
import subprocess
import time
from typing import Any

from custom.support_functions import create_connection
from scenarios.AggressiveIOC_Traded_against_TwoOrders_partially_and_Cancelled.scenario import scenario


def create_logs_dir(path: Path) -> None:
    with contextlib.suppress(FileExistsError):
        os.mkdir(path)


def dump_data(filename: str, data: Any):
    path = Path('scenarios/data_services') / filename
    with open(path, 'wb') as file:
        pickle.dump(data, file)


if __name__ == '__main__':
    logs_path = Path('logs/')
    create_logs_dir(logs_path)
    logging.basicConfig(filename=logs_path / f'{time.asctime().replace(":", "-")} script.log',
                        level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()

    # Creation of grpc channels and instances of act, check1 and estore stubs.
    connection = create_connection(Path('./configs'))

    try:
        start_datetime = datetime.datetime.utcnow()
        scenario(connection, scenario_id=1)
        finish_datetime = datetime.datetime.utcnow()

    finally:
        connection.close()

    logger.info(f'start datetime: {start_datetime}')
    logger.info(f'finish datetime: {finish_datetime}')

    logger.info('Data Services - start')
    dump_data(filename='start_datetime.pickle', data=start_datetime)
    dump_data(filename='finish_datetime.pickle', data=finish_datetime)

    with subprocess.Popen('["jupyter", "notebook", "scenarios/data_services/notebook.ipynb"]') as p:
        x = None
        time.sleep(10)
        while x not in ['Y', 'y']:
            x = input('Enter Y/y to close DataServices and finish demo script: ')
        p.kill()
