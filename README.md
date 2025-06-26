# Solvers for the Dispersive Art Gallery Problem – MIP, CP, and SAT

Given a polygonal domain $\mathcal P$, a finite set $\mathcal G \subset \mathcal P$ is called a guard set if every point in $\mathcal P$ is seen by at least one point in $\mathcal G$, where visibility potentially can be defined in several ways.
In the classic Art Gallery Problem, the goal is to find a guard set of smallest cardinality.
In contrast, the Dispersive Art Gallery Problem (DAGP) asks for a guard set where the minimum pairwise distance between guards is maximized, i.e., the guards should be placed far away from each other. In this formulation, the number of placed guards is clearly irrelevant.

We compute exact solutions for the DAGP in the following setting:
- We use vertex guards, i.e., the guards are restricted to vertices of $\mathcal P$
- The guard distances are given by the geodesic $L_1$-metric, i.e., the length of a shortest rectilinear path that stays inside $\mathcal P$
- We use r-visibility, i.e., two points $p,q \in \mathcal P$ see each other if and only if the axis-parallel rectangle defined by $p$ and $q$ is fully contained inside $\mathcal P$.

Our solver uses significant parts of the [DAGP solver by Dominik Krupke](https://github.com/d-krupke/dispersive_agp_solver), but uses a different witness strategy, distance measure, and visibility model.
We also complement the solver with an extensive evaluation.


## Installation

## Example Usage

## Mathematical Formulation

## SAT Formulation

## Solver Evaluation

Further details can be found in...

## License

While this code is licensed under the MIT license, it has a dependency on
[CGAL](https://www.cgal.org/), which is licensed under GPL. This may have some
implications for commercial use.