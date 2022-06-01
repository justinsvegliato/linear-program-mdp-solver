import cplex
import numpy as np


class MemoryMDP:
    def __init__(self, mdp):
        self.states = mdp.states()
        self.actions = mdp.actions()

        self.n_states = len(self.states)
        self.n_actions = len(self.actions)

        self.rewards = np.zeros(shape=(self.n_states, self.n_actions))
        for state in range(self.n_states):
            for action in range(self.n_actions):
                self.rewards[state, action] = mdp.reward_function(self.states[state], self.actions[action])

        self.transition_probabilities = np.zeros(shape=(self.n_states, self.n_actions, self.n_states))
        for state in range(self.n_states):
            for action in range(self.n_actions):
                for successorState in range(self.n_states):
                    self.transition_probabilities[state, action, successorState] = mdp.transition_function(self.states[state], self.actions[action], self.states[successorState])

        self.start_state_probabilities = np.zeros(self.n_states)
        for state in range(self.n_states):
            self.start_state_probabilities[state] = mdp.start_state_function(self.states[state])


def __validate(memory_mdp):
    assert memory_mdp.n_states is not None
    assert memory_mdp.n_actions is not None

    assert memory_mdp.states is not None
    assert memory_mdp.actions is not None
    assert memory_mdp.rewards is not None
    assert memory_mdp.transition_probabilities is not None
    assert memory_mdp.start_state_probabilities is not None

    assert memory_mdp.rewards.shape == (memory_mdp.n_states, memory_mdp.n_actions)
    assert memory_mdp.transition_probabilities.shape == (memory_mdp.n_states, memory_mdp.n_actions, memory_mdp.n_states)
    assert memory_mdp.start_state_probabilities.shape == (memory_mdp.n_states,)


def __set_variables(c, memory_mdp):
    c.variables.add(types=[c.variables.type.continuous] * memory_mdp.n_states)


def __set_objective(c, memory_mdp):
    c.objective.set_linear([(i, memory_mdp.start_state_probabilities[i]) for i in range(memory_mdp.n_states)])
    c.objective.set_sense(c.objective.sense.minimize)


def __set_constraints(program, memory_mdp, gamma):
    lin_expr = []
    rhs = []

    # Each constraint will use all states' variables (as the "next possible states")
    variables = range(memory_mdp.n_states)

    # There is one constraint for each (state, action) pair
    for i in range(memory_mdp.n_states):
        for j in range(memory_mdp.n_actions):
            coefficients = []
            # Each constraint refers to all state variables (as the "next possible states")
            # Each coefficient depends on whether the next possible state is the current state or not
            for k in range(memory_mdp.n_states):
                # If the next possible state is not the current state
                if k != i:
                    coefficient = - gamma * memory_mdp.transition_probabilities[i, j, k]
                # If the next possible is the current state
                else:
                    coefficient = 1 - gamma * memory_mdp.transition_probabilities[i, j, k]
                coefficients.append(coefficient)

            # TODO: It may become necessary to avoid giving CPLEX 0 coefficients altogether.
            # Append linear constraint
            lin_expr.append([variables, coefficients])

            # The constraint's right-hand side is simply the reward
            rhs.append(float(memory_mdp.rewards[i, j]))

    # Add all linear constraints to CPLEX at once
    program.linear_constraints.add(lin_expr=lin_expr, rhs=rhs, senses=["G"] * len(rhs))


def __get_policy(values, memory_mdp, gamma):
    policy = []

    for i in range(memory_mdp.n_states):
        best_action, best_action_value = None, None

        for j in range(memory_mdp.n_actions):
            action_value = memory_mdp.rewards[i, j] + gamma * np.sum(memory_mdp.transition_probabilities[i, j] * values)
            if best_action_value is None or action_value > best_action_value:
                best_action = j
                best_action_value = action_value

        policy.append(best_action)

    return policy


def solve(mdp, gamma):
    memory_mdp = MemoryMDP(mdp)

    __validate(memory_mdp)

    c = cplex.Cplex()

    __set_variables(c, memory_mdp)
    __set_objective(c, memory_mdp)
    __set_constraints(c, memory_mdp, gamma)

    print("===== Program Details =============================================")
    print("{} variables".format(c.variables.get_num()))
    print("{} sense".format(c.objective.sense[c.objective.get_sense()]))
    print("{} linear coefficients".format(len(c.objective.get_linear())))
    print("{} linear constraints".format(c.linear_constraints.get_num()))

    print("===== CPLEX Details ===============================================")
    c.solve()
    print("===================================================================")

    objective_value = c.solution.get_objective_value()
    values = c.solution.get_values()
    policy = __get_policy(values, memory_mdp, gamma)

    return {
        'objective_value': objective_value,
        'values': {memory_mdp.states[state]: value for state, value in enumerate(values)},
        'policy': {memory_mdp.states[state]: memory_mdp.actions[action] for state, action in enumerate(policy)}
    }
