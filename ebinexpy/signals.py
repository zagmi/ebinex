class Signals:
    import threading
    balance = threading.Event()
    connected = threading.Event()