class Signals:
    import threading
    trade = threading.Event()
    balance = threading.Event()
    connected = threading.Event()