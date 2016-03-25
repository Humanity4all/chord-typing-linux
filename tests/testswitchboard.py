"""Test SwitchBoard."""
from nose.tools import assert_list_equal
from switchboard import SwitchBoard


def test_switch_board():
    """
    Test SwitchBoard.

    This is a rather basic test, by no means exhaustive.
    """
    config = {'config': {
        'n_switches': 3,
        'switch0': 23,
        'switch1': 24,
        'switch2': 25}}
    switch_board = SwitchBoard(config)

    class Event(object):

        """Mock event."""

        def __init__(self, key_code, key_state):
            self.keycode = key_code
            self.keystate = key_state

    # we're in idle. a switch press results in a switch to one_switch
    result = switch_board.process_event(Event(23, 1))
    expected = [[[1, 0, 0], 0, 1, False]]
    assert_list_equal(result, expected)

    # we're in one_switch, going to two_switch
    result = switch_board.process_event(Event(24, 1))
    expected = [[[1, 1, 0], 1, 1, True]]
    assert_list_equal(result, expected)

    # holding
    result = switch_board.process_event(Event(23, 2))
    expected = [[[2, 1, 0], 0, 2, True]]
    assert_list_equal(result, expected)

    # now we're in two_switch, going into many_switch
    result = switch_board.process_event(Event(25, 1))
    expected = [[[2, 1, 1], 2, 1, False]]
    assert_list_equal(result, expected)

    # holding
    result = switch_board.process_event(Event(25, 2))
    expected = [[[2, 1, 2], 2, 2, False]]
    assert_list_equal(result, expected)

    # going back to idle
    result = switch_board.process_event(Event(25, 0))
    expected = [[[2, 1, 0], 2, 0, False]]
    assert_list_equal(result, expected)

    result = switch_board.process_event(Event(24, 0))
    expected = [[[2, 0, 0], 1, 0, False]]
    assert_list_equal(result, expected)

    result = switch_board.process_event(Event(23, 0))
    expected = [[[0, 0, 0], 0, 0, False]]
    assert_list_equal(result, expected)
