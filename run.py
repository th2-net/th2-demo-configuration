from __future__ import print_function

import datetime
import logging
import time

import yaml
from google.protobuf.timestamp_pb2 import Timestamp
from th2_grpc_common.common_pb2 import EventBatch

from custom import support_functions as sf

# IMPORT REFDATA FROM FILES
with open('configs/instruments.refdata') as f:
    instruments = yaml.load(f, Loader=yaml.FullLoader)
with open('configs/firms.refdata') as f:
    firms = yaml.load(f, Loader=yaml.FullLoader)


def scenario(factory):
    # Storing grpc Timestamp of script start.
    report_start_timestamp = Timestamp()
    report_start_timestamp.GetCurrentTime()

    # Sending request to estore. Creation of the root Event for all cases performed.

    # CASE 1
    parent_id = sf.create_event_id()

    sf.send_child(
        factory=factory,
        event_id=sf.create_event_id(),
        parent_id=parent_id,
        start_timestamp=report_start_timestamp,
        status='FAILED')

    sf.send_parent(
        factory=factory,
        start_timestamp=report_start_timestamp,
        event_id=parent_id,
        status='FAILED')
    print("Send CASE1")

    # CASE 2
    parent_id = sf.create_event_id()
    sf.send_child(
        factory=factory,
        event_id=sf.create_event_id(),
        parent_id=parent_id,
        start_timestamp=report_start_timestamp,
        status='FAILED')

    time.sleep(1)

    sf.send_parent(
        factory=factory,
        start_timestamp=report_start_timestamp,
        event_id=parent_id,
        status='FAILED')
    print("Send CASE2")

    # CASE 3
    parent_id = sf.create_event_id()
    sf.send_child(
        factory=factory,
        event_id=sf.create_event_id(),
        parent_id=parent_id,
        start_timestamp=report_start_timestamp,
        status='FAILED')

    time.sleep(40)

    parent_id = sf.create_event_id()
    sf.send_child(
        factory=factory,
        event_id=sf.create_event_id(),
        parent_id=parent_id,
        start_timestamp=report_start_timestamp,
        status='FAILED')

    time.sleep(10)

    sf.send_parent(
        factory=factory,
        start_timestamp=report_start_timestamp,
        event_id=parent_id,
        status='FAILED')
    print("Send CASE3")


if __name__ == '__main__':
    logging.basicConfig(filename=time.asctime().replace(':', '-') + ' script.log',
                        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    factory = sf.connect(config_path="./configs/")

    try:
        start_datetime = datetime.datetime.now()
        scenario(factory)
        time.sleep(10)
        finish_datetime = datetime.datetime.now()

        print(F"start datetime: {start_datetime}")
        print(F"finish datetime: {finish_datetime}")

    finally:
        factory['factory'].close()
