class DeliveryMDP(object):
    def _get_state_record(self, state):
        components = state.split(':')
        return (components[0], components[1] == 'True')

    def _compute_states(self):
        location_states = list(self.world_map['locations'])
        has_package_states = [True, False]
        return [location + ':' + str(has_package) for location in location_states for has_package in has_package_states]

    def _compute_actions(self):
        return list(self.world_map['locations']) + ['PICKUP'] + ['DROPOFF']

    def _compute_transition_probabilities(self):
        transition_probabilities = {state: {action: {successor_state: 0.0 for successor_state in self.state_space} for action in self.action_space} for state in self.state_space}

        for state in self.state_space:
            for action in self.action_space:
                for successor_state in self.state_space:
                    state_record = self._get_state_record(state)
                    successor_state_record = self._get_state_record(successor_state)

                    if action == 'DROPOFF':
                        if (state_record[0] == 'RBR' and not state_record[1]):
                            print(successor_state)
                            print(successor_state_record)
                        if state_record[0] == self.dropoff_location and state_record[0] == successor_state_record[0] and state_record[1] and successor_state_record[1]:
                            transition_probabilities[state][action][successor_state] = 1.0
                            break

                        if state_record[0] == self.dropoff_location and state_record[0] == successor_state_record[0] and not state_record[1] and not successor_state_record[1]:
                            transition_probabilities[state][action][successor_state] = 1.0
                            break

                        if state_record[0] != self.dropoff_location and state_record[0] == successor_state_record[0] and not successor_state_record[1]:
                            transition_probabilities[state][action][successor_state] = 1.0
                            break

                    if action == 'PICKUP':
                        if state_record[0] == self.pickup_location and state_record[0] == successor_state_record[0]:
                            transition_probabilities[state][action][successor_state] = 1.0
                            break

                        if state_record[0] != self.pickup_location and state_record[0] == successor_state_record[0] and state_record[1] == successor_state_record[1]:
                            transition_probabilities[state][action][successor_state] = 1.0
                            break

                    if action in self.world_map['locations']:
                        if (state_record[0] not in self.world_map['paths'] or action == state_record[0]) and state_record[0] == successor_state_record[0] and state_record[1] == successor_state_record[1]:
                            transition_probabilities[state][action][successor_state] = 1.0
                            break

                        if state_record[0] in self.world_map['paths']:
                            if action in self.world_map['paths'][state_record[0]] and successor_state_record[0] == action and state_record[1] == successor_state_record[1]:
                                transition_probabilities[state][action][successor_state] = 1.0
                                break

                            if action not in self.world_map['paths'][state_record[0]] and state_record[0] == successor_state_record[0] and state_record[1] == successor_state_record[1]:
                                transition_probabilities[state][action][successor_state] = 1.0
                                break

        return transition_probabilities

    def _compute_rewards(self):
        rewards = {state: {action: 0.0 for action in self.action_space} for state in self.state_space}

        for state in self.state_space:
            for action in self.action_space:
                state_record = self._get_state_record(state)

                if action == 'PICKUP':
                    rewards[state][action] = -10

                if action == 'DROPOFF':
                    if state_record[0] == self.dropoff_location and state_record[1]:
                        rewards[state][action] = 1000
                    else:
                        rewards[state][action] = -10

                if action in self.world_map['locations']:
                    if state_record[0] in self.world_map['paths'] and action in self.world_map['paths'][state_record[0]]:
                        rewards[state][action] = -self.world_map['paths'][state_record[0]][action]['cost']
                    else:
                        rewards[state][action] = -1000

        return rewards

    def _compute_start_state_probabilities(self):
        return {state: 1.0 / len(self.state_space) for state in self.state_space}

    def __init__(self, world_map, pickup_location, dropoff_location):
        self.world_map = world_map
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location

        self.state_space = self._compute_states()
        self.action_space = self._compute_actions()
        self.transition_probabilities = self._compute_transition_probabilities()
        self.rewards = self._compute_rewards()
        self.start_state_probabilities = self._compute_start_state_probabilities()

    def states(self):
        return self.state_space

    def actions(self):
        return self.action_space

    def transition_function(self, state, action, successor_state):
        return self.transition_probabilities[state][action][successor_state]

    def reward_function(self, state, action):
        return self.rewards[state][action]

    def start_state_function(self, state):
        return self.start_state_probabilities[state]

    def is_goal(self, state):
        return state[0] == self.dropoff_location and state[1]
