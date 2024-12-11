import os
import time
from ebinexpy import Ebinex

email = os.environ.get("EBINEX_EMAIL")
password = os.environ.get("EBINEX_PASSWORD")

client = Ebinex(email, password, keep=True)
while True:
    time.sleep(10)
    print(client.balance.amount)