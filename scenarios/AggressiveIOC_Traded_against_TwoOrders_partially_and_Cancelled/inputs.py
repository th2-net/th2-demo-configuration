from datetime import datetime

from custom import support_functions as sf


class Inputs:
    basic_header = {
        'BeginString': 'FIXT.1.1',
        'SenderCompID': '*',
        'SendingTime': '*',
        'MsgSeqNum': '*',
        'BodyLength': '*',
        'MsgType': '8', }

    def __init__(self, input_parameters):
        self.input_parameters = input_parameters
        self.trading_party1 = self.trader1_trading_party()
        self.trading_party2 = self.trader2_trading_party()
        self.order1 = self.newordersingle1()
        self.order2 = self.newordersingle2()
        self.order3 = self.newordersingle3()

    def trader1_trading_party(self) -> list:
        return [
            {'PartyID': self.input_parameters['trader1'], 'PartyIDSource': "D", 'PartyRole': "76"},
            {'PartyID': "0", 'PartyIDSource': "P", 'PartyRole': "3"},
            {'PartyID': "0", 'PartyIDSource': "P", 'PartyRole': "122"},
            {'PartyID': "3", 'PartyIDSource': "P", 'PartyRole': "12"}]

    def trader2_trading_party(self) -> list:
        return [
            {'PartyID': self.input_parameters['trader2'], 'PartyIDSource': "D", 'PartyRole': "76"},
            {'PartyID': "0", 'PartyIDSource': "P", 'PartyRole': "3"},
            {'PartyID': "0", 'PartyIDSource': "P", 'PartyRole': "122"},
            {'PartyID': "3", 'PartyIDSource': "P", 'PartyRole': "12"}]

    def newordersingle1(self) -> dict:
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'OrderQty': self.input_parameters['Order1Qty'],
            'Price': self.input_parameters['Order1Price'],
            'ClOrdID': sf.generate_client_order_id(7),
            'SecondaryClOrdID': '11111',
            'Side': "1",
            'TransactTime': (datetime.now().isoformat()),
            'TradingParty': self.trading_party1
        }

    def newordersingle2(self) -> dict:
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'OrderQty': self.input_parameters['Order2Qty'],
            'Price': self.input_parameters['Order2Price'],
            'ClOrdID': sf.generate_client_order_id(7),
            'SecondaryClOrdID': '22222',
            'Side': "1",
            'TransactTime': (datetime.now().isoformat()),
            'TradingParty': self.trading_party1
        }

    def newordersingle3(self) -> dict:
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'OrderQty': self.input_parameters['Order3Qty'],
            'Price': self.input_parameters['Order3Price'],
            'ClOrdID': sf.generate_client_order_id(7),
            'SecondaryClOrdID': '33333',
            'Side': "2",
            'TimeInForce': '3',
            'TransactTime': (datetime.now().isoformat()),
            'TradingParty': self.trading_party2,
        }

    def execution1(self) -> dict:
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'ClOrdID': self.order1['ClOrdID'],
            'LeavesQty': self.order1['OrderQty'],
            'Side': self.order1['Side'],
            'Price': self.order1['Price'],
            'CumQty': '0',
            'ExecType': '0',
            'OrdStatus': '0',
            'TradingParty': self.trading_party1,
            'ExecID': '*',
            'OrderQty': self.order1['OrderQty'],
            'OrderID': '*',
            'Text': '*',
            'header': {**self.basic_header,
                       'TargetCompID': self.input_parameters['trader1']},
        }

    def execution2(self) -> dict:
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'ClOrdID': self.order2['ClOrdID'],
            'LeavesQty': self.order2['OrderQty'],
            'Side': self.order2['Side'],
            'Price': self.order2['Price'],
            'CumQty': '0',
            'ExecType': '0',
            'OrdStatus': '0',
            'TradingParty': self.trading_party1,
            'ExecID': '*',
            'OrderQty': self.order2['OrderQty'],
            'OrderID': '*',
            'Text': '*',
            'header': {**self.basic_header,
                       'TargetCompID': self.input_parameters['trader1']},
        }

    def execution2vs3(self) -> dict:
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'ClOrdID': self.order2['ClOrdID'],
            'LeavesQty': '0',
            'Side': self.order2['Side'],
            'CumQty': self.order2['OrderQty'],
            'ExecType': 'F',
            'OrdStatus': '2',
            'TradingParty': (self.trading_party1 + [
                {'PartyID': self.input_parameters['trader2_firm'], 'PartyIDSource': "D", 'PartyRole': "17"}
            ]),
            'ExecID': '*',
            'LastPx': self.order2['Price'],
            'Price': self.order2['Price'],
            'OrderQty': self.order2['OrderQty'],
            'OrderID': '*',
            'Text': '*',
            'TimeInForce': '0',
            'header': {**self.basic_header,
                       'TargetCompID': self.input_parameters['trader1']},
        }

    def execution1vs3(self):
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'ClOrdID': self.order1['ClOrdID'],
            'LeavesQty': '0',
            'Side': self.order1['Side'],
            'CumQty': self.order1['OrderQty'],
            'ExecType': 'F',
            'OrdStatus': '2',
            'TradingParty': self.trading_party1 + [
                {'PartyID': self.input_parameters['trader2_firm'], 'PartyIDSource': "D", 'PartyRole': "17"}],
            'ExecID': '*',
            'LastPx': self.order1['Price'],
            'Price': self.order1['Price'],
            'OrderQty': self.order1['OrderQty'],
            'OrderID': '*',
            'Text': '*',
            'TimeInForce': '0',
            'header': {**self.basic_header,
                       'TargetCompID': self.input_parameters['trader1']
                       }
        }

    def execution3vs2(self):
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'ClOrdID': self.order3['ClOrdID'],
            'OrderQty': self.order3['OrderQty'],
            'LeavesQty': self.order3['OrderQty'] - self.order2['OrderQty'],
            'Side': self.order3['Side'],
            'CumQty': self.order2['OrderQty'],
            'ExecType': 'F',
            'OrdStatus': '1',
            'TradingParty': self.trading_party2 + [
                {'PartyID': self.input_parameters['trader1_firm'], 'PartyIDSource': "D", 'PartyRole': "17"}],
            'ExecID': '*',
            'Price': self.order3['Price'],
            'OrderID': '*',
            'Text': '*',
            'TimeInForce': '3',
            'header': {**self.basic_header,
                       'TargetCompID': self.input_parameters['trader2']},
        }

    def execution3vs1(self):
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'ClOrdID': self.order3['ClOrdID'],
            'OrderQty': self.order3['OrderQty'],
            'LeavesQty': self.order3['OrderQty'] - self.order2['OrderQty'] - self.order1['OrderQty'],
            'Side': self.order3['Side'],
            'CumQty': self.order2['OrderQty'] + self.order1['OrderQty'],
            'ExecType': 'F',
            'OrdStatus': '1',
            'TradingParty': self.trading_party2 + [
                {'PartyID': self.input_parameters['trader1_firm'], 'PartyIDSource': "D", 'PartyRole': "17"}],
            'ExecID': '*',
            'Price': self.order3['Price'],
            'OrderID': '*',
            'Text': '*',
            'TimeInForce': '3',
            'header': {**self.basic_header,
                       'TargetCompID': self.input_parameters['trader2']},
        }

    def execution3(self):
        return {
            'SecurityID': self.input_parameters['Instrument'],
            'SecurityIDSource': "8",
            'OrdType': "2",
            'AccountType': "1",
            'OrderCapacity': "A",
            'ClOrdID': self.order3['ClOrdID'],
            'OrderQty': self.order3['OrderQty'],
            'LeavesQty': '0',
            'Side': self.order3['Side'],
            'CumQty': self.order2['OrderQty'] + self.order1['OrderQty'],
            'ExecType': 'C',
            'OrdStatus': 'C',
            'TradingParty': self.trading_party2,
            'ExecID': '*',
            'Price': self.order3['Price'],
            'OrderID': '*',
            'Text': '*',
            'TimeInForce': '3',
            'header': {**self.basic_header,
                       'TargetCompID': self.input_parameters['trader2']},
        }
