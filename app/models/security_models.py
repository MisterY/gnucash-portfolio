""" Models for Securities """

from dataclasses import dataclass


class StockAnalysisInputModel: # pylint: disable=invalid-name
    """ Input model for Stock Analysis """
    symbol: str = None
