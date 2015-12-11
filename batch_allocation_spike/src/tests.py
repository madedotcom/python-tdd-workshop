from contexts import catch
from expects import expect, be_above, be_below, equal, be_true, be_false, be_an


class InsuficientStock(Exception):

    pass


class LineNotAllocatedError(Exception):

    pass


class Stock:

    def __init__(self, quantity):
        self.quantity = quantity

    def allocate(self, line):
        if self.quantity < line.quantity:
            raise InsuficientStock()

        line.allocate_to(self)
        self.quantity -= line.quantity

    def deallocate(self, line):
        line.deallocate_from(self)
        self.quantity += line.quantity


class Line:

    def __init__(self, quantity):
        self.quantity = quantity
        self._allocated_stock = None

    def is_allocated(self, stock):
        return self._allocated_stock is not None

    def allocate_to(self, stock):
        self._allocated_stock = stock

    def deallocate_from(self, stock):
        if self._allocated_stock is None:
            raise LineNotAllocatedError()
        self._allocated_stock = None

    def is_allocated_to(self, stock):
        return self._allocated_stock == stock


class CompoundStock:

    def __init__(self, stocks):
        self._stocks = stocks

    def allocate(self, line):
        for stock in self._stocks:
            try:
                stock.allocate(line)
            except InsuficientStock:
                continue
            else:
                return
        else:
            raise


class When_allocating_a_line_to_stock:

    def given_stock(self):
        self.stock = Stock(2)
        self.line = Line(1)

    def when_we_try_to_allocate(self):
        self.stock.allocate(self.line)

    def it_should_be_allocated(self):
        expect(self.line.is_allocated(self.stock)).to(be_true)

    def the_available_stock_level_should_be_reduced(self):
        expect(self.stock.quantity).to(equal(1))


class When_not_enough_stock:

    def given_too_small_stock(self):
        self.stock = Stock(2)
        self.line = Line(3)

    def when_we_try_to_allocate(self):
        try:
            self.stock.allocate(self.line)
        except InsuficientStock:
            self.exception_raised = True

    def it_should_not_be_allocated(self):
        expect(self.line.is_allocated(self.stock)).to(be_false)
        expect(self.exception_raised).to(be_true)


class When_allocating_to_multiple_stocks:

    def given_compound_stock(self):
        self.first = Stock(2)
        self.second = Stock(3)
        self.third = Stock(3)
        self.stock = CompoundStock([self.first, self.second, self.third])
        self.line = Line(3)

    def when_we_allocate(self):
        self.stock.allocate(self.line)

    def it_should_allocate_to_the_first_available_stock(self):
        expect(self.line.is_allocated_to(self.first)).to(be_false)
        expect(self.line.is_allocated_to(self.second)).to(be_true)
        expect(self.line.is_allocated_to(self.third)).to(be_false)


class When_deallocating_a_line_to_stock:

    def given_partially_allocated_stock(self):
        self.stock = Stock(2)
        self.line = Line(1)
        self.stock.allocate(self.line)

    def when_we_deallocate(self):
        self.stock.deallocate(self.line)

    def it_should_be_deallocated(self):
        expect(self.line.is_allocated(self.stock)).to(be_false)

    def the_available_stock_level_should_be_restored(self):
        expect(self.stock.quantity).to(equal(2))


class When_deallocating_line_that_was_never_allocated:

    def given_stock(self):
        self.allocated_stock = Stock(2)
        self.not_allocated_stock = Stock(2)
        self.line = Line(1)
        self.allocated_stock.allocate(self.line)

    def when_we_try_to_deallocate_a_line_never_allocated(self):
        self.exc = catch(self.not_allocated_stock.deallocate, self.line)

    def it_should_fail(self):
        expect(self.exc).to(be_an(LineNotAllocatedError))
