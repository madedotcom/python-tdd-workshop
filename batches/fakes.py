import logging

class FakeUnitOfWork:

    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class FakeUnitOfWorkManager:

    def __init__(self):
        self.sess = FakeUnitOfWork()

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

class SpyLog(logging.StreamHandler):

    def __init__(self):
        self._logs = []
        self.setLevel(logging.DEBUG)
        self.filters = []
        self.lock = None
        self.formatter = logging.Formatter()

    def emit(self, record):
        self.formatter.format(record)
        self._logs.append(record)

    def capture(self):
        return SpyLogContextManager(self)

    @property
    def errors(self):
        return [r for r in self._logs if r.levelname == "ERROR"]

    @property
    def infos(self):
        return [r for r in self._logs if r.levelname == "INFO"]

    @property
    def warnings(self):
        return [r for r in self._logs if r.levelname == "WARNING"]


class SpyLogContextManager:

    def __init__(self, log):
        self._log = log

    def __enter__(self):
        self._old_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.NOTSET)
        logging.getLogger().addHandler(self._log)

    def __exit__(self, type, value, traceback):
        logging.getLogger().setLevel(self._old_level)
        logging.getLogger().removeHandler(self._log)
        print("logs:")
        for r in self._log._logs:
            print(r.levelname + " " + r.message)


class FakeMessageBus:

    def __init__(self):
        self.messages = []
        self.deferred_messages = []

    def handle(self, e):
        self.messages.append(e)

    def defer(self, msg, datetime, correlation_id):
        self.deferred_messages.append((msg, datetime))

    def clear(self):
        self.messages = []


class FakeEventPublisher:

    def __init__(self):
        self.posted_events = []

    def publish(self, stream, evt, correlation_id):
        self.posted_events.append(evt)

    def __iter__(self):
        for e in self.posted_events:
            yield e

    def __len__(self):
        return len(self.posted_events)
