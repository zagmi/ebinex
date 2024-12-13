import os
import time
from ebinexpy import Ebinex
from ebinexpy.iykyk import Environment

email = os.environ.get("EBINEX_EMAIL")
password = os.environ.get("EBINEX_PASSWORD")

client = Ebinex(email, password, keep=True)
for env in list(Environment):
    client.change_environment(env)
    print(client.balance.amount)