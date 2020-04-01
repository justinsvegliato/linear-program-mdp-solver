# `linear-program-mdp-solver`

This library is for solving MDPs with linear programming.

## Installation

To use this library, we have to install the following Python dependencies.

```bash
pip install numpy
pip install cplex
```

## Example

```python
import cplex_mdp_solver
from grid_world_mdp import GridWorldMDP

grid_world = [
    ['O', 'O', 'W', 'W', 'O', 'O', 'O', 'W', 'O', 'O', 'O', 'O'],
    ['O', 'O', 'W', 'W', 'O', 'W', 'O', 'W', 'O', 'W', 'O', 'O'],
    ['O', 'O', 'W', 'W', 'O', 'W', 'O', 'O', 'O', 'W', 'O', 'O'],
    ['O', 'O', 'O', 'O', 'O', 'W', 'W', 'W', 'W', 'W', 'O', 'O'],
    ['O', 'O', 'W', 'W', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
    ['O', 'O', 'O', 'O', 'O', 'W', 'W', 'W', 'W', 'W', 'G', 'O']
]

printer.print_grid_world_domain(grid_world)

mdp = GridWorldMDP(grid_world)

solution = cplex_mdp_solver.solve(mdp, 0.99)
```
