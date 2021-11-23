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
        self.request1 = self.m_k_d_f()
        self.request2 = self.m_k_d_t()
        self.request3 = self.m_k_d_us()

    def m_k_d_f(self) -> dict:
        return {
            'MDReqID': "34965",
            'SubscriptionRequestType': '0',
            'MarketDepth': self.input_parameters['MarketDepth'],
            'NoMDEntryTypes': len(self.input_parameters['MDEntryType']),
            'MDEntryType': self.input_parameters['MDEntryType'],
            'NoRelatedSym': len(self.input_parameters['Instruments']),
            'Component Block': self.input_parameters['Instruments'],
        }

    def m_k_d_t(self) -> dict:
        return {
            'MDReqID': "34966",
            'SubscriptionRequestType': '1',
            'MDUpdateType': '0',
            'MarketDepth': self.input_parameters['MarketDepth'],
            'NoMDEntryTypes': len(self.input_parameters['MDEntryType']),
            'MDEntryType': self.input_parameters['MDEntryType'],
            'NoRelatedSym': len(self.input_parameters['Instrument']),
            'Component Block': self.input_parameters['Instrument'],
        }

    def m_k_d_f(self) -> dict:
        return {
            'MDReqID': "34966",
            'SubscriptionRequestType': '2',
            'MarketDepth': '0',
            'NoMDEntryTypes': '0',
            'MDEntryType': None,
            'NoRelatedSym': '0',
            'Component Block': None,
        }

