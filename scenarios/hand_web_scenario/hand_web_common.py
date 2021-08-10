from th2_grpc_check1.check1_pb2 import CheckRuleRequest
from th2_grpc_common.common_pb2 import ValueFilter, FilterOperation, ConnectionID

import copy


def create_filter_fields(fields, key_fields_list):
    fields = copy.deepcopy(fields)
    for field in fields:
        if fields[field] == '*':
            fields[field] = ValueFilter(operation=FilterOperation.NOT_EMPTY)
        if isinstance(fields[field], str) or isinstance(fields[field], int) or isinstance(fields[field], float):
            if field in key_fields_list:
                fields[field] = ValueFilter(simple_filter=str(fields[field]), key=True)
            else:
                fields[field] = ValueFilter(simple_filter=str(fields[field]))
    return fields


def create_check_rule_request(description, connectivity, checkpoint, timeout, event_id, message_filter):
    connectivity = ConnectionID(session_alias=connectivity)
    return CheckRuleRequest(connectivity_id=connectivity,
                            filter=message_filter,
                            checkpoint=checkpoint,
                            timeout=timeout,
                            parent_event_id=event_id,
                            description=description)


def to_str_trading_parties(array):
    copied = copy.deepcopy(array)
    for dict_cp in copied:
        for key in dict_cp:
            if not isinstance(dict_cp[key], str):
                dict_cp[key] = str(dict_cp[key])
    return copied
