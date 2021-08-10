from __future__ import print_function
import time
from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp
from th2_grpc_act_template.act_template_pb2 import PlaceMessageRequest
from th2_grpc_check1.check1_pb2 import CheckSequenceRuleRequest, PreFilter
from th2_grpc_common.common_pb2 import ConnectionID, ValueFilter, MessageFilter, RequestStatus, FilterOperation

from scenarios.AggressiveIOC_Traded_against_TwoOrders_partially_and_Cancelled.inputs import Inputs
from custom import support_functions as sf


def aggressive_ioc_traded_against_two_orders_partially_and_then_cancelled(case_name, report_id, input_parameters,
                                                                          factory):
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
    input = Inputs(input_parameters)
    # ######STEP1 - TRADER1 SENDS PASSIVE BUY ORDER WITH PRICE = X ####################################################
    # Sending message to act and waiting for response
    order1_response = sf.placeOrderFIX(
        act=factory['act'],
        place_message_request=PlaceMessageRequest(
            description=f'STEP1: Trader "{input_parameters["trader1"]}" sends request to create passive Order.',
            connection_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            parent_event_id=input_parameters['case_id'],
            message=sf.create_message_object(msg_type='NewOrderSingle',
                                             fields=input.order1,
                                             session_alias=input_parameters['trader1_fix'])))
    # Check if response is correct
    if order1_response.status.status != RequestStatus.SUCCESS:
        print("Case " + case_name + " is INTERRUPTED in " + str(
            round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())) + " sec.")
        return input_parameters['ver1_chain'], input_parameters['ver2_chain']
    ###################################################################################################################
    # ######STEP2 - TRADER1 RECEIVES THE EXECUTION REPORT WITH EXECTYPE = NEW #########################################
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
                                                     fields=input.execution1(),
                                                     key_fields_list=['ClOrdID', 'OrdStatus'])]))
    ###################################################################################################################
    # ####STEP3 - TRADER1 SENDS PASSIVE BUY ORDER WITH PRICE = X-1 ####################################################
    # Sending message to act and waiting for response
    order2_response = sf.placeOrderFIX(
        act=factory['act'],
        place_message_request=PlaceMessageRequest(
            description=f'STEP3: Trader "{input_parameters["trader1"]}" '
                        f'sends request to create passive Order with price lower than first order.',
            connection_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            parent_event_id=input_parameters['case_id'],
            message=sf.create_message_object(msg_type='NewOrderSingle',
                                             fields=input.order2,
                                             session_alias=input_parameters['trader1_fix'])))
    # Check if response is correct
    if order2_response.status.status != RequestStatus.SUCCESS:
        print("Case " + case_name + " is INTERRUPTED in " + str(
            round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())) + " sec.")
        return input_parameters['ver1_chain'], input_parameters['ver2_chain']
    ###################################################################################################################
    # ######STEP4 - TRADER1 RECEIVES THE EXECUTION REPORT WITH EXECTYPE = NEW #########################################
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
                                                     fields=input.execution2(),
                                                     key_fields_list=['ClOrdID', 'OrdStatus'])]
        ))
    ###################################################################################################################
    # ####STEP5 - TRADER2 SENDS AGGRESSIVE SELL ORDER WITH PRICE = X+1 ################################################
    # Sending message to act and waiting for response
    order3_response = sf.placeOrderFIX(
        act=factory['act'],
        place_message_request=PlaceMessageRequest(
            description=f'STEP5: Trader "{input_parameters["trader2"]}" sends request to create aggressive IOC Order.',
            connection_id=ConnectionID(session_alias=input_parameters['trader2_fix']),
            parent_event_id=input_parameters['case_id'],
            message=sf.create_message_object(msg_type='NewOrderSingle',
                                             fields=input.order3,
                                             session_alias=input_parameters['trader2_fix'])))
    # Check if response is correct
    if order3_response.status.status != RequestStatus.SUCCESS:
        print("Case " + case_name + " is INTERRUPTED in " + str(
            round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())) + " sec.")
        return input_parameters['ver1_chain'], input_parameters['ver2_chain']
    ###################################################################################################################
    # ######STEP6 - TRADER1 RECEIVES TWO EXECUTION REPORTS WITH EXECTYPE = TRADE ######################################
    er_2vs3_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                             fields=input.execution2vs3(),
                                             key_fields_list=['ClOrdID', 'OrdStatus', 'LeavesQty', 'CumQty'])
    er_1vs3_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                             fields=input.execution1vs3(),
                                             key_fields_list=['ClOrdID', 'OrdStatus', 'LeavesQty', 'CumQty'])
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
    er_3vs2_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                             fields=input.execution3vs2(),
                                             key_fields_list=['ClOrdID', 'OrdStatus', 'LeavesQty', 'CumQty'])
    er_3vs1_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                             fields=input.execution3vs1(),
                                             key_fields_list=['ClOrdID', 'OrdStatus', 'LeavesQty', 'CumQty'])
    er_cancellation_filter = sf.create_filter_object(msg_type='ExecutionReport',
                                                     fields=input.execution3(),
                                                     key_fields_list=['ClOrdID', 'OrdStatus', 'LeavesQty', 'CumQty'])
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
