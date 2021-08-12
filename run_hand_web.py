from __future__ import print_function

import datetime
import logging
import time

from custom import support_functions as sf
from scenarios.hand_web_scenario import hand_web

from th2_grpc_check1.check1_service import Check1Service
from th2_grpc_act_uiframework_web_demo.ui_frame_work_hand_web_act_service import UiFrameWorkHandWebActService


def parse_factory(factory_param):
    grpc_router = factory_param.grpc_router
    web_act = grpc_router.get_service(UiFrameWorkHandWebActService)
    check = grpc_router.get_service(Check1Service)
    estore = factory_param.event_batch_router
    logging.info('Connection established.')
    return {'web_act': web_act,
            'check': check,
            'estore': estore,
            'factory': factory_param,
            'custom': factory_param.create_custom_configuration()}


if __name__ == '__main__':
    logging.basicConfig(filename=time.asctime().replace(':', '-') + ' script.log',
                        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Creation of grpc channels and instances of act, check1 and estore stubs.
    factory = sf.simple_connect(config_path="./configs/")
    try:
        start_datetime = datetime.datetime.now()
        hand_web.run_tests(parse_factory(factory))
        time.sleep(10)
        finish_datetime = datetime.datetime.now()

        print(F"start datetime: {start_datetime}")
        print(F"finish datetime: {finish_datetime}")

    finally:
        factory.close()