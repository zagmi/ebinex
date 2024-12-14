import queue


class Signals:
    order = queue.Queue()
    trade = queue.Queue()
    balance = queue.Queue()
