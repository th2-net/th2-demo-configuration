from __future__ import print_function

import logging
import os
import time

import yaml
from google.protobuf.timestamp_pb2 import Timestamp

from scenarios.AggressiveIOC_Traded_against_TwoOrders_partially_and_Cancelled import fix_run
from custom import support_functions as sf

# IMPORT REFDATA FROM FILES
with open('configs/instruments.refdata') as f:
    instruments = yaml.load(f, Loader=yaml.FullLoader)
with open('configs/firms.refdata') as f:
    firms = yaml.load(f, Loader=yaml.FullLoader)

issue_key = 'Issue'
folder_key = 'Folder'


def scenario(factory, parent=None):
    # Storing EventID object of root Event.
    report_id = sf.create_event_id()

    # Storing grpc Timestamp of script start.
    report_start_timestamp = Timestamp()
    report_start_timestamp.GetCurrentTime()

    # Initialize chain_id for script
    ver1_chain = None
    ver2_chain = None
    scenario_id = 1
    version = os.environ['JIRA_PROJECT_VERSION']
    cycle = os.environ['ZEPHYR_CYCLE']
    root_prefix = f"{version}|{cycle}|"
    # Sending request to estore. Creation of the root Event for all cases performed.
    sf.submit_event(
        estore=factory['estore'],
        event_batch=sf.create_event_batch(
            report_name=f"{root_prefix}[TS_{scenario_id}]Aggressive IOC vs two orders: second order's price is lower than first",
            start_timestamp=report_start_timestamp,
            event_id=report_id,
            parent_id=parent))

    # Getting case participants from refdata
    trader1 = firms[0]['Traders'][0]['TraderName']
    trader1_firm = firms[0]['FirmName']
    trader1_fix = firms[0]['Traders'][0]['TraderConnection']
    trader2 = firms[1]['Traders'][0]['TraderName']
    trader2_firm = firms[1]['FirmName']
    trader2_fix = firms[1]['Traders'][0]['TraderConnection']

    # mapping for issues' keys
    issue_events = {}
    folder_events = {}

    case_id = 0
    # Execution of case for every instrument in refdata
    for instrument in instruments:
        case_id += 1

        parent_id = report_id
        folder = None
        # create folder event if needed
        if folder_key in instrument:
            folder = instrument[folder_key]
            if folder not in folder_events:
                folder_id = sf.create_event_id()
                sf.submit_event(
                    estore=factory['estore'],
                    event_batch=sf.create_event_batch(
                        report_name=f"{folder}",
                        start_timestamp=report_start_timestamp,
                        event_id=folder_id,
                        parent_id=parent_id))
                folder_events[folder] = folder_id
            parent_id = folder_events[folder]

        # create issue event if needed
        if issue_key in instrument:
            issue = instrument[issue_key]
            key = (folder, issue)
            if key not in issue_events:
                issue_id = sf.create_event_id()
                sf.submit_event(
                    estore=factory['estore'],
                    event_batch=sf.create_event_batch(
                        report_name=f"{issue}",
                        start_timestamp=report_start_timestamp,
                        event_id=issue_id,
                        parent_id=parent_id))
                issue_events[key] = issue_id
            parent_id = issue_events[key]

        ver1_chain, ver2_chain = fix_run.aggressive_ioc_traded_against_two_orders_partially_and_then_cancelled(
            f"Case[TC_{scenario_id}.{case_id}]: "
            f"Trader {trader1} vs trader {trader2} for instrument {instrument['SecurityID']}",
            parent_id, {
                'case_id': sf.create_event_id(),
                'Instrument': instrument['SecurityID'],
                'Order1Price': instrument['Price'],
                'Order1Qty': 30,
                'Order2Price': instrument['Price'] + 1,
                'Order2Qty': 10,
                'Order3Price': instrument['Price'] - 1,
                'Order3Qty': 100,
                'trader1': trader1,
                'trader1_firm': trader1_firm,
                'trader1_fix': trader1_fix,
                'trader2': trader2,
                'trader2_firm': trader2_firm,
                'trader2_fix': trader2_fix,
                'ver1_chain': ver1_chain,
                'ver2_chain': ver2_chain
            }, factory)


if __name__ == '__main__':
    logging.basicConfig(filename=time.asctime().replace(':', '-') + ' script.log',
                        level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Creation of grpc channels and instances of act, check1 and estore stubs.
    factory = sf.connect(config_path="./configs/")
    try:
        scenario(factory)
    finally:
        factory['factory'].close()
