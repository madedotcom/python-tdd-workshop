from expects import expect, equal, raise_error


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
        for stock in self.stocks:
            try:
                return Allocation(stock, line)
            except AllocationError:
                pass


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
        self.stock = Stock(sku='🐄 ', qty=10)
        self.line = Line(sku='🐄 ', qty=10)
        self.allocation = Allocation(self.stock, self.line)

    def should_allocate_them(self):
        expect(self.allocation.line).to(equal(self.line))
        expect(self.allocation.stock).to(equal(self.stock))


class When_we_allocate_stock_it_cannot_be_different_sku:

    def given_stock_and_line_of_different_sku(self):
        self.stock = Stock(sku='🐄 ', qty=10)
        self.line = Line(sku='B', qty=10)

    def should_not_allocate(self):
        def allocate():
            Allocation(self.stock, self.line)
        expect(allocate).to(raise_error(AllocationError))


class When_we_allocate_the_stock_level_should_decrease:

    def given_stock_and_one_line(self):
        self.stock = Stock(sku='🐄 ', qty=10)
        self.line = Line(sku='🐄 ', qty=2)
        self.allocation = Allocation(self.stock, self.line)

    def should_decrease_stock_level(self):
        expect(self.stock.qty).to(equal(8))


class When_we_allocate_to_insufficient_stock:

    def given_stock_and_one_line(self):
        self.stock = Stock(sku='🐄 ', qty=1)
        self.line = Line(sku='🐄 ', qty=2)

    def should_not_allocate(self):
        def allocate():
            Allocation(self.stock, self.line)
        expect(allocate).to(raise_error(AllocationError))


class When_we_allocate_a_sale_order_line_on_product:

    def given_a_product_with_stock_and_one_line(self):
        self.stock = Stock(sku='🐄 ', qty=10)
        self.product = Product(
            sku='🐄 ',
            stocks=[self.stock],
        )
        self.line = Line(sku='🐄 ', qty=2)
        self.product.allocate_line(self.line)

    def should_allocate(self):
        expect(self.stock.qty).to(equal(8))


class When_we_allocate_a_line_to_a_product_with_more_stocks:

    def given_a_product_with_stocks(self):
        self.stock1 = Stock(sku='🐄 ', qty=5)
        self.stock2 = Stock(sku='🐄 ', qty=10)
        self.product = Product(
            sku='🐄 ',
            stocks=[self.stock1, self.stock2],
        )
        self.line = Line(sku='🐄 ', qty=6)
        self.product.allocate_line(self.line)

    def should_allocate_at_the_first_available(self):
        expect(self.stock1.qty).to(equal(5))
        expect(self.stock2.qty).to(equal(4))


class FakeUnitOfWork:

    def __init__(self, fixtures):
        self.committed = False
        self.rolled_back = False
        self.products = fixtures

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class FakeUnitOfWorkManager:

    def __init__(self, fixtures):
        self.sess = FakeUnitOfWork(fixtures)

    def start(self):
        return self.sess

    @property
    def committed(self):
        return self.sess.committed

    @property
    def availability(self):
        return self.sess.availability

    @availability.setter
    def availability(self, v):
        self.sess.availability = v


class CreateStockCommand:

    def __init__(self, sku, qty):
        self.sku = sku
        self.qty = qty


class CreateStockCommandHandler:

    def __call__(self, cmd):
        with self.uow.start() as tx:
            product = tx.products.get(cmd.sku)
            stock = Stock(sku=cmd.sku, qty=cmd.qty)
            product.stocks.append(stock)
            tx.commit()


class When_we_have_a_command_that_we_pass_to_a_handler:

    def given_a_command_and_a_handler(self):

        self.product = Product(
            sku='🐄 ',
            stocks=[],
        )
        command = CreateStockCommand(sku='🐄 ', qty=1)
        handler = CreateStockCommandHandler()
        self.manager = FakeUnitOfWorkManager(fixtures={'🐄 ': self.product})
        handler.uow = self.manager
        handler(command)

    def then_stock_is_created(self):
        expect(self.product.stocks[0].qty).to(equal(1))
        expect(self.manager.committed).to(equal(True))
