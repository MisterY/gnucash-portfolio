"""
Asset Allocation module
"""
from decimal import Decimal
try: import simplejson as json
except ImportError: import json
import os
from os import path
#from logging import log, DEBUG
from piecash import Book, Commodity, Price
from gnucash_portfolio.accountaggregate import AccountAggregate, AccountsAggregate
from gnucash_portfolio.securitiesaggregate import SecurityAggregate, SecuritiesAggregate
from gnucash_portfolio.currencyaggregate import CurrencyAggregate


class AssetBase:
    """Base class for asset group & class"""
    def __init__(self, json_node):
        self.data = json_node
        # reference to parent object
        self.parent: AssetClass = None

        # Set allocation %.
        self.allocation = Decimal(0)
        if "allocation" in json_node:
            self.allocation = Decimal(json_node["allocation"])
        else:
            self.allocation = Decimal(0)
        # How much is currently allocated, in %.
        self.curr_alloc = Decimal(0)
        # Difference between allocation and allocated.
        self.alloc_diff = Decimal(0)
        # Difference in percentages of allocation
        self.alloc_diff_perc = Decimal(0)

        # Current value in currency.
        self.alloc_value = Decimal(0)
        # Allocated value
        self.curr_value = Decimal(0)
        # Difference between allocation and allocated
        self.value_diff = Decimal(0)

        # Threshold. Expressed in %.
        self.threshold = Decimal(0)
        self.over_threshold = False
        self.under_threshold = False

    @property
    def name(self):
        """Group name"""
        if not self.data:
            return ""

        if "name" in self.data:
            return self.data["name"]
        else:
            return ""

    @property
    def fullname(self):
        """ includes the full path with parent names """
        prefix = ""
        if self.parent:
            if self.parent.fullname:
                prefix = self.parent.fullname + ":"
        else:
            # Only the root does not have a parent. In that case we also don't need a name.
            return ""

        return prefix + self.name


class AssetGroup(AssetBase):
    """Group contains other groups or asset classes"""
    def __init__(self, json_node):
        super().__init__(json_node)
        self.classes = []


class AssetClass(AssetBase):
    """Asset Class contains stocks"""
    def __init__(self, json_node):
        super().__init__(json_node)

        # For cash asset class
        self.root_account = None

        self.stocks: list(Stock) = []
        # parse stocks
        if "stocks" not in json_node:
            return

        for symbol in json_node["stocks"]:
            stock = Stock(symbol)
            self.stocks.append(stock)


class Stock:
    """Stock link"""
    def __init__(self, symbol: str):
        """Parse json node"""
        self.symbol = symbol

        # Quantity (number of shares)
        self.quantity = Decimal(0)

        # Price (last known)
        self.price = Decimal(0)

    @property
    def value(self) -> Decimal:
        """Value of the shares. Value = Quantity * Price"""
        return self.quantity * self.price


class _AllocationLoader:
    """ Parses the allocation settings and loads the current allocation from database """
    def __init__(self, currency: Commodity, book: Book):
        self.currency = currency
        self.book = book
        self.asset_allocation = None

    def load_asset_allocation_model(self):
        """ Loads Asset Allocation model for display """
        self.asset_allocation = self.load_asset_allocation_config()
        # Populate values from database.
        self.__load_values_into(self.asset_allocation)

        # calculate percentages
        total_value = self.asset_allocation.curr_value
        self.__calculate_percentages(self.asset_allocation, total_value)

        # Return model.
        model = {
            'allocation': self.asset_allocation,
            'currency': self.currency.mnemonic
        }

        return model

    def load_asset_allocation_config(self) -> AssetGroup:
        """ Loads only the configuration from json """
                # read asset allocation file
        root_node = self.__load_asset_allocation_config_json()
        result = self.__parse_node(root_node)
        return result

    def __load_values_into(self, asset_group: AssetGroup):
        """
        Populates the asset class values from the database.
        Reads the stock values and fills the asset classes.
        """
        # iterate recursively until an Asset Class is found.
        for child in asset_group.classes:
            if isinstance(child, AssetGroup):
                self.__load_values_into(child)

            if isinstance(child, AssetClass):
                # Add all the stock values.
                svc = SecuritiesAggregate(self.book)
                for stock in child.stocks:
                    # then, for each stock, calculate value
                    symbol = stock.symbol
                    cdty = svc.get_stock(symbol)
                    stock_svc = SecurityAggregate(self.book, cdty)

                    # Quantity
                    quantity = stock_svc.get_quantity()
                    stock.quantity = quantity

                    # last price
                    last_price: Price = stock_svc.get_last_available_price()
                    stock.price = last_price.value

                    # Value
                    stock_value = last_price.value * quantity
                    if last_price.currency != self.currency:
                        # Recalculate into the base currency.
                        stock_value = self.get_value_in_base_currency(
                            stock_value, last_price.currency)

                    child.curr_value += stock_value

            if child.name == "Cash":
                # load cash balances
                child.curr_value = self.get_cash_balance(child.root_account)

            asset_group.curr_value += child.curr_value

    def get_value_in_base_currency(self, value: Decimal, currency: Commodity) -> Decimal:
        """ Recalculates the given value into base currency """
        base_cur = self.currency

        svc = CurrencyAggregate(self.book, currency)
        last_price = svc.get_latest_rate(base_cur)

        result = value * last_price.value

        return result

    def get_cash_balance(self, root_account_name: str) -> Decimal:
        """ Loads investment cash balance in base currency """
        svc = AccountsAggregate(self.book)
        root_account = svc.get_by_fullname(root_account_name)
        acct_svc = AccountAggregate(self.book, root_account)
        result = acct_svc.get_cash_balance_with_children(root_account, self.currency)
        return result

    def __parse_node(self, node):
        """Creates an appropriate entity for the node. Recursive."""
        entity = None

        if "classes" in node:
            entity = AssetGroup(node)
            # Process child nodes
            for child_node in node["classes"]:
                child = self.__parse_node(child_node)

                child.parent = entity
                entity.classes.append(child)

        if "stocks" in node:
            # This is an Asset Class
            entity = AssetClass(node)

        # Cash
        if node["name"] == "Cash":
            # Cash node
            entity = AssetClass(node)
            entity.root_account = node["rootAccount"]

        # Threshold
        if "threshold" in node:
            threshold = node["threshold"].replace('%', '')
            entity.threshold = Decimal(threshold)

        return entity

    def __load_asset_allocation_config_json(self):
        """
        Loads asset allocation from the file.
        Returns the list of asset classes.
        """
        allocation_file = path.abspath(path.join(
            os.path.dirname(os.path.realpath(__file__)), "../config/assetAllocation.json"))
        with open(allocation_file, 'r') as json_file:
            allocation_json = json.load(json_file)

        return allocation_json

    def __calculate_percentages(self, asset_group: AssetGroup, total: Decimal):
        """ calculate the allocation percentages """
        if not hasattr(asset_group, "classes"):
            return

        for child in asset_group.classes:
            # calculate
            # allocation is read from the config.
            child.curr_alloc = child.curr_value * 100 / total
            child.alloc_diff = child.curr_alloc - child.allocation
            child.alloc_diff_perc = child.alloc_diff * 100 / child.allocation

            # Values
            child.alloc_value = total * child.allocation / 100
            # Value is calculated during load.
            #child.curr_value = total * child.curr_alloc / 100
            child.value_diff = child.curr_value - child.alloc_value

            # Threshold
            child.over_threshold = abs(child.alloc_diff_perc) > self.asset_allocation.threshold

            self.__calculate_percentages(child, total)
        return


class AssetAllocationAggregate():
    """ The main service class """
    def __init__(self, book: Book):
        self.book = book
        self.root: AssetGroup = None

    def load_full_model(self, currency: Commodity):
        """ Populates complete Asset Allocation tree """
        loader = _AllocationLoader(currency, self.book)
        return loader.load_asset_allocation_model()

    def load_config_only(self, currency: Commodity):
        """ Loads only the asset allocation tree from configuration """
        loader = _AllocationLoader(currency, self.book)
        return loader.load_asset_allocation_config()

    def find_class_by_fullname(self, fullname: str):
        """ Locates the asset class by fullname. i.e. Equity:International """
        found = self.__get_by_fullname(self.root, fullname)
        return found

    def __get_by_fullname(self, asset_class, fullname: str):
        """ Recursive function """
        if asset_class.fullname == fullname:
            return asset_class

        if not hasattr(asset_class, "classes"):
            return None

        for child in asset_class.classes:
            found = self.__get_by_fullname(child, fullname)
            if found:
                return found

        return None
