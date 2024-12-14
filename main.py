import os
import time
from ebinexpy import Ebinex
from ebinexpy.iykyk import Environment, Direction

email = "miguelsantiago1940@gmail.com"
password = "Santiago2024"

client = Ebinex(email, password, keep=True)
client.change_environment(Environment.TEST)
time.sleep(10)
client.order(10, direction=Direction.BULL)
time.sleep(2*60)