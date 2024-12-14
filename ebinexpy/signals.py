import queue
import threading


class Signals:
    order = queue.Queue()
    trade = queue.Queue() 
    balance = queue.Queue()    

