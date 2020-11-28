from __future__ import print_function

import logging
import time
from datetime import datetime

import yaml
from google.protobuf.timestamp_pb2 import Timestamp
from th2_grpc_act_template.act_template_pb2 import *
from th2_grpc_check1.check1_pb2 import *
from th2_grpc_common.common_pb2 import *

from .custom import support_functions as sf

# IMPORT REFDATA FROM FILES
with open('configs/instruments.refdata') as f:
    instruments = yaml.load(f, Loader=yaml.FullLoader)
with open('configs/firms.refdata') as f:
    firms = yaml.load(f, Loader=yaml.FullLoader)


def aggressive_ioc_traded_against_two_orders_partially_and_then_cancelled(case_name, report_id, input_parameters,
                                                                          factory):
    # ####SETTING STATIC INFORMATION###################################################################################
    # General parameters for orders in this case
    new_order_general_parameters = {
        'SecurityID': input_parameters['Instrument'],
        'SecurityIDSource': "8",
        'OrdType': "2",
        'AccountType': "1",
        'OrderCapacity': "A",
    }
    # NoPartyIDs repeating group for Trader1
    trader1_trading_party = [
        {'PartyID': input_parameters['trader1'], 'PartyIDSource': "D", 'PartyRole': "76"},
        {'PartyID': "0", 'PartyIDSource': "P", 'PartyRole': "3"},
        {'PartyID': "0", 'PartyIDSource': "P", 'PartyRole': "122"},
        {'PartyID': "3", 'PartyIDSource': "P", 'PartyRole': "12"}]
    # NoPartyIDs repeating group for Trader2
    trader2_trading_party = [
        {'PartyID': input_parameters["trader2"], 'PartyIDSource': "D", 'PartyRole': "76"},
        {'PartyID': "0", 'PartyIDSource': "P", 'PartyRole': "3"},
        {'PartyID': "0", 'PartyIDSource': "P", 'PartyRole': "122"},
        {'PartyID': "3", 'PartyIDSource': "P", 'PartyRole': "12"}]
    # FIX header
    basic_header = {
        'BeginString': 'FIXT.1.1',
        'SenderCompID': 'FGW',
        'SendingTime': '*',
        'MsgSeqNum': '*',
        'BodyLength': '*',
        'MsgType': '8', }

    ###################################################################################################################

    # ################CREATING THE REPORT FOR CASE#####################################################################
    case_start_timestamp = Timestamp()
    case_start_timestamp.GetCurrentTime()

    # Sending request to estore. Creation of the parent Event for actions.
    sf.submit_event(
        estore=factory['estore'],
        event_batch=sf.create_event_batch(
            report_name=case_name,
            start_timestamp=case_start_timestamp,
            event_id=input_parameters['case_id'],
            parent_id=report_id))
    ###################################################################################################################

    # ######STEP1 - TRADER1 SENDS PASSIVE BUY ORDER WITH PRICE = X ####################################################

    # Unique parameters for Order1
    order1_parameters = {
        **new_order_general_parameters,
        'OrderQty': input_parameters['Order1Qty'],
        'Price': input_parameters['Order1Price'],
        'ClOrdID': sf.generate_client_order_id(7),
        'SecondaryClOrdID': '11111',
        'Side': "1",
        'TransactTime': (datetime.now().isoformat()),
        'TradingParty': sf.wrap_into_trading_party("value", trader1_trading_party),
    }

    # Sending message to act and waiting for response
    order1_response = sf.placeOrderFIX(
        act=factory['act'],
        place_message_request=PlaceMessageRequest(
            description=f'STEP1: Trader "{input_parameters["trader1"]}" sends request to create passive Order.',
            connection_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            parent_event_id=input_parameters['case_id'],
            message=sf.create_message_object(msg_type='NewOrderSingle',
                                             fields=order1_parameters,
                                             session_alias=input_parameters['trader1_fix'])))
    # Check if response is correct
    if order1_response.status.status != 0:
        return input_parameters['ver1_chain'], input_parameters['ver2_chain']
    ###################################################################################################################

    # ######STEP2 - TRADER1 RECEIVES THE EXECUTION REPORT WITH EXECTYPE = NEW #########################################
    # Unique parameters for Execution Report ExecType=NEW on Order1
    er1_parameters = {
        **new_order_general_parameters,
        'ClOrdID': order1_parameters['ClOrdID'],
        'LeavesQty': order1_parameters['OrderQty'],
        'Side': order1_parameters['Side'],
        'Price': order1_parameters['Price'],
        'CumQty': '0',
        'ExecType': '0',
        'OrdStatus': '0',
        'TradingParty': sf.wrap_into_trading_party('filter', trader1_trading_party),
        'ExecID': '*',
        'OrderQty': order1_parameters['OrderQty'],
        'OrderID': '*',
        'Text': '*',
        'header': {**basic_header,
                   'TargetCompID': input_parameters['trader1']},
    }

    # Sending request to check1
    ver1_chain = sf.submitCheckSequenceRule(
        check=factory['check'],
        check_sequence_rule_request=CheckSequenceRuleRequest(
            description=f'STEP2: Trader "{input_parameters["trader1"]}" receives Execution Report. '
            f'The order stands on book in status NEW',
            chain_id=sf.create_chain_id() if not input_parameters['ver1_chain'] else input_parameters['ver1_chain'],
            connectivity_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            checkpoint=order1_response.checkpoint_id,
            timeout=5000,
            parent_event_id=input_parameters['case_id'],
            pre_filter=PreFilter(fields={
                'SecurityID': ValueFilter(simple_filter=input_parameters['Instrument']),
                'header': ValueFilter(message_filter=MessageFilter(fields={
                    'MsgType': ValueFilter(simple_filter='f', operation=FilterOperation.NOT_EQUAL)}))}),
            message_filters=[sf.create_filter_object(msg_type='ExecutionReport',
                                                     fields=er1_parameters,
                                                     key_fields_list=['ClOrdID'])]
        ))
    ###################################################################################################################

    # ####STEP3 - TRADER1 SENDS PASSIVE BUY ORDER WITH PRICE = X-1 ####################################################
    # Unique parameters for Order2
    order2_parameters = {
        **new_order_general_parameters,
        'OrderQty': input_parameters['Order2Qty'],
        'Price': input_parameters['Order2Price'],
        'ClOrdID': sf.generate_client_order_id(7),
        'SecondaryClOrdID': '22222',
        'Side': "1",
        'TransactTime': (datetime.now().isoformat()),
        'TradingParty': sf.wrap_into_trading_party("value", trader1_trading_party),
    }

    # Sending message to act and waiting for response
    order2_response = sf.placeOrderFIX(
        act=factory['act'],
        place_message_request=PlaceMessageRequest(
            description=f'STEP3: Trader "{input_parameters["trader1"]}" '
            f'sends request to create passive Order with price lower than first order.',
            connection_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            parent_event_id=input_parameters['case_id'],
            message=sf.create_message_object(msg_type='NewOrderSingle',
                                             fields=order2_parameters,
                                             session_alias=input_parameters['trader1_fix'])))

    # Check if response is correct
    if order2_response.status.status != 0:
        return input_parameters['ver1_chain'], input_parameters['ver2_chain']
    ###################################################################################################################

    # ######STEP4 - TRADER1 RECEIVES THE EXECUTION REPORT WITH EXECTYPE = NEW #########################################
    # Unique parameters for Execution Report ExecType=NEW for Order2
    er2_parameters = {
        **new_order_general_parameters,
        'ClOrdID': order2_parameters['ClOrdID'],
        'LeavesQty': order2_parameters['OrderQty'],
        'Side': order2_parameters['Side'],
        'Price': order2_parameters['Price'],
        'CumQty': '0',
        'ExecType': '0',
        'OrdStatus': '0',
        'TradingParty': sf.wrap_into_trading_party('filter', trader1_trading_party),
        'ExecID': '*',
        'OrderQty': order2_parameters['OrderQty'],
        'OrderID': '*',
        'Text': '*',
        'header': {**basic_header,
                   'TargetCompID': input_parameters['trader1']},
    }

    # Sending request to check1
    sf.submitCheckSequenceRule(
        check=factory['check'],
        check_sequence_rule_request=CheckSequenceRuleRequest(
            description=f'STEP4: Trader "{input_parameters["trader1"]}" '
            f'receives Execution Report. The order stands on book in status NEW',
            connectivity_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            checkpoint=order2_response.checkpoint_id,
            chain_id=ver1_chain.chain_id,
            timeout=1000,
            parent_event_id=input_parameters['case_id'],
            pre_filter=PreFilter(fields={'SecurityID': ValueFilter(simple_filter=input_parameters['Instrument'])}),
            message_filters=[sf.create_filter_object(msg_type='ExecutionReport',
                                                     fields=er2_parameters,
                                                     key_fields_list=['ClOrdID'])]
        ))
    ###################################################################################################################

    # ####STEP5 - TRADER2 SENDS AGGRESSIVE SELL ORDER WITH PRICE = X+1 ################################################
    # Unique parameters for Order3
    order3_parameters = {
        **new_order_general_parameters,
        'OrderQty': input_parameters['Order3Qty'],
        'Price': input_parameters['Order3Price'],
        'ClOrdID': sf.generate_client_order_id(7),
        'SecondaryClOrdID': '33333',
        'Side': "2",
        'TimeInForce': '3',
        'TransactTime': (datetime.now().isoformat()),
        'TradingParty': sf.wrap_into_trading_party("value", trader2_trading_party),
    }

    # Sending message to act and waiting for response
    order3_response = sf.placeOrderFIX(
        act=factory['act'],
        place_message_request=PlaceMessageRequest(
            description=f'STEP5: Trader "{input_parameters["trader2"]}" sends request to create aggressive IOC Order.',
            connection_id=ConnectionID(session_alias=input_parameters['trader2_fix']),
            parent_event_id=input_parameters['case_id'],
            message=sf.create_message_object(msg_type='NewOrderSingle',
                                             fields=order3_parameters,
                                             session_alias=input_parameters['trader2_fix'])))

    # Check if response is correct
    if order3_response.status.status != 0:
        return input_parameters['ver1_chain'], input_parameters['ver2_chain']
    ###################################################################################################################

    # ######STEP6 - TRADER1 RECEIVES TWO EXECUTION REPORTS WITH EXECTYPE = TRADE ######################################
    # Parameters for Execution Report ExecType=TRADE Order2vsOrder3
    er_2vs3_parameters = {
        **new_order_general_parameters,
        'ClOrdID': order2_parameters['ClOrdID'],
        'LeavesQty': '0',
        'Side': order2_parameters['Side'],
        'CumQty': order2_parameters['OrderQty'],
        'ExecType': 'F',
        'OrdStatus': '2',
        'TradingParty': sf.wrap_into_trading_party('filter', trader1_trading_party + [
            {'PartyID': input_parameters['trader2_firm'], 'PartyIDSource': "D", 'PartyRole': "17"}
        ]),
        'ExecID': '*',
        'LastPx': order2_parameters['Price'],
        'Price': order2_parameters['Price'],
        'OrderQty': order2_parameters['OrderQty'],
        'OrderID': '*',
        'Text': '*',
        'TimeInForce': '0',
        'header': {**basic_header,
                   'TargetCompID': input_parameters['trader1']},
    }
    er_2vs3_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                             fields=er_2vs3_parameters,
                                             key_fields_list=['ClOrdID'])

    # Parameters for Execution Report ExecType=TRADE Order1vsOrder3
    er_1vs3_parameters = {
        **new_order_general_parameters,
        'ClOrdID': order1_parameters['ClOrdID'],
        'LeavesQty': '0',
        'Side': order1_parameters['Side'],
        'CumQty': order1_parameters['OrderQty'],
        'ExecType': 'F',
        'OrdStatus': '2',
        'TradingParty': sf.wrap_into_trading_party('filter', trader1_trading_party + [
            {'PartyID': input_parameters['trader2_firm'], 'PartyIDSource': "D", 'PartyRole': "17"}
        ]),
        'ExecID': '*',
        'LastPx': order1_parameters['Price'],
        'Price': order1_parameters['Price'],
        'OrderQty': order1_parameters['OrderQty'],
        'OrderID': '*',
        'Text': '*',
        'TimeInForce': '0',
        'header': {**basic_header,
                   'TargetCompID': input_parameters['trader1']},
    }
    er_1vs3_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                             fields=er_1vs3_parameters,
                                             key_fields_list=['ClOrdID'])

    # Sending request to check1
    sf.submitCheckSequenceRule(
        check=factory['check'],
        check_sequence_rule_request=CheckSequenceRuleRequest(
            description=f'STEP6: Trader "{input_parameters["trader1"]}" receives Execution Reports with ExecType=F: '
            f'first at Order2 and second on Order1.',
            connectivity_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            chain_id=ver1_chain.chain_id,
            timeout=1000,
            parent_event_id=input_parameters['case_id'],
            pre_filter=PreFilter(fields={'SecurityID': ValueFilter(simple_filter=input_parameters['Instrument'])}),
            message_filters=[er_2vs3_filter, er_1vs3_filter],
            check_order=True))
    ###################################################################################################################

    # ######STEP7 - TRADER2 RECEIVES TWO EXECUTION REPORTS WITH EXECTYPE = TRADE AND ONE WITH EXECTYPE = EXPIRED#######
    # Parameters for Execution Report ExecType=TRADE Order3vsOrder2
    er_3vs2_parameters = {
        **new_order_general_parameters,
        'ClOrdID': order3_parameters['ClOrdID'],
        'OrderQty': order3_parameters['OrderQty'],
        'LeavesQty': order3_parameters['OrderQty'] - order2_parameters['OrderQty'],
        'Side': order3_parameters['Side'],
        'CumQty': order2_parameters['OrderQty'],
        'ExecType': 'F',
        'OrdStatus': '1',
        'TradingParty': sf.wrap_into_trading_party('filter', trader2_trading_party + [
            {'PartyID': input_parameters['trader1_firm'], 'PartyIDSource': "D", 'PartyRole': "17"}
        ]),
        'ExecID': '*',
        'Price': order3_parameters['Price'],
        'OrderID': '*',
        'Text': '*',
        'TimeInForce': '3',
        'header': {**basic_header,
                   'TargetCompID': input_parameters['trader2']},
    }
    er_3vs2_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                             fields=er_3vs2_parameters,
                                             key_fields_list=['ClOrdID'])

    # Parameters for Execution Report ExecType=TRADE Order3vsOrder1
    er_3vs1_parameters = {
        **new_order_general_parameters,
        'ClOrdID': order3_parameters['ClOrdID'],
        'OrderQty': order3_parameters['OrderQty'],
        'LeavesQty': order3_parameters['OrderQty'] - order2_parameters['OrderQty'] - order1_parameters['OrderQty'],
        'Side': order3_parameters['Side'],
        'CumQty': order2_parameters['OrderQty'] + order1_parameters['OrderQty'],
        'ExecType': 'F',
        'OrdStatus': '1',
        'TradingParty': sf.wrap_into_trading_party('filter', trader2_trading_party + [
            {'PartyID': input_parameters['trader1_firm'], 'PartyIDSource': "D", 'PartyRole': "17"}
        ]),
        'ExecID': '*',
        'Price': order3_parameters['Price'],
        'OrderID': '*',
        'Text': '*',
        'TimeInForce': '3',
        'header': {**basic_header,
                   'TargetCompID': input_parameters['trader2']},
    }
    er_3vs1_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                             fields=er_3vs1_parameters,
                                             key_fields_list=['ClOrdID'])

    # Parameters for Execution Report ExecType=C Order3
    er_cancellation_parameters = {
        **new_order_general_parameters,
        'ClOrdID': order3_parameters['ClOrdID'],
        'OrderQty': order3_parameters['OrderQty'],
        'LeavesQty': '0',
        'Side': order3_parameters['Side'],
        'CumQty': order2_parameters['OrderQty'] + order1_parameters['OrderQty'],
        'ExecType': 'C',
        'OrdStatus': 'C',
        'TradingParty': sf.wrap_into_trading_party('filter', trader2_trading_party),
        'ExecID': '*',
        'Price': order3_parameters['Price'],
        'OrderID': '*',
        'Text': '*',
        'TimeInForce': '3',
        'header': {**basic_header,
                   'TargetCompID': input_parameters['trader2']},
    }
    er_cancellation_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                                     fields=er_cancellation_parameters,
                                                     key_fields_list=['ClOrdID'])

    # Sending request to check1
    ver2_chain = sf.submitCheckSequenceRule(
        check=factory['check'],
        check_sequence_rule_request=CheckSequenceRuleRequest(
            description=f'STEP7: Trader "{input_parameters["trader2"]}" receives Execution Reports: '
            f'first trade with Order2, next with Order1 and then cancellation',
            connectivity_id=ConnectionID(session_alias=input_parameters['trader2_fix']),
            checkpoint=order3_response.checkpoint_id,
            chain_id=sf.create_chain_id() if not input_parameters['ver2_chain'] else input_parameters['ver2_chain'],
            timeout=1000,
            parent_event_id=input_parameters['case_id'],
            pre_filter=PreFilter(fields={'SecurityID': ValueFilter(simple_filter=input_parameters['Instrument'])}),
            message_filters=[er_3vs2_filter, er_3vs1_filter, er_cancellation_filter],
            check_order=True))
    ###################################################################################################################
    # Print case execution time
    print("Case " + case_name + " is executed in " + str(
        round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())) + " sec.")
    return ver1_chain.chain_id, ver2_chain.chain_id


def scenario():
    # Creation of grpc channels and instances of act, check1 and estore stubs.
    factory = sf.connect(router_grpc="./configs/grpc.json",
                         rabbit_mq='./configs/rabbit.json',
                         router_mq='./configs/mq.json')

    # Storing EventID object of root Event.
    report_id = sf.create_event_id()

    # Storing grpc Timestamp of script start.
    report_start_timestamp = Timestamp()
    report_start_timestamp.GetCurrentTime()

    # Initialize chain_id for script
    ver1_chain = None
    ver2_chain = None
    scenario_id = 1
    # Sending request to estore. Creation of the root Event for all cases performed.
    sf.submit_event(
        estore=factory['estore'],
        event_batch=sf.create_event_batch(
            report_name=f"[TS_{scenario_id}]Aggressive IOC vs two orders: second order's price is lower than first",
            start_timestamp=report_start_timestamp,
            event_id=report_id))

    # Getting case participants from refdata
    trader1 = firms[0]['Traders'][0]['TraderName']
    trader1_firm = firms[0]['FirmName']
    trader1_fix = firms[0]['Traders'][0]['TraderConnection']
    trader2 = firms[1]['Traders'][0]['TraderName']
    trader2_firm = firms[1]['FirmName']
    trader2_fix = firms[1]['Traders'][0]['TraderConnection']

    # ####REQUEST SECURITY STATUSES##################################
    mdata_requests_report = sf.create_event_id()
    # Sending request to estore. Creation of the root Event for all cases performed later.
    sf.submit_event(
        estore=factory['estore'],
        event_batch=sf.create_event_batch(
            report_name="Prerequisites: Request security statuses",
            start_timestamp=report_start_timestamp,
            event_id=mdata_requests_report,
            parent_id=report_id))

    for instrument in instruments:
        sf.request_security_status(instrument['SecurityID'], trader1_fix, mdata_requests_report, factory)
    ##################################################################

    case_id = 0
    # Execution of case for every instrument in refdata
    for instrument in instruments:
        case_id += 1
        ver1_chain, ver2_chain = aggressive_ioc_traded_against_two_orders_partially_and_then_cancelled(
            f"Case[TC_{scenario_id}.{case_id}]: "
            f"Trader {trader1} vs trader {trader2} for instrument {instrument['SecurityID']}",
            report_id, {
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
    scenario()
