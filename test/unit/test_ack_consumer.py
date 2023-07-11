from simulator.ack_consumer import Acknowledger


def test_not_complete():
    acker = Acknowledger({})
    assert not acker.check_update_cache("1", "topic1")


def test_complete():
    acker = Acknowledger({})
    acker.check_update_cache("1", "topic1")
    acker.check_update_cache("1", "topic2")
    assert acker.check_update_cache("1", "topic3")
    

def test_persistence():
    cache = {}
    ack1 = Acknowledger(cache)
    ack1.check_update_cache("1", "topic1")
    del ack1
    ack2 = Acknowledger(cache)
    ack2.check_update_cache("1", "topic2")
    assert ack2.check_update_cache("1", "topic3")