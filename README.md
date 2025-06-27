# Dispersive Art Gallery Problem - MIP, CP, and SAT Solvers

> ⚠️ **Disclaimer**  
> This repository is newly set up.  
> It may take a few more days until everything works smoothly and is documented.  
> Feel free to check back soon!

Given a polygonal domain $\mathcal P$, a finite set $\mathcal G \subset \mathcal P$ is a _guard set_ if every point in $\mathcal P$ is seen by at least one point in $\mathcal G$.
In the classic _Art Gallery Problem_, the aim is to find a guard set of minimum cardinality.
In contrast, the _Dispersive Art Gallery Problem_ (DAGP) asks for a guard set with maximized minimum pairwise guard distance, i.e., the guards should be placed far away from each other. Notably, in this formulation, the number of guards is irrelevant. Objectives of this type naturally occur in many situations, e.g. in sensor deployment, where it is crucial to balance sensor spacing and signal coverage.

We compute exact solutions for the DAGP restricted to _vertex guards_ in orthogonal polygons. To this end, we use _r-visibility_ and measure distances as given by the geodesic $L_1$-metric.

The solvers use significant portions of [Dominik Krupke's solver](https://github.com/d-krupke/dispersive_agp_solver), but differ in the used witness strategy, distance measure, and visibility model.
We also complement the solvers with a rather extensive evaluation.

A section of the paper "Guarding Offices with Maximum Dispersion" (accepted at [International Symposium on Mathematical Foundations of Computer Science 2025 (MFCS)](https://mfcs2025.mimuw.edu.pl)) is devoted to this solver and its evaluation. 
A full version of the paper can be found on [arXiv](https://arxiv.org/abs/2506.21307). The paper also outlines previous work on the DAGP in more detail.


## Installation
tbd

[r-visibility polygons](https://github.com/KaiKobbe/r_visibility_polygons)

## Example Usage

Below, a very simple example is given.
Solving the instance to optimality should be done immediately.
Note that, especially for larger instances, _plot_instance()_ may take some time if the bottleneck should be depicted, as it currently determines this by simple pairwise comparisons.

```python
from disp_agp_solver import get_instance_from_graphml_xz, plot_instance, solve

# Specify as backend either "MIP", "CP-SAT", or "SAT"
# "SAT" by default uses Glucose4, but other solvers from the PySAT package can be used as "SAT[*solvername*]
solution, objective, upper_bound = solve(instance, backend="SAT")

print(f"Found a solution with objective {objective} and {len(solution)} guards!")
plot_instance(instance, bottleneck=True, guards=solution)
```

## Formulations

$$\forall w\in \mathcal{W}: \sum_{g \in V(\mathcal{P}), w\in Vis(g)} x_g \geq 1$$

$$\forall g, g' \in V(\mathcal{P}): x_{g} \wedge x_{g'} \rightarrow \ell \leq \delta(g, g')$$

$$\bigwedge_{w \in \mathcal{W}} \left(\bigvee_{g \in V(\mathcal{P}), w \in \text{Vis}(g)} x_g\right)$$

$$\bigwedge_{g, g' \in V(\mathcal{P}), \delta(g, g') < \ell} \left(\overline{x_{g}} \vee \overline{x_{g'}}\right)$$

## Evaluation
We evaluated the solvers for the following instances: 
- 745 random orthogonal polygons from the [Salzburg Database](https://sbgdb.cs.sbg.ac.at)
- 1599 random office-like polygons

Summarizing the evaluation, the SAT-approach largely outperforms MIP and CP-SAT, being able to solve instances with $1600$ vertices in about 15 seconds.
MIP and CP-SAT perform relative similarly.
However, for large instances, CP-SAT seems to scale slightly better.
While the SAT-approach performs similarly for random orthogonal polygons and office-like polygons, MIP and CP-SAT require less time to compute optimal solutions for office-like polygons.
Further details on the evaluation can be found [here](https://github.com/KaiKobbe/dispersive_agp_solver/tree/main/evaluation/office_like_instances).

## License

While this code is licensed under the MIT license, it has a dependency on
[CGAL](https://www.cgal.org/), which is licensed under GPL. This may have some
implications for commercial use.