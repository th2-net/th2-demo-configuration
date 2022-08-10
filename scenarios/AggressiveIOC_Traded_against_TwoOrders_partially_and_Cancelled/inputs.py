from datetime import datetime
from typing import Any, Dict, Optional

from custom import support_functions as sf
from th2_common_utils.converters.filter_converters import FieldFilter
from th2_grpc_act_template.act_template_typed_pb2 import NewOrderSingle, NoPartyIDs, TradingParty
from th2_grpc_check1.check1_pb2 import ChainID
from th2_grpc_common.common_pb2 import FilterOperation


class Inputs:

    basic_header = {
        'BeginString': 'FIXT.1.1',
        'SenderCompID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
        'SendingTime': FieldFilter(operation=FilterOperation.NOT_EMPTY),
        'MsgSeqNum': FieldFilter(operation=FilterOperation.NOT_EMPTY),
        'BodyLength': FieldFilter(operation=FilterOperation.NOT_EMPTY),
        'MsgType': '8'
    }

    def __init__(self,
                 instrument: Dict[str, str],
                 users: Dict[str, Any],
                 ver1_chain: Optional[ChainID],
                 ver2_chain: Optional[ChainID]) -> None:
        self.instrument = instrument
        self.users = users
        self.ver1_chain = ver1_chain
        self.ver2_chain = ver2_chain

        self.order1 = self.new_order_single1()
        self.order2 = self.new_order_single2()
        self.order3 = self.new_order_single3()

    def trader1_trading_party(self) -> dict:
        return {
            'NoPartyIDs': [
                {'PartyID': self.users['trader1']['TraderName'], 'PartyIDSource': 'D', 'PartyRole': '76'},
                {'PartyID': '0', 'PartyIDSource': 'P', 'PartyRole': '3'},
                {'PartyID': '0', 'PartyIDSource': 'P', 'PartyRole': '122'},
                {'PartyID': '3', 'PartyIDSource': 'P', 'PartyRole': '12'}
            ]
        }

    def trader2_trading_party(self) -> dict:
        return {
            'NoPartyIDs': [
                {'PartyID': self.users['trader2']['TraderName'], 'PartyIDSource': 'D', 'PartyRole': '76'},
                {'PartyID': '0', 'PartyIDSource': 'P', 'PartyRole': '3'},
                {'PartyID': '0', 'PartyIDSource': 'P', 'PartyRole': '122'},
                {'PartyID': '3', 'PartyIDSource': 'P', 'PartyRole': '12'}
            ]
        }

    def new_order_single1(self) -> NewOrderSingle:
        return self._create_new_order_single(order_qty=30,
                                             side='1',
                                             user_id='trader1',
                                             ord_type='2',
                                             secondary_cl_ord_id='11111')

    def new_order_single2(self) -> NewOrderSingle:
        return self._create_new_order_single(order_qty=10,
                                             side='1',
                                             user_id='trader1',
                                             ord_type='2',
                                             secondary_cl_ord_id='22222')

    def new_order_single3(self) -> NewOrderSingle:
        return self._create_new_order_single(order_qty=100,
                                             side='2',
                                             user_id='trader2',
                                             ord_type='2',
                                             secondary_cl_ord_id='33333',
                                             time_in_force='3')

    def execution1(self) -> dict:
        return {
            'SecurityID': self.instrument['Name'],
            'SecurityIDSource': '8',
            'OrdType': '2',
            'AccountType': '1',
            'OrderCapacity': 'A',
            'ClOrdID': FieldFilter(self.order1.cl_ord_id, key=True),
            'LeavesQty': int(self.order1.order_qty),
            'Side': self.order1.side,
            'Price': int(self.order1.price),
            'CumQty': '0',
            'ExecType': '0',
            'OrdStatus': FieldFilter('0', key=True),
            'TradingParty': self.trader1_trading_party(),
            'ExecID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'OrderQty': int(self.order1.order_qty),
            'OrderID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Text': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'header': {
                **self.basic_header,
                       'TargetCompID': self.users['trader1']['TraderName']
            },
        }

    def execution2(self) -> dict:
        return {
            'SecurityID': self.instrument['Name'],
            'SecurityIDSource': '8',
            'OrdType': '2',
            'AccountType': '1',
            'OrderCapacity': 'A',
            'ClOrdID': FieldFilter(self.order2.cl_ord_id, key=True),
            'LeavesQty': int(self.order2.order_qty),
            'Side': self.order2.side,
            'Price': int(self.order2.price),
            'CumQty': '0',
            'ExecType': '0',
            'OrdStatus': FieldFilter('0', key=True),
            'TradingParty': self.trader1_trading_party(),
            'ExecID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'OrderQty': int(self.order2.order_qty),
            'OrderID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Text': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'header': {
                **self.basic_header,
                'TargetCompID': self.users['trader1']['TraderName']
            },
        }

    def execution2vs3(self) -> dict:
        trading_party = self.trader1_trading_party()
        trading_party['NoPartyIDs'] += [
            {
                'PartyID': self.users['trader2']['FirmName'],
                'PartyIDSource': 'D',
                'PartyRole': '17'
            }
        ]

        return {
            'SecurityID': self.instrument['Name'],
            'SecurityIDSource': '8',
            'OrdType': '2',
            'AccountType': '1',
            'OrderCapacity': 'A',
            'ClOrdID': FieldFilter(self.order2.cl_ord_id, key=True),
            'LeavesQty': FieldFilter('0', key=True),
            'Side': self.order2.side,
            'CumQty': FieldFilter(int(self.order2.order_qty), key=True),
            'ExecType': 'F',
            'OrdStatus': FieldFilter('2', key=True),
            'TradingParty': trading_party,
            'ExecID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'LastPx': int(self.order2.price),
            'Price': int(self.order2.price),
            'OrderQty': int(self.order2.order_qty),
            'OrderID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Text': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'TimeInForce': '0',
            'header': {
                **self.basic_header,
                'TargetCompID': self.users['trader1']['TraderName']
            },
        }

    def execution1vs3(self) -> dict:
        trading_party = self.trader1_trading_party()
        trading_party['NoPartyIDs'] += [
            {
                'PartyID': self.users['trader2']['FirmName'],
                'PartyIDSource': 'D',
                'PartyRole': '17'
            }
        ]

        return {
            'SecurityID': self.instrument['Name'],
            'SecurityIDSource': '8',
            'OrdType': '2',
            'AccountType': '1',
            'OrderCapacity': 'A',
            'ClOrdID': FieldFilter(self.order1.cl_ord_id, key=True),
            'LeavesQty': FieldFilter('0', key=True),
            'Side': self.order1.side,
            'CumQty': FieldFilter(int(self.order1.order_qty), key=True),
            'ExecType': 'F',
            'OrdStatus': FieldFilter('2', key=True),
            'TradingParty': trading_party,
            'ExecID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'LastPx': int(self.order1.price),
            'Price': int(self.order1.price),
            'OrderQty': int(self.order1.order_qty),
            'OrderID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Text': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'TimeInForce': '0',
            'header': {
                **self.basic_header,
                'TargetCompID': self.users['trader1']['TraderName']
            }
        }

    def execution3vs2(self) -> dict:
        trading_party = self.trader2_trading_party()
        trading_party['NoPartyIDs'] += [
            {
                'PartyID': self.users['trader1']['FirmName'],
                'PartyIDSource': 'D',
                'PartyRole': '17'
            }
        ]

        return {
            'SecurityID': self.instrument['Name'],
            'SecurityIDSource': '8',
            'OrdType': '2',
            'AccountType': '1',
            'OrderCapacity': 'A',
            'ClOrdID': FieldFilter(self.order3.cl_ord_id, key=True),
            'OrderQty': int(self.order3.order_qty),
            'LeavesQty': FieldFilter(int(self.order3.order_qty - self.order2.order_qty), key=True),
            'Side': self.order3.side,
            'CumQty': FieldFilter(int(self.order2.order_qty), key=True),
            'ExecType': 'F',
            'OrdStatus': FieldFilter('1', key=True),
            'TradingParty': trading_party,
            'ExecID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Price': int(self.order3.price),
            'OrderID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Text': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'TimeInForce': '3',
            'header': {
                **self.basic_header,
                'TargetCompID': self.users['trader2']['TraderName']
            },
        }

    def execution3vs1(self) -> dict:
        trading_party = self.trader2_trading_party()
        trading_party['NoPartyIDs'] += [
            {
                'PartyID': self.users['trader1']['FirmName'],
                'PartyIDSource': 'D',
                'PartyRole': '17'
            }
        ]

        return {
            'SecurityID': self.instrument['Name'],
            'SecurityIDSource': '8',
            'OrdType': '2',
            'AccountType': '1',
            'OrderCapacity': 'A',
            'ClOrdID': FieldFilter(self.order3.cl_ord_id, key=True),
            'OrderQty': int(self.order3.order_qty),
            'LeavesQty': FieldFilter(int(self.order3.order_qty - self.order2.order_qty - self.order1.order_qty),
                                     key=True),
            'Side': self.order3.side,
            'CumQty': FieldFilter(int(self.order2.order_qty + self.order1.order_qty), key=True),
            'ExecType': 'F',
            'OrdStatus': FieldFilter('1', key=True),
            'TradingParty': trading_party,
            'ExecID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Price': int(self.order3.price),
            'OrderID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Text': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'TimeInForce': '3',
            'header': {
                **self.basic_header,
                'TargetCompID': self.users['trader2']['TraderName']
            },
        }

    def execution3(self) -> dict:
        return {
            'SecurityID': self.instrument['Name'],
            'SecurityIDSource': '8',
            'OrdType': '2',
            'AccountType': '1',
            'OrderCapacity': 'A',
            'ClOrdID': FieldFilter(self.order3.cl_ord_id, key=True),
            'OrderQty': int(self.order3.order_qty),
            'LeavesQty': FieldFilter('0', key=True),
            'Side': self.order3.side,
            'CumQty': FieldFilter(int(self.order2.order_qty + self.order1.order_qty), key=True),
            'ExecType': 'C',
            'OrdStatus': FieldFilter('C', key=True),
            'TradingParty': self.trader2_trading_party(),
            'ExecID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Price': int(self.order3.price),
            'OrderID': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'Text': FieldFilter(operation=FilterOperation.NOT_EMPTY),
            'TimeInForce': '3',
            'header': {
                **self.basic_header,
                'TargetCompID': self.users['trader2']['TraderName']
            },
        }

    def _create_new_order_single(self,
                                 order_qty: float,
                                 side: str,
                                 user_id: str,
                                 ord_type: str,
                                 secondary_cl_ord_id: str,
                                 time_in_force: str = '0') -> NewOrderSingle:
        return NewOrderSingle(security_id=self.instrument['Name'],
                              security_id_source=str(self.instrument['SecurityIDSource']),
                              ord_type=ord_type,
                              account_type=self.users[user_id]['AccountType'],
                              order_capacity=self.users[user_id]['OrderCapacity'],
                              order_qty=order_qty,
                              price=int(self.instrument['Price']),
                              cl_ord_id=sf.create_client_order_id(6),
                              secondary_cl_ord_id=secondary_cl_ord_id,
                              side=side,
                              time_in_force=time_in_force,
                              transact_time=datetime.now().isoformat(),
                              trading_party=self._create_trading_party(user_id))

    def _create_trading_party(self, user_id: str) -> TradingParty:
        return TradingParty(
            no_party_ids=[
                NoPartyIDs(party_id=self.users[user_id]['TraderName'],
                           party_id_source='D',
                           party_role=76),
                NoPartyIDs(party_id='0',
                           party_id_source='P',
                           party_role=3),
                NoPartyIDs(party_id='0',
                           party_id_source='P',
                           party_role=122),
                NoPartyIDs(party_id='3',
                           party_id_source='P',
                           party_role=12)
            ]
        )
