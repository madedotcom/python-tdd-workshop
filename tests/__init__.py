import datetime

from contexts import catch
from expects import *

from batches import Stock, Inventory, SaleOrderLine, InsufficientStockError


today = datetime.date.today()

class When_allocating_an_order_line_to_a_stock:

    def given_a_stock_and_a_line(self):
        self.stock = Stock(3, today)
        self.inventory = Inventory([
            self.stock
        ])
        self.line = SaleOrderLine(1)

    def because_we_allocate_a_sale_order_line_to_the_stock(self):
        self.inventory.allocate(self.line)

    def it_should_reduce_the_quantity_available(self):
        expect(self.inventory.available).to(equal(2))


class When_reducing_a_stock_below_zero:

    def given_a_stock(self):
        self.stock = Stock(0, today)

    def because_we_reduce(self):
        self.exn = catch(self.stock.allocate, SaleOrderLine(1))

    def then_it_should_raise_insufficient_stock(self):
        expect(self.exn).to(be_an(InsufficientStockError))


class When_allocating_an_order_line_to_an_inventory:

    def given_multiple_stock_and_a_line(self):
        self.inventory = Inventory([
            Stock(1, today),
            Stock(2, today)
        ])
        self.line = SaleOrderLine(2)

    def because_we_allocate_the_line(self):
        self.inventory.allocate(self.line)

    def it_should_reduce_the_available_stock(self):
        expect(self.inventory.available).to(equal(1))


class When_inventory_has_multiple_valid_stocks:

    def given_two_stock_with_different_dates(self):
        self.earlier = Stock(2, datetime.date(2015,11,1))
        self.later = Stock(2, datetime.date(2015,12,1))

        self.inventory = Inventory([
            self.later,
            self.earlier
        ])
        self.line = SaleOrderLine(2)

    def because_allocation(self):
        self.inventory.allocate(self.line)

    def it_should_allocate_the_earliest_available_stock(self):
        expect(self.earlier.quantity).to(equal(0))

    def it_shouldnt_allocate_to_the_latest_stock(self):
        expect(self.later.quantity).to(equal(2))


class When_allocating_the_same_line_twice:

    def given_an_inventory(self):
        self.inventory = Inventory([
            Stock(3, today),
            Stock(1, today)
        ])
        self.line = SaleOrderLine(1)

    def because_we_allocate_a_line_twice(self):
        self.inventory.allocate(self.line)
        self.inventory.allocate(self.line)

    def it_should_only_allocate_once(self):
        expect(self.inventory.available).to(equal(3))


class When_cancelling_a_line:

    def given_a_line_allocated_to_stock(self):
        self.stock = Stock(3, today)
        self.inventory = Inventory([
            self.stock
        ])
        self.line = SaleOrderLine(1)
        self.inventory.allocate(self.line)

    def because_we_cancel_the_line(self):
        self.inventory.cancel(self.line)

    def it_should_be_deallocated(self):
        expect(self.line.allocated_stock).to(be(None))

    def the_quantity_should_be_increased(self):
        expect(self.stock.quantity).to(equal(3))
        expect(self.inventory.available).to(equal(3))


class When_shipments_are_expected_into_inventory:

    def given_an_empty_inventory(self):
        self.inventory = Inventory([])

    def because_a_new_shipment_is_expected(self):
        self.inventory.expect(Stock(1, today))

    def it_should_add_a_stock_to_the_inventory(self):
        expect(self.inventory.available).to(equal(1))


class When_doesnt_have_sufficient_stock:

    def given_an_inventory_with_two_incoming_stocks_and_a_big_line(self):
        self.stock_a = Stock(3, today)
        self.stock_b = Stock(3, today)
        self.inventory = Inventory([self.stock_a, self.stock_b])
        self.line = SaleOrderLine(5)

    def because_allocation(self):
        self.exn = catch(self.inventory.allocate, self.line)

    def then_big_line_couldnt_be_allocated(self):
        expect(self.exn).to(be_an(InsufficientStockError))


class When_unload_a_stock_to_inventory:

    def given_an_inventory_with_two_incoming_stocks_and_a_big_line(self):
        self.stock_a = Stock(3, today)
        self.stock_b = Stock(3, today)
        self.inventory = Inventory([self.stock_a, self.stock_b])
        self.line = SaleOrderLine(5)

    def because_both_get_unloaded(self):
        self.inventory.unload(self.stock_a)
        self.inventory.unload(self.stock_b)

    def then_big_line_could_be_allocated(self):
        self.inventory.allocate(self.line)
