import queue


class Signals:
    book = queue.Queue()
    order = queue.Queue()
    trade = queue.Queue()
    balance = queue.Queue()
