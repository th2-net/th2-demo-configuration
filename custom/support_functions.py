from __future__ import print_function

import logging
import uuid
import time
from google.protobuf.timestamp_pb2 import Timestamp
from th2_common.schema.factory.common_factory import CommonFactory
from th2_grpc_common.common_pb2 import EventID, Event, EventBatch


# -----------Connection functions
def connect(config_path, tries=3):
    try:
        logging.info('Trying to connect...')
        factory = CommonFactory(config_path=config_path, logging_config_filepath="configs/log4py.conf")
        estore = factory.event_batch_router
        logging.info('Connection established.')
        return {'estore': estore,
                'factory': factory}
    except Exception as e:
        if tries > 0:
            logging.error('Unable to connect.')
            logging.error(str(e))
            logging.info('Retry in 3...')
            print(f'Unable to connect: \n {str(e)}')
            time.sleep(3)
            connect(config_path, tries - 1)
        else:
            raise


# -------estore functions
def submit_event(estore, event_batch):
    logging.debug(f'Event content:{str(event_batch)}')
    response = estore.send(event_batch)
    logging.debug(f'Estore response content:{str(response)}')


def create_event_id():
    return EventID(id=str(uuid.uuid1()))


def send_root(factory, start_timestamp, event_id, name, status, body=b"", etype=b""):
    current_timestamp = Timestamp()
    current_timestamp.GetCurrentTime()
    parent = Event(
        id=event_id,
        name=name,
        status=status,
        body=body,
        type=etype,
        start_timestamp=start_timestamp,
        end_timestamp=current_timestamp)

    event_batch = EventBatch()
    event_batch.events.append(parent)
    submit_event(
        estore=factory['estore'],
        event_batch=event_batch
    )


def send_event(factory, start_timestamp, event_id, parent_id, name, status, body=b"", etype=b""):
    current_timestamp = Timestamp()
    current_timestamp.GetCurrentTime()

    child = Event(
        id=event_id,
        parent_id=parent_id,
        name=name,
        status=status,
        body=body,
        type=etype,
        start_timestamp=start_timestamp,
        end_timestamp=current_timestamp,
    )

    event_batch = EventBatch()
    event_batch.events.append(child)
    submit_event(
        estore=factory['estore'],
        event_batch=event_batch
    )
