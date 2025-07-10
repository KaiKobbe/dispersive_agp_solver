# Dispersive Art Gallery Problem - MIP, CP, and SAT

Given a polygonal domain $\mathcal P$, a finite set $\mathcal G \subset \mathcal P$ is a _guard set_ if every point in $\mathcal P$ is seen by at least one guard in $\mathcal G$.
In the classic _Art Gallery Problem_, the aim is to find a guard set of minimum cardinality.
In contrast, the Dispersive Art Gallery Problem (DAGP) seeks a guard set that maximizes the minimum pairwise distance between guards (referred to as _dispersion distance_). 
Notably, in this formulation, the number of guards is irrelevant. 
Objectives of this type naturally occur in many situations, e.g. in sensor deployment, where it is crucial to balance sensor spacing and signal coverage.
We compute exact solutions for the DAGP restricted to _vertex guards_ in orthogonal polygons. 
To this end, we use _r-visibility_ and measure distances according to the geodesic $L_1$-metric.
The main purpose is to compare solvers based on SAT (PySAT), CP-SAT, and MIP (Gurobi).

This solver builds on significant portions of [Dominik Krupke's implementation](https://github.com/d-krupke/dispersive_agp_solver), but differs in the witness strategy, distance measure, and visibility model. 
In addition, we complement the solver with a comprehensive performance evaluation.
A section of the paper "Guarding Offices with Maximum Dispersion" (to appear at the [International Symposium on Mathematical Foundations of Computer Science 2025](https://mfcs2025.mimuw.edu.pl)) is devoted to this solver and its evaluation. 
A full version is available on [arXiv](https://arxiv.org/abs/2506.21307).
The paper also provides a more detailed overview of previous work on the DAGP.

## Installation
Before the solver can be used, it is mandatory to install our package for [r-visibility polygons](https://github.com/KaiKobbe/r_visibility_polygons).
(The package requires a modern C++ compiler.)
This can be done via the following command:

```bash
pip install --verbose git+https://github.com/KaiKobbe/r_visibility_polygons
```

Afterward, it should be easy to install the solver using the following command:

```bash
pip install --verbose git+https://github.com/KaiKobbe/dispersive_agp_solver
```

Note that an active Gurobi license is required to use the MIP solver.

## Usage

Below, a very simple example is given.
Solving the instance to optimality should be done immediately.

```python
from dispersive_agp_solver import get_instance, solve, plot_solution

# construct a simple instance
# outer_boundary should be in CCW order, holes CW
outer_boundary = [
    (0, 0),
    (10, 0),
    (10, 10),
    (0, 10)
]

holes = [
    [(2, 2), (2, 4), (4, 4), (4, 2)],
    [(6, 2), (6, 5), (8, 5), (8, 2)],
    [(3, 6), (3, 8), (7, 8), (7, 6)]
]
instance = get_instance(outer_boundary, holes)

# compute a guard set with maximum dispersion for the above instance
solution, objective = solve(instance)

# plot the solution 
plot_solution(instance, guards=solution)
```

By default, the SAT-based approach is used.
This can be modified by using `solve(instance, backend="CP-SAT")` or `solve(instance, backend="MIP")` instead.

## Formulations

Let $\mathcal P$ denote a polygonal region with vertex set $V(\mathcal P)$.
The geodesic $L_1$-distance between two guards $g,g' \in V(\mathcal V)$ is denoted as $\delta(g,g')$.
The set of points that are r-visible to a guard $g \in V(\mathcal P)$, i.e., the visibility region of $g$, is denoted as $Vis(g)$.
To ensure full coverage, we use a shadow witness set $\mathcal W$; see for example the work of [Couto et al.](https://link.springer.com/chapter/10.1007/978-3-540-68552-4_8):
The key idea is to construct the arrangement of visibility polygons defined by the polygon’s vertices, where each face (referred to as AVP) is covered by the same guard set. 
From this arrangement, shadow AVPs are identified as the local minima in the partial order of AVPs based on their covering sets. 
Selecting a single witness from each shadow AVP ensures full coverage of the polygon, even under r-visibility constraints.
Subsequently, we explain the used formulations.

### MIP and CP-SAT
For each possible guard position $g \in V(\mathcal P)$, we introduce a binary variable $x_g \in \mathbb{B}$ indicating whether a guard is placed at vertex $g$.
We also introduce a continuous variable $\ell \in \mathbb{R}^+$ representing the dispersion distance of the solution.
The objective maximizes $\ell$, subject to

$$\forall w\in \mathcal{W}: \sum_{g \in V(\mathcal{P}), w\in Vis(g)} x_g \geq 1$$

ensuring that every shadow witness is seen by at least one guard, and

$$\forall g, g' \in V(\mathcal{P}): x_{g} \wedge x_{g'} \rightarrow \ell \leq \delta(g, g')$$

ensuring that, for every pair of guards in the solution, their distance is at least $\ell$.
Note that the second type of constraint is not linear but can be reformulated as a linear constraint using the big-M method.

### SAT
As above, each  $g \in V(\mathcal P)$ is associated with a binary variable $x_g \in \mathbb{B}$.
We use a SAT-solver for the decision problem whether a guard set with dispersion distance $\ell$ exists and search the largest $\ell$ for which the solver answers positively.
Note that the number of possible dispersion distances is quadratic in $|V(P)|$, allowing us to perform a binary search over them.
For efficiency, $\ell$ is updated based on the actual solution returned by the SAT solver rather than just the probed values.
Similarly to the above formulation, the existence of a guard set with dispersion distance $\ell$ can be checked by

$$\bigwedge_{w \in \mathcal{W}} \left(\bigvee_{g \in V(\mathcal{P}), w \in Vis(g)} x_g\right)$$

ensuring coverage, and

$$\bigwedge_{g, g' \in V(\mathcal{P}), \delta(g, g') < \ell} \left(\overline{x_{g}} \vee \overline{x_{g'}}\right)$$

enforcing a minimum guard distance of $\ell$.

## Evaluation
We analyzed solver performance across various types of orthogonal polygons and found that the SAT-based approach significantly outperforms the other two. 
Further details on the evaluation can be found [here](https://github.com/KaiKobbe/dispersive_agp_solver/tree/main/evaluation).

## License
While this code is licensed under the MIT license, it has a dependency on
[CGAL](https://www.cgal.org/), which is licensed under GPL. This may have some
implications for commercial use.