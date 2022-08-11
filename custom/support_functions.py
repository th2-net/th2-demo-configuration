import logging
from pathlib import Path
import random
import time
from typing import List, Optional
import uuid

from google.protobuf.text_format import MessageToString
from google.protobuf.timestamp_pb2 import Timestamp
from th2_common.schema.factory.common_factory import CommonFactory
from th2_common.schema.message.message_router import MessageRouter
from th2_common_utils import create_event
from th2_grpc_act_template.act_template_typed_pb2 import NewOrderSingle, PlaceMessageRequestTyped, \
    PlaceMessageResponseTyped, RequestMessageTyped
from th2_grpc_act_template.act_typed_service import ActTypedService
from th2_grpc_check1 import check1_pb2
from th2_grpc_check1.check1_pb2 import ChainID, CheckSequenceRuleRequest, CheckSequenceRuleResponse, PreFilter
from th2_grpc_check1.check1_service import Check1Service
from th2_grpc_common.common_pb2 import Checkpoint, ConnectionID, Event, EventBatch, EventID, EventStatus, MessageID, \
    MessageMetadata, RootMessageFilter
import yaml

logger = logging.getLogger()


class Connection:

    def __init__(self,
                 factory: CommonFactory,
                 act: ActTypedService,
                 check1: Check1Service,
                 estore: MessageRouter) -> None:
        self.factory = factory
        self.act = act
        self.check1 = check1
        self.estore = estore

    def create_and_send_event(self,
                              event_name: str = 'DemoScriptEvent',
                              parent_id: Optional[EventID] = None,
                              start_timestamp: Optional[Timestamp] = None) -> EventID:
        event: Event = create_event(parent_id=parent_id,
                                    status=EventStatus.SUCCESS,
                                    name=event_name,
                                    start_timestamp=start_timestamp)
        self.estore.send(EventBatch(events=[event]))

        return event.id

    def placeOrderFIX(self,
                      session_alias: str,
                      parent_event_id: EventID,
                      message_typed: NewOrderSingle,
                      description: str) -> PlaceMessageResponseTyped:
        place_message_request = PlaceMessageRequestTyped(
            metadata=MessageMetadata(message_type='NewOrderSingle',
                                     id=MessageID(connection_id=ConnectionID(
                                         session_alias=session_alias))),
            parent_event_id=parent_event_id,
            message_typed=RequestMessageTyped(new_order_single=message_typed),
            description=description
        )

        logging.debug(f'Sending request to act: {MessageToString(place_message_request, as_one_line=True)}')

        try:
            act_response: PlaceMessageResponseTyped = self.act.placeOrderFIX(place_message_request)
        except Exception as e:
            logging.error(f'FATAL ERROR. Unable to proceed: {e}')
            raise e

        if act_response.status.status == 0:
            logging.debug(f'Request submitted. Response received with status: {act_response.status.status}')
        else:
            logging.error(f'Request submitted. Act rule executed incorrectly{str(act_response.status)}.')

        return act_response

    def submitCheckSequenceRule(self,
                                description: str,
                                chain_id: ChainID,
                                session_alias: str,
                                parent_event_id: EventID,
                                prefilter: PreFilter,
                                root_message_filters: List[RootMessageFilter],
                                checkpoint: Optional[Checkpoint] = None,
                                check_order: bool = False,
                                timeout: int = 1000) -> CheckSequenceRuleResponse:
        check_sequence_rule_request = CheckSequenceRuleRequest(
            description=description,
            chain_id=chain_id if chain_id else create_chain_id(),
            connectivity_id=ConnectionID(session_alias=session_alias),
            checkpoint=checkpoint,
            timeout=timeout,
            parent_event_id=parent_event_id,
            pre_filter=prefilter,
            check_order=check_order,
            root_message_filters=root_message_filters
        )

        logging.debug(f'Sending CheckSequenceRuleRequest to check...: '
                      f'{MessageToString(check_sequence_rule_request, as_one_line=True)}')

        try:
            check_response: CheckSequenceRuleResponse = self.check1.submitCheckSequenceRule(check_sequence_rule_request)
        except Exception as e:
            logging.error(f'FATAL ERROR. Unable to proceed: {e}')
            raise e

        if check_response.status.status == 0:
            logging.debug(f'Request submitted. Response received: '
                          f'{MessageToString(check_response, as_one_line=True)}')
        else:
            logging.error(f'Request submitted. Check executed incorrectly. '
                          f'Check response status: {check_response.status}')

        return check_response

    def close(self) -> None:
        self.factory.close()


def create_connection(config_path: Path, tries: int = 3) -> Connection:
    try:
        factory = CommonFactory(config_path=config_path, logging_config_filepath=Path('configs/log4py.conf'))
        grpc_router = factory.grpc_router
        estore = factory.event_batch_router

        act = grpc_router.get_service(ActTypedService)
        check1 = grpc_router.get_service(Check1Service)

        logger.info('Connection established.')

        return Connection(factory=factory,
                          act=act,
                          check1=check1,
                          estore=estore)

    except Exception as e:
        if tries > 0:
            logging.error(f'Unable to connect: {e}. Retry in 3 seconds...')
            time.sleep(3)
            create_connection(config_path, tries - 1)
        else:
            raise e


def create_chain_id() -> ChainID:
    return check1_pb2.ChainID(id=str(uuid.uuid1()))


def create_client_order_id(length: int) -> str:
    return str(random.randint(10 ** length, (10 ** (length + 1)) - 1))


def read_configuration(path: Path) -> dict:
    with open(path) as f:
        return yaml.load(f, Loader=yaml.FullLoader)
