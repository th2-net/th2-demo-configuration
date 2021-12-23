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
        self.request1 = self.m_d_r_f()
        self.request2 = self.m_d_r_t()
        self.request3 = self.m_d_r_t2()
        self.request4 = self.m_d_r_us()

    def m_d_r_f(self) -> dict:
        return {
            'MDReqID': "34965",
            'SubscriptionRequestType': '0',
            'MarketDepth': '0',
            'NoMDEntryTypes': '2',
            'MDEntryType': '7',
            'MDEntryType': '8',
            'NoRelatedSym': '3',
            'Symbol': 'Instrument1',
            'Symbol': 'Instrument2',
            'Symbol': 'Instrument3'
        }

    def m_d_r_t(self) -> dict:
        return {
            'MDReqID': "34966",
            'SubscriptionRequestType': '1',
            'MDUpdateType': '0',
            'MarketDepth': '1',
            'NoMDEntryTypes': '2',
            'MDEntryType': '7',
            'MDEntryType': '8',
            'NoRelatedSym': '3',
            'Symbol': 'Instrument1',
            'Symbol': 'Instrument2',
            'Symbol': 'Instrument3'
        }

    def m_d_r_us(self) -> dict:
        return {
            'MDReqID': "34966",
            'SubscriptionRequestType': '2',
            'MarketDepth': '0',
            'NoMDEntryTypes': '0',
            'MDEntryType': None,
            'NoRelatedSym': '0',
            'Component Block': None
        }

    def m_d_r_t2(self) -> dict:
        return {
            'MDReqID': "34975",
            'SubscriptionRequestType': '0',
            'MarketDepth': '1',
            'NoMDEntryTypes': '2',
            'MDEntryType': '7',
            'MDEntryType': '8',
            'NoRelatedSym': '3',
            'Symbol': 'Instrument1',
            'Symbol': 'Instrument2',
            'Symbol': 'Instrument3'
        }

