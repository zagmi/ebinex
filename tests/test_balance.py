import ebinexpy.iykyk as tp


def test_balance(client: tp.Ebinex):
    for env in list(tp.Environment):
        client.change_environment(env)
        assert client.account.default_coin_balance
