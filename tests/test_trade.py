import numpy.random as random
import ebinexpy.iykyk as tp


def test_trade(client: tp.Ebinex):
    client.change_environment(tp.Environment.TEST)
    direction = random.choice(list(tp.Direction))
    client.order(1, direction=direction)
    assert client.balance is not None
