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
import copy
from dataclasses import dataclass

from th2_grpc_act_uiframework_win_demo.uiframework_win_demo_pb2 import BaseMessage, OpenApplicationRequest, \
    InitConnectionRequest, SendNewOrderSingleRequest, ExtractLastOrderDetailsRequest
from th2_grpc_check1.check1_pb2 import CheckpointRequest, CheckRuleRequest
from th2_grpc_common.common_pb2 import ConnectionID, ValueFilter, MessageFilter, FilterOperation, RootMessageFilter, \
    MetadataFilter, ListValueFilter
from th2_grpc_hand import rhbatch_pb2

from custom.support_functions import store_event, generate_client_order_id


def create_order_params() -> list:
    return [Tag('35', 'MsgType', 'D'),
            Tag('11', 'ClOrdID', str(generate_client_order_id(7))),
            Tag('54', 'Side', '1'),
            Tag('60', 'TransactTime', '$TIMESTAMP'),
            Tag('40', 'OrdType', '2'),
            Tag('44', 'Price', '98'),
            Tag('38', 'OrderQty', '9998'),
            Tag('453', 'NoPartyIDs', '0')]


def create_check_rule_request(description, connectivity, checkpoint, timeout, event_id, root_filter):
    connectivity = ConnectionID(session_alias=connectivity)
    return CheckRuleRequest(connectivity_id=connectivity,
                            root_filter=root_filter,
                            checkpoint=checkpoint,
                            timeout=timeout,
                            parent_event_id=event_id,
                            description=description)


def create_filter_fields(fields, key_fields_list, extract_fields=False):
    fields = copy.deepcopy(fields)
    for field in fields:
        if fields[field] == '*':
            fields[field] = ValueFilter(operation=FilterOperation.NOT_EMPTY)
        if extract_fields:
            value = fields[field].value
        else:
            value = fields[field]
        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
            if field in key_fields_list:
                fields[field] = ValueFilter(simple_filter=str(value), key=True)
            else:
                fields[field] = ValueFilter(simple_filter=str(value))
        if isinstance(value, list):
            list_value_filter = ListValueFilter()
            for current_value in value:
                if isinstance(current_value, dict):
                    message_filter = MessageFilter(
                        fields=create_filter_fields(current_value, key_fields_list, extract_fields))
                    list_value_filter.values.append(ValueFilter(message_filter=message_filter))
            fields[field] = ValueFilter(list_filter=list_value_filter)
    return fields


@dataclass
class Tag:
    tag_number: str
    tag_name: str
    value: str


def open_application(factory, base_message):
    request = OpenApplicationRequest(base=base_message,
                                     workDir=factory['custom']['application_folder'],
                                     appFile=factory['custom']['exec_file'])
    factory['win_act'].openApplication(request)


def create_base_message(factory) -> BaseMessage:
    parent_event_id = store_event(factory, "Mini-FIX demo execution")
    print("Event %s" % parent_event_id)
    session_id = factory['win_act'].register(
        rhbatch_pb2.RhTargetServer(target=factory['custom']['target_server_win']))
    return BaseMessage(sessionId=session_id, parentEventId=parent_event_id)


def init_connection(factory, base_message):
    session_settings = InitConnectionRequest.SessionSettings(senderCompId=factory['custom']['sender_comp_id'],
                                                             targetCompId=factory['custom']['target_comp_id'],
                                                             fixVersion="FIXT.1.1",
                                                             resetSession=False)
    connection_request = InitConnectionRequest(base=base_message,
                                               sessionSettings=session_settings,
                                               host=factory['custom']['fix_server_host'],
                                               port=factory['custom']['fix_server_port'])
    factory['win_act'].initConnection(connection_request)


def send_new_order_single(factory, base_message, tags: list):
    order_request = SendNewOrderSingleRequest(base=base_message)
    for tag_desc in tags:
        current = SendNewOrderSingleRequest.Tags()
        current.tagNumber = tag_desc.tag_number
        current.tagValue = tag_desc.value
        order_request.tags.append(current)
    factory['win_act'].sendNewOrderSingle(order_request)


def extract_last_order_details(factory, base_message):
    details_request = ExtractLastOrderDetailsRequest(base=base_message,
                                                     extractionFields=["ClOrdID", "CumQty",
                                                                       "OrderQty", "Price",
                                                                       "LeavesQty", "ExecID",
                                                                       "OrderID", "Text"])
    details = factory['win_act'].extractLastOrderDetails(details_request)
    return details.executionId, dict(details.data)


def extract_last_system_message(factory, base_message):
    return factory['win_act'].extractLastSystemMessage(base_message)


def create_checkpoint(factory, base_message):
    checkpoint_request = CheckpointRequest(parent_event_id=base_message.parentEventId)
    return factory['check'].createCheckpoint(checkpoint_request).checkpoint


def create_root_filter(exp_fields, execution_id, extract_values=False, message_type="FIX",
                       root_message_type="ExecutionReport", key_fields_list=["ClOrdID"], skip_metadata=False):
    message_filter = RootMessageFilter(
        messageType=root_message_type,
        message_filter=MessageFilter(
            fields=create_filter_fields(fields=exp_fields, key_fields_list=key_fields_list,
                                        extract_fields=extract_values))
    )
    if not skip_metadata:
        message_filter.metadata_filter.CopyFrom(MetadataFilter(
            property_filters={
                "MessageType": MetadataFilter.SimpleFilter(value=message_type),
                "ExecutionId": MetadataFilter.SimpleFilter(value=execution_id)
            }
        ))
    return message_filter


def check_fix_message(factory, base_message, checkpoint, tags, fields_set, execution_id):
    exp_fields = {}
    for tag_data in tags:
        if tag_data.tag_name in fields_set:
            exp_fields[tag_data.tag_name] = tag_data.value

    factory['check'].submitCheckRule(
        create_check_rule_request(
            description="Check raw Execution Report from MiniFix against expected result from script",
            connectivity="th2-hand-demo",
            checkpoint=checkpoint,
            timeout=5000,
            event_id=base_message.parentEventId,
            root_filter=create_root_filter(exp_fields, execution_id)
        ))


def check_hand_message(factory, base_message, checkpoint, result_id, execution_id):
    exp_fields = {
        "ActionResults": [
            {
                "data": 98,
                "id": result_id
            }
        ],
        "ExecutionId": execution_id,
        "MessageType": "PLAIN_STRING",
        "RhSessionId": "th2_hand"
    }

    factory['check'].submitCheckRule(
        create_check_rule_request(
            description="Check extracted value from MiniFix against expected result from script",
            connectivity="th2-hand-demo",
            checkpoint=checkpoint,
            timeout=5000,
            event_id=base_message.parentEventId,
            root_filter=create_root_filter(exp_fields, execution_id, message_type="th2-hand",
                                           root_message_type="th2-hand", key_fields_list=["ExecutionId", "id"],
                                           skip_metadata=True)
        )
    )


def check_fix_message_failed(factory, base_message, checkpoint, tags, fields_set, execution_id):
    exp_fields = {}
    for tag_data in tags:
        if tag_data.tag_name in fields_set:
            exp_fields[tag_data.tag_name] = tag_data.value

    exp_fields['Price'] = str(int(exp_fields.get('Price')) + 1)

    factory['check'].submitCheckRule(
        create_check_rule_request(
            description="Check raw Execution Report from MiniFix against expected result from script (failed)",
            connectivity="th2-hand-demo",
            checkpoint=checkpoint,
            timeout=5000,
            event_id=base_message.parentEventId,
            root_filter=create_root_filter(exp_fields, execution_id)
        ))


def check_fix_message_against_table(factory, base_message, checkpoint, check_fields, execution_id):
    RootMessageFilter()
    factory['check'].submitCheckRule(
        create_check_rule_request(
            description="Check consistency raw Execution Report with displayed in table in MiniFixUI",
            connectivity="th2-hand-demo",
            checkpoint=checkpoint,
            timeout=5000,
            event_id=base_message.parentEventId,
            root_filter=create_root_filter(check_fields, execution_id, True)
        ))


def run(factory):
    base_message = create_base_message(factory)
    open_application(factory, base_message)
    init_connection(factory, base_message)
    checkpoint = create_checkpoint(factory, base_message)
    params = create_order_params()
    send_new_order_single(factory, base_message, params)
    execution_id, extracted_details = extract_last_order_details(factory, base_message)
    extracted_system_message = extract_last_system_message(factory, base_message)
    last_system_message_execution_id = extracted_system_message.executionId
    check_fix_message(factory, base_message, checkpoint, params, {'ClOrdID', 'Price', 'OrderQty', 'OrdType', 'Side'},
                      last_system_message_execution_id)
    check_fix_message_against_table(factory, base_message, checkpoint, extracted_details,
                                    last_system_message_execution_id)
    check_fix_message_failed(factory, base_message, checkpoint, params,
                             {'ClOrdID', 'Price', 'OrderQty', 'OrdType', 'Side'}, last_system_message_execution_id)

    check_hand_message(factory, base_message, checkpoint, "extractCellNameElId_8", execution_id)
    factory['win_act'].closeConnection(base_message)
    factory['win_act'].closeApplication(base_message)
