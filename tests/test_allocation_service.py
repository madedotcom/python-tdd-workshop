from expects import expect, equal, raise_error

# Exceptions
class AllocationError(Exception):
    pass

# Relationship between stock and line
# Warehouse A stock
# Warehouse B stock
# Shipment A1 stock
# ...

class Stock:
    def __init__(self, sku, qty):
        self.sku = sku
        self.qty = qty

    def decrease_qty(self, delta):
        self.qty -= delta


class Line:
    def __init__(self, sku, qty):
        self.sku = sku
        self.qty = qty


class Product:
    def __init__(self, sku, stocks):
        self.sku = sku
        self.stocks = stocks

    def allocate_line(self, line):
        Allocation(self.stocks[0], line)


class Allocation:
    def __init__(self, stock, line):
        if stock.sku != line.sku:
            err_msg = 'Can not allocate stock and line with different SKUs'
            raise AllocationError(err_msg)

        if stock.qty < line.qty:
            err_msg = 'Not enough stock'
            raise AllocationError(err_msg)

        self.stock = stock
        self.line = line
        stock.decrease_qty(line.qty)


class When_we_have_one_stock_and_one_line_allocate_them:
    def given_stock_and_one_line(self):
        self.stock = Stock(sku='A', qty=10)
        self.line = Line(sku='A', qty=10)
        self.allocation = Allocation(self.stock, self.line)

    def should_allocate_them(self):
        expect(self.allocation.line).to(equal(self.line))
        expect(self.allocation.stock).to(equal(self.stock))


class When_we_allocate_stock_it_cannot_be_different_sku:

    def given_stock_and_line_of_different_sku(self):
        self.stock = Stock(sku='A', qty=10)
        self.line = Line(sku='B', qty=10)

    def should_not_allocate(self):
        def allocate():
            Allocation(self.stock, self.line)
        expect(allocate).to(raise_error(AllocationError))


class When_we_allocate_the_stock_level_should_decrease:
    def given_stock_and_one_line(self):
        self.stock = Stock(sku='A', qty=10)
        self.line = Line(sku='A', qty=2)
        self.allocation = Allocation(self.stock, self.line)

    def should_decrease_stock_level(self):
        expect(self.stock.qty).to(equal(8))


class When_we_allocate_to_insufficient_stock:
    def given_stock_and_one_line(self):
        self.stock = Stock(sku='A', qty=1)
        self.line = Line(sku='A', qty=2)

    def should_not_allocate(self):
        def allocate():
            Allocation(self.stock, self.line)
        expect(allocate).to(raise_error(AllocationError))


class When_we_allocate_a_sale_order_line_on_product:
    def given_a_product_with_stock_and_one_line(self):
        self.stock = Stock(sku='A', qty=10)
        self.product = Product(
            sku='A',
            stocks=[self.stock],
        )
        self.line = Line(sku='A', qty=2)
        self.product.allocate_line(self.line)

    def should_allocate(self):
        expect(self.stock.qty).to(equal(8))


class When_we_allocate_a_line_to_a_product_with_more_stocks:
    def given_a_product_with_stocks(self):
        self.stock1 = Stock(sku='A', qty=5)
        self.stock2 = Stock(sku='A', qty=10)
        self.product = Product(
            sku='A',
            stocks=[self.stock1, self.stock2],
        )
        self.line = Line(sku='A', qty=6)
        self.product.allocate_line(self.line)

    def should_allocate_at_the_first_available(self):
        expect(self.stock1.qty).to(equal(5))
        expect(self.stock2.qty).to(equal(4))
# class WarehouseStock(Stock):
# property (weight)
#    weight = 1

# class Stock (location)
     # location weight (1, 2)
     # qty

# class Line
# class Allocation

#
#we have stock in warehouse for sku A
#we have stock in batch for sku A
#
#self.warehouse``
#
#when I want to allocate 
#I want the warehouse's qty to decrease if there is qty
