# Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from th2_grpc_act_uiframework_web_demo.uiframework_web_demo_pb2 import NewOrderSingleParams, RptViewerDetails, \
    RhBatchResponseDemo, RptViewerSearchDetails

import random, string, logging
from datetime import datetime
from th2_grpc_hand import rhbatch_pb2
from th2_grpc_common.common_pb2 import MessageFilter

from custom.support_functions import store_event, wrap_into_trading_party
from scenarios.hand_web_scenario import hand_web_common

#######################################################################################################################
# Creation of grpc channels and instances of ACT, CHECK stubs.
#######################################################################################################################

nos_params = {
    'OrderQty': 200,
    'OrdType': '2',
    'ClOrdID': '',
    'SecurityIDSource': '8',
    'OrderCapacity': 'A',
    'TransactTime': '',
    'SecondaryClOrdID': '11111',
    'AccountType': 1,
    'Side': '1',
    'Price': 55,
    'SecurityID': '5221001',
    'DisplayQty': 200
}

sessionParams = {
    'session': 'demo-conn1',
    'dictionary': 'fix50-generic',
    'messageType': 'NewOrderSingle',
}


check_fields = {'ClOrdID': nos_params['ClOrdID'],
                'OrderQty': nos_params['OrderQty'],
                'SecurityIDSource': '8',
                'OrderCapacity': 'A',
                'TransactTime': '2020-12-01T13:37:01.194850',
                'SecondaryClOrdID': nos_params['SecondaryClOrdID'],
                'AccountType': '1',
                'Side': nos_params['Side'],
                'Price': str(nos_params['Price']),
                'SecurityID': nos_params['SecurityID']}
no_party_ids = [
    {"PartyRole": 76, "PartyID": "ARFQ01FIX03", "PartyIDSource": "D"},
    {"PartyRole": 3, "PartyID": "0", "PartyIDSource": "P"},
    {"PartyRole": 122, "PartyID": "0", "PartyIDSource": "P"},
    {"PartyRole": 12, "PartyID": "3", "PartyIDSource": "P"}
]

check_params = {**check_fields, 'TradingParty': wrap_into_trading_party("filter", hand_web_common
                                                                        .to_str_trading_parties(no_party_ids))}


def test_1(factory, test_case_event_id, session_id):
    test_common(factory, test_case_event_id, session_id, sessionParams, nos_params.copy(), check_params.copy())


def test_2(factory, test_case_event_id, session_id):
    test_common(factory, test_case_event_id, session_id, {}, nos_params.copy(), check_params.copy())


def test_3(factory, test_case_event_id, session_id):
    check_fields_1 = check_params.copy()
    check_fields_1['AccountType'] = '2'
    check_fields_1['OrderQty'] = '0'
    nos_copy = nos_params.copy()
    nos_copy['SecondaryClOrdID'] = '22222'
    check_fields_1['SecurityID'] = nos_copy['SecurityID'] = '5221002'
    test_common(factory, test_case_event_id, session_id, sessionParams, nos_copy, check_fields_1)


def test_common(factory, test_case_event_id, session_id, session_args, nos_params_cp, test_check_fields):

    act = factory['web_act']
    check1 = factory['check']

    test_check_fields['TransactTime'] = nos_params_cp['TransactTime'] = datetime.utcnow().isoformat()[:-3]
    test_check_fields['ClOrdID'] = nos_params_cp['ClOrdID'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    exec_reports_fields = test_check_fields.copy()
    test_check_fields['TransactTime'] = test_check_fields['TransactTime'][:-4]
    del exec_reports_fields['SecondaryClOrdID']
    del exec_reports_fields['TransactTime']

    nos = NewOrderSingleParams(**session_args, sessionID=session_id, eventID=test_case_event_id)
    nos.message.CopyFrom(NewOrderSingleParams.NewOrderSingleBody(**nos_params_cp))
    for npid_rg in no_party_ids:
        party_id = nos.message.TradingParty.NoPartyIDs.add()
        party_id.CopyFrom(NewOrderSingleParams.NoPartyID(**npid_rg))

    batch_response = act.sendNewOrderSingleGui(nos)
    checkpoint = batch_response.checkpoint
    logging.debug("RPC sent new order single:\n%s", batch_response)

    if batch_response.scriptStatus != RhBatchResponseDemo.ExecutionStatus.SUCCESS:
        raise Exception("Error while sending NewOrderSingle Message")

    url = batch_response.data['url']
    if not url:
        raise Exception("url wasnt extracted")
    rpt_details = RptViewerDetails(sessionID=session_id, eventID=test_case_event_id, url=url)
    batch_response = act.extractSentMessageGui(rpt_details)

    if batch_response.scriptStatus != RhBatchResponseDemo.ExecutionStatus.SUCCESS:
        raise Exception("Error while retrieving NewOrderSingle Message from rpt-viewer")

    rpt_details = RptViewerSearchDetails(sessionID=session_id, eventID=test_case_event_id,
                                         url=url, msgType='ExecutionReport',
                                         msgBody=nos_params_cp['ClOrdID'],
                                         description='Extracting response message from UI')

    batch_response = act.findMessageGui(rpt_details)
    if batch_response.scriptStatus != RhBatchResponseDemo.ExecutionStatus.SUCCESS:
        raise Exception("Error while retrieving ExecutionReport Message from rpt-viewer")

    check1.submitCheckRule(
        hand_web_common.create_check_rule_request(
            description="Check New Order Single",
            connectivity=session_id.sessionAlias,
            checkpoint=checkpoint,
            timeout=3000,
            event_id=test_case_event_id,
            message_filter=MessageFilter(messageType='NewOrderSingle',
                                         fields=hand_web_common.create_filter_fields(fields=test_check_fields,
                                                                            key_fields_list=["ClOrdID"]))
        ))

    check1.submitCheckRule(
        hand_web_common.create_check_rule_request(
            description="Check Execution Report",
            connectivity=session_id.sessionAlias,
            checkpoint=checkpoint,
            timeout=3000,
            event_id=test_case_event_id,
            message_filter=MessageFilter(messageType='ExecutionReport',
                                         fields=hand_web_common.create_filter_fields(fields=exec_reports_fields,
                                                                            key_fields_list=["ClOrdID"]))
        ))


def run_web_gui_tests(factory, parent_event_id, name, test):

    tc_event = store_event(factory, name, parent_id=parent_event_id)
    act = factory['web_act']
    session_id = act.register(rhbatch_pb2.RhTargetServer(target=factory['custom']['target_server_web']))
    try:
        test(factory, tc_event, session_id)
    except Exception:
        logging.error("Test case " + name + " failed", exc_info=True)
    finally:
        act.unregister(session_id)


def run_tests(factory):
    parent_event_id = store_event(factory, "[TS_0] Sending order via act-ui and verification ExecutionReport")
    logging.debug("Event %s", parent_event_id)

    run_web_gui_tests(factory, parent_event_id, "Case[TC_0.1] Sending NewOrderSingle and verifying ExecutionReport "
                                                "on INSTR1", test_1)
    run_web_gui_tests(factory, parent_event_id, "Case[TC_0.2] Sending NewOrderSingle and verifying ExecutionReport "
                                                "without session parameters", test_2)
    run_web_gui_tests(factory, parent_event_id, "Case[TC_0.3] Sending NewOrderSingle and verifying ExecutionReport "
                                                "on INSTR2", test_3)

