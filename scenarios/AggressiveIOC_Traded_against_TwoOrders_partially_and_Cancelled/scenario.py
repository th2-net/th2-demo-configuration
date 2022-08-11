from pathlib import Path
from typing import Optional

from custom import support_functions as sf
from custom.support_functions import Connection
from scenarios.AggressiveIOC_Traded_against_TwoOrders_partially_and_Cancelled import case
from scenarios.AggressiveIOC_Traded_against_TwoOrders_partially_and_Cancelled.inputs import Inputs
from th2_grpc_common.common_pb2 import EventID


def scenario(connection: Connection, scenario_id: int, parent: Optional[EventID] = None) -> None:
    # Creation of the root Event for all cases performed.
    scenario_name = f'[TS_{scenario_id}]Aggressive IOC vs two orders: ' \
                    f'second order\'s price is more favorable than first'
    scenario_event_id = connection.create_and_send_event(event_name=scenario_name,
                                                         parent_id=parent)

    # Initialize chain_id for scenario
    ver1_chain, ver2_chain = None, None

    # Getting case participants from refdata
    instruments = sf.read_configuration(Path(__file__).parent / 'configs/instruments.refdata')
    users = sf.read_configuration(Path(__file__).parent / 'configs/users.refdata')

    trader1, trader2 = users.keys()

    # Execution of case for every instrument in refdata
    for case_id, instrument in enumerate(instruments, start=1):
        ver1_chain, ver2_chain = case.aggressive_ioc_traded_against_two_orders_partially_and_then_cancelled(
            case_name=f'Case[TC_{scenario_id}.{case_id}]: '
                      f'Trader {trader1} vs trader {trader2} for instrument {instrument["Name"]}',
            scenario_event_id=scenario_event_id,
            inputs=Inputs(
                instrument=instrument,
                users=users,
                ver1_chain=ver1_chain,
                ver2_chain=ver2_chain
            ),
            connection=connection
        )
