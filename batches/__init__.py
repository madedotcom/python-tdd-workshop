class InsufficientStockError(Exception):
    pass


class Stock:

    def __init__(self, size, unload_date):
        self.size = size
        self.unload_date = unload_date
        self.allocations = []

    def allocate(self, line):
        if not self.can_be_allocated(line):
            raise InsufficientStockError()
        if line.allocated_stock is None:
            self.allocations.append(line)
            line.allocated_stock = self

    def cancel(self, line):
        self.allocations.remove(line)
        line.allocated_stock = None

    def can_be_allocated(self, line):
        return self.quantity >= line.quantity

    @property
    def quantity(self):
        return self.size - sum(line.quantity for line in self.allocations)


class Inventory:

    def __init__(self, stocks):
        self.stocks = stocks
        self._sort()

    def allocate(self, line):
        for stock in self.stocks:
            if stock.can_be_allocated(line):
                stock.allocate(line)
                return
        raise InsufficientStockError()

    def cancel(self, line):
        line.allocated_stock.cancel(line)

    @property
    def available(self):
        return sum(s.quantity for s in self.stocks)

    def expect(self, stock):
        self.stocks.append(stock)
        self._sort()

    def _sort(self):
        self.stocks = sorted(self.stocks, key=lambda s: s.unload_date)


class SaleOrderLine:

    def __init__(self, quantity):
        self.quantity = quantity
        self.allocated_stock = None
