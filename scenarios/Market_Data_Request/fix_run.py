from __future__ import print_function
import time
from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp
from th2_grpc_act_template.act_template_pb2 import PlaceMessageRequest
from th2_grpc_check1.check1_pb2 import CheckSequenceRuleRequest, PreFilter
from th2_grpc_common.common_pb2 import ConnectionID, ValueFilter, MessageFilter, RequestStatus, FilterOperation

from scenarios.Market_Data_Request.inputs import Inputs
from custom import support_functions as sf

def market_data_request(case_name,report_id, input_parameters,factory):
    # ############### CREATING THE REPORT FOR CASE ####################################################################
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
    ###################################################################################################################
    # ###### STEP1 - Market Data Request Full Book ####################################################################
    # Sending message to act and waiting for response
    request1_response = sf.market_data_request(
        act=factory['act'],
        place_message_request=PlaceMessageRequest(
            description=f'STEP1: Sends request to get Full Book.',
            connection_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            parent_event_id=input_parameters['case_id'],
            message=sf.create_message_object(msg_type='MarketDataRequest',
                                             fields=input.request1,
                                             session_alias=input_parameters['trader1_fix'])))
    # Check if response is correct
    if request1_response.status.status != RequestStatus.SUCCESS:
        print("Case " + case_name + " is INTERRUPTED in " + str(
            round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())) + " sec.")
        return input_parameters['ver1_chain'], input_parameters['ver2_chain']
    ###################################################################################################################
    # ###### STEP2 - Market Data Request Top Book #####################################################################
    # Sending message to act and waiting for response
    request2_response = sf.market_data_request(
        act=factory['act'],
        place_message_request=PlaceMessageRequest(
            description=f'STEP1: Sends request to get Top Book.',
            connection_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            parent_event_id=input_parameters['case_id'],
            message=sf.create_message_object(msg_type='MarketDataRequest',
                                             fields=input.request2,
                                             session_alias=input_parameters['trader1_fix'])))
    # Check if response is correct
    if request2_response.status.status != RequestStatus.SUCCESS:
        print("Case " + case_name + " is INTERRUPTED in " + str(
            round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())) + " sec.")
        return input_parameters['ver1_chain'], input_parameters['ver2_chain']
    ###################################################################################################################
    # ###### STEP3 - Data Change ######################################################################################
    # Sending message to act and waiting for response

    ###################################################################################################################
    # ###### STEP4 - Market Data Request Unsubscribe ##################################################################
    # Sending message to act and waiting for response
    request3_response = sf.market_data_request(
        act=factory['act'],
        place_message_request=PlaceMessageRequest(
            description=f'STEP1: Sends request to Unsubscribe.',
            connection_id=ConnectionID(session_alias=input_parameters['trader1_fix']),
            parent_event_id=input_parameters['case_id'],
            message=sf.create_message_object(msg_type='MarketDataRequest',
                                             fields=input.request3,
                                             session_alias=input_parameters['trader1_fix'])))
    # Check if response is correct
    if request3_response.status.status != RequestStatus.SUCCESS:
        print("Case " + case_name + " is INTERRUPTED in " + str(
            round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())) + " sec.")
        return input_parameters['ver1_chain'], input_parameters['ver2_chain']
