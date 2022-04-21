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
        self.NoMDET = self.m_d_r_mdet()
        self.NoRS = self.m_d_r_nrs()
        self.request1 = self.m_d_r_f()
        self.request2 = self.m_d_r_t()
        self.request3 = self.m_d_r_t2()

    def m_d_r_mdet(self) -> list:
        return [
            {'MDEntryType': '2'}
        ]

    def m_d_r_nrs(self) -> list:
        return [
            {'Instrument': {'SecurityID': self.input_parameters['Instrument'],
                            'SecurityIDSource': '8', 'Symbol': 'Instrument1'}}
        ]

    def m_d_r_f(self) -> dict:
        return {
            'MDReqID': sf.generate_client_order_id(7),
            'SubscriptionRequestType': '0',
            'MarketDepth': '0',
            'NoMDEntryTypes': self.NoMDET,
            'NoRelatedSym': self.NoRS
        }

    def m_d_r_t(self) -> dict:
        return {
            'MDReqID': sf.generate_client_order_id(7),
            'SubscriptionRequestType': '1',
            'MDUpdateType': '0',
            'MarketDepth': '1',
            'NoMDEntryTypes': self.NoMDET
        }

    def m_d_r_t2(self) -> dict:
        return {
            'MDReqID': sf.generate_client_order_id(7),
            'SubscriptionRequestType': '0',
            'MarketDepth': '1',
            'NoRelatedSym': self.NoRS
        }
