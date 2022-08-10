from datetime import datetime
import logging
from typing import Tuple

from custom.support_functions import Connection
from scenarios.AggressiveIOC_Traded_against_TwoOrders_partially_and_Cancelled.inputs import Inputs
from th2_common_utils import create_timestamp
from th2_common_utils.converters.filter_converters import dict_to_pre_filter, dict_to_root_message_filter, FieldFilter
from th2_grpc_check1.check1_pb2 import ChainID
from th2_grpc_common.common_pb2 import EventID, FilterOperation, RequestStatus

logger = logging.getLogger()


def aggressive_ioc_traded_against_two_orders_partially_and_then_cancelled(
        case_name: str,
        scenario_event_id: EventID,
        inputs: Inputs,
        connection: Connection) -> Tuple[ChainID, ChainID]:
    # ################CREATING THE REPORT FOR CASE#####################################################################
    # Sending request to estore. Creation of the parent Event for actions.

    case_start_timestamp = create_timestamp()
    case_id = connection.create_and_send_event(event_name=case_name,
                                               parent_id=scenario_event_id,
                                               start_timestamp=case_start_timestamp)

    ###################################################################################################################
    # ######STEP1 - TRADER1 SENDS PASSIVE BUY ORDER WITH PRICE = X ####################################################
    # Sending message to act and waiting for response

    order1_response = connection.placeOrderFIX(
        session_alias=inputs.users['trader1']['TraderConnection'],
        parent_event_id=case_id,
        message_typed=inputs.order1,
        description=f'STEP1: Trader {inputs.users["trader1"]["TraderName"]} sends request to create passive Order.'
    )

    # Check if response is correct
    if order1_response.status.status != RequestStatus.SUCCESS:
        logger.error(f'Case {case_name} is INTERRUPTED '
                     f'in {round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())} sec.')
        return inputs.ver1_chain, inputs.ver2_chain

    ###################################################################################################################
    # ######STEP2 - TRADER1 RECEIVES THE EXECUTION REPORT WITH EXECTYPE = NEW #########################################
    # Sending request to check1

    ver1_chain = connection.submitCheckSequenceRule(
        description=f'STEP2: Trader {inputs.users["trader1"]["TraderName"]} receives Execution Report. '
                    f'The order stands on book in status NEW',
        chain_id=inputs.ver1_chain,
        session_alias=inputs.users['trader1']['TraderConnection'],
        checkpoint=order1_response.checkpoint_id,
        parent_event_id=case_id,
        prefilter=dict_to_pre_filter(
            fields={
                'SecurityID': inputs.instrument['Name'],
                'header': {'MsgType': FieldFilter('f', operation=FilterOperation.NOT_EQUAL)}
            }
        ),
        root_message_filters=[
            dict_to_root_message_filter(message_type='ExecutionReport',
                                        message_filter=inputs.execution1())
        ],
        timeout=5000
    )

    ###################################################################################################################
    # ####STEP3 - TRADER1 SENDS PASSIVE BUY ORDER WITH PRICE = X-1 ####################################################
    # Sending message to act and waiting for response

    order2_response = connection.placeOrderFIX(
        session_alias=inputs.users['trader1']['TraderConnection'],
        parent_event_id=case_id,
        message_typed=inputs.order2,
        description=f'STEP3: Trader {inputs.users["trader1"]["TraderName"]} '
                    f'sends request to create passive Order with price higher than first order.'
    )

    # Check if response is correct
    if order2_response.status.status != RequestStatus.SUCCESS:
        logger.error(f'Case {case_name} is INTERRUPTED '
                     f'in {round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())} sec.')
        return inputs.ver1_chain, inputs.ver2_chain

    ###################################################################################################################
    # ######STEP4 - TRADER1 RECEIVES THE EXECUTION REPORT WITH EXECTYPE = NEW #########################################
    # Sending request to check1

    connection.submitCheckSequenceRule(
        description=f'STEP4: Trader {inputs.users["trader1"]["TraderName"]} '
                    f'receives Execution Report. The order stands on book in status NEW',
        chain_id=ver1_chain.chain_id,
        session_alias=inputs.users['trader1']['TraderConnection'],
        checkpoint=order2_response.checkpoint_id,
        parent_event_id=case_id,
        prefilter=dict_to_pre_filter(fields={'SecurityID': inputs.instrument['Name']}),
        root_message_filters=[
            dict_to_root_message_filter(message_type='ExecutionReport',
                                        message_filter=inputs.execution2())
        ]
    )

    ###################################################################################################################
    # ####STEP5 - TRADER2 SENDS AGGRESSIVE SELL ORDER WITH PRICE = X+1 ################################################
    # Sending message to act and waiting for response

    order3_response = connection.placeOrderFIX(
        session_alias=inputs.users['trader2']['TraderConnection'],
        parent_event_id=case_id,
        message_typed=inputs.order3,
        description=f'STEP5: Trader {inputs.users["trader2"]["TraderName"]} '
                    f'sends request to create aggressive IOC Order.'
    )

    # Check if response is correct
    if order3_response.status.status != RequestStatus.SUCCESS:
        logger.error(f'Case {case_name} is INTERRUPTED '
                     f'in {round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())} sec.')
        return inputs.ver1_chain, inputs.ver2_chain

    ###################################################################################################################
    # ######STEP6 - TRADER1 RECEIVES TWO EXECUTION REPORTS WITH EXECTYPE = TRADE ######################################
    # Sending request to check1

    connection.submitCheckSequenceRule(
        description=f'STEP6: Trader {inputs.users["trader1"]["TraderName"]} receives Execution Reports '
                    f'with ExecType=F: first at Order2 and second on Order1.',
        chain_id=ver1_chain.chain_id,
        session_alias=inputs.users['trader1']['TraderConnection'],
        parent_event_id=case_id,
        prefilter=dict_to_pre_filter(fields={'SecurityID': inputs.instrument['Name']}),
        root_message_filters=[
            dict_to_root_message_filter(message_type='ExecutionReport',
                                        message_filter=inputs.execution2vs3()),
            dict_to_root_message_filter(message_type='ExecutionReport',
                                        message_filter=inputs.execution1vs3())
        ],
        check_order=True
    )

    ###################################################################################################################
    # ######STEP7 - TRADER2 RECEIVES TWO EXECUTION REPORTS WITH EXECTYPE = TRADE AND ONE WITH EXECTYPE = EXPIRED#######
    # Sending request to check

    ver2_chain = connection.submitCheckSequenceRule(
        description=f'STEP7: Trader {inputs.users["trader2"]["TraderName"]} receives Execution Reports: '
                    f'first trade with Order2, next with Order1 and then cancellation',
        chain_id=inputs.ver2_chain,
        session_alias=inputs.users['trader2']['TraderConnection'],
        parent_event_id=case_id,
        checkpoint=order3_response.checkpoint_id,
        prefilter=dict_to_pre_filter(fields={'SecurityID': inputs.instrument['Name']}),
        root_message_filters=[
            dict_to_root_message_filter(message_type='ExecutionReport',
                                        message_filter=inputs.execution3vs2()),
            dict_to_root_message_filter(message_type='ExecutionReport',
                                        message_filter=inputs.execution3vs1()),
            dict_to_root_message_filter(message_type='ExecutionReport',
                                        message_filter=inputs.execution3()),
        ],
        check_order=True
    )

    ###################################################################################################################
    # Print case execution time

    logger.info(f'Case {case_name} is executed '
                f'in {round(datetime.now().timestamp() - case_start_timestamp.ToSeconds())} sec.')
    return ver1_chain.chain_id, ver2_chain.chain_id
