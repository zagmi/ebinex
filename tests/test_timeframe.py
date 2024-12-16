import ebinexpy.iykyk as tp


def test_timeframe(client: tp.Ebinex):
    initial = client.timeframe
    timeframes = list(tp.Timeframe)

    for new in timeframes:
        if new != initial:
            client.change_timeframe(new)
            assert client.timeframe != initial

