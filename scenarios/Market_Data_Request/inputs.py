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
        self.request4 = self.m_d_r_us()


    def m_d_r_mdet(self) -> list:
        return [
            {'MDEntryType': '7'},
            {'MDEntryType': '8'}
        ]

    def m_d_r_nrs(self) -> list:
        return [
            {'Instrument': {'Symbol': 'Instrument1'}},
            {'Instrument': {'Symbol': 'Instrument2'}},
            {'Instrument': {'Symbol': 'Instrument3'}}
        ]

    def m_d_r_f(self) -> dict:
        return {
            'MDReqID': "34965",
            'SubscriptionRequestType': '0',
            'MarketDepth': '0',
            'NoMDEntryTypes': self.NoMDET,
            'NoRelatedSym': self.NoRS
        }

    def m_d_r_t(self) -> dict:
        return {
            'MDReqID': "34966",
            'SubscriptionRequestType': '1',
            'MDUpdateType': '0',
            'MarketDepth': '1',
            'NoMDEntryTypes': self.NoMDET,
            'NoRelatedSym': self.NoRS
        }

    def m_d_r_us(self) -> dict:
        return {
            'MDReqID': "34966",
            'SubscriptionRequestType': '2',
            'MarketDepth': '0',
            'NoMDEntryTypes': [],
            'NoRelatedSym': []
        }

    def m_d_r_t2(self) -> dict:
        return {
            'MDReqID': "34975",
            'SubscriptionRequestType': '0',
            'MarketDepth': '1',
            'NoMDEntryTypes': self.NoMDET,
            'NoRelatedSym': self.NoRS
        }
