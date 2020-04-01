import cplex_mdp_solver
import printer
from grid_world_mdp import GridWorldMDP


def main():
    grid_world = [
        ['O', 'O', 'W', 'W', 'O', 'O', 'O', 'W', 'O', 'O', 'O', 'O'],
        ['O', 'O', 'W', 'W', 'O', 'W', 'O', 'W', 'O', 'W', 'O', 'O'],
        ['O', 'O', 'W', 'W', 'O', 'W', 'O', 'O', 'O', 'W', 'O', 'O'],
        ['O', 'O', 'O', 'O', 'O', 'W', 'W', 'W', 'W', 'W', 'O', 'O'],
        ['O', 'O', 'W', 'W', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
        ['O', 'O', 'O', 'O', 'O', 'W', 'W', 'W', 'W', 'W', 'G', 'O']
    ]

    print("Grid World Domain:")
    printer.print_grid_world_domain(grid_world)

    print("Setting up the grid world MDP...")
    ground_mdp = GridWorldMDP(grid_world)

    print("Solving the grid world MDP...")
    ground_solution = cplex_mdp_solver.solve(ground_mdp, 0.99)

    print("Concrete Grid World Policy:")
    printer.print_grid_world_policy(grid_world, ground_solution['policy'])


if __name__ == '__main__':
    main()
