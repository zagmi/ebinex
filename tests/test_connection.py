import ebinexpy.iykyk as tp


def test_conn(client: tp.Ebinex):
    assert client.connected
