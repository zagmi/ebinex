import ebinexpy.iykyk as tp
import numpy.random as random


def test_trade(client: tp.Ebinex):
    environment = tp.Environment.TEST
    client.change_environment(environment)
    direction = random.choice(list(tp.Direction))
    order, wait = client.order(1, direction=direction)
    wait(until=[tp.Statuses.WIN, tp.Statuses.LOSE])
    assert client.environment == order.environment
