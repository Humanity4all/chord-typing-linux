"""SwitchBoard."""


def _idle(state_machine, switch_states, index):
    """
    No switches are pressed.

    press -> _one_switch
    hold -> invalid
    release -> invalid
    """
    if switch_states[index] == 0:
        # release
        # invalid in this context, but invalid keystates happen,
        # for example if a key is held while harmony is started
        # TODO: issue a warning
        return []
    elif switch_states[index] == 1:
        # press
        state_machine.change_state(_one_switch)
        return [[switch_states, index, 1, False]]
    if switch_states[index] == 3:
        # hold
        return []


def _one_switch(state_machine, switch_states, index):
    """
    One switch is pressed.

    press -> _two_switch
    hold -> nothing
    release -> _idle
    """
    if switch_states[index] == 0:
        # release
        state_machine.change_state(_idle)
        return [
            [switch_states, index, 1, True],
            [switch_states, index, 0, True]]
    elif switch_states[index] == 1:
        # press
        state_machine.change_state(_two_switch)
        return [[switch_states, index, 1, True]]
    elif switch_states[index] == 2:
        # hold
        return [[switch_states, index, 2, False]]


def _one_switch_used(state_machine, switch_states, index):
    """
    One switch is pressed, but is has been used in a chord already.

    press -> _two_switch
    hold -> nothing
    release -> _idle
    """
    if switch_states[index] == 0:
        # release
        state_machine.change_state(_idle)
        return [[switch_states, index, 0, False]]
    elif switch_states[index] == 1:
        # press
        state_machine.change_state(_two_switch)
        return [[switch_states, index, 1, True]]
    elif switch_states[index] == 2:
        # hold
        return [[switch_states, index, 2, False]]


def _two_switch(state_machine, switch_states, index):
    """
    Two switches are pressed.

    press -> _many_switch
    hold -> nothing
    release -> _one_switch_used
    """
    if switch_states[index] == 0:
        # release
        state_machine.change_state(_one_switch_used)
        return [[switch_states, index, 0, True]]
    elif switch_states[index] == 1:
        # press
        state_machine.change_state(_many_switch)
        return [[switch_states, index, 1, False]]
    elif switch_states[index] == 2:
        # hold
        return [[switch_states, index, 2, True]]


def _many_switch(state_machine, switch_states, index):
    """
    More than two switches are or were pressed.

    This state stays active until we can safely return to _idle.
    press -> nothing
    hold -> nothing
    release -> _idle if num_pressed == 0
    """
    if switch_states[index] == 0:
        # release
        if switch_states.count(0) == len(switch_states):
            state_machine.change_state(_idle)
        return [[switch_states, index, 0, False]]
    elif switch_states[index] == 1:
        # press
        return [[switch_states, index, 1, False]]
    elif switch_states[index] == 2:
        # hold
        return [[switch_states, index, 2, False]]


class SwitchBoard(object):

    """Keep track of key states and determine chord state."""

    def __init__(self, config):
        """Store basic info."""
        self._state = _idle
        num_switches = config['config']['n_switches']
        self._switches = []
        for i in range(num_switches):
            self._switches.append(config['config']['switch%d' % i])

        self._switch_states = [0] * num_switches

    def change_state(self, new_state):
        """Change state."""
        self._state = new_state

    def process_event(self, event):
        """
        Act on event.

        Return format:
        list of zero or more events in the form of:
        [
            switch_states(list of ints),
            index_of_change(int),
            event(0=release, 1=press, 2=hold),
            is_chord(bool)
        ]
        """
        index = self._switches.index(event.keycode)
        self._switch_states[index] = event.keystate
        result = self._state(
            self,
            self._switch_states,
            index)

        return result
