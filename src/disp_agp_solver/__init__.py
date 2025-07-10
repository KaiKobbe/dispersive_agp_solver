"""
This package provides an exact solver for the DISPERSIVE AGP with vertex guards.
The DISPERSIVE AGP is a variant of the Art Gallery Problem (AGP) where
the objective is to maximize minimum pairwise geodesic L1-distance between the selected guards.
The number of guards does not matter.

The packages provides solvers based on SAT, CP, and IP models. However, the SAT-solver comes with the best performance.
To ensure total coverage, the solver uses shadow witnesses as they have been introduced by Couto et al.

Note that the restriction to vertex guards makes this problem much
more tractable than general point guards.
"""

from .backends import OptimizerParams, SearchStrategy, solve
from .instance import Instance, get_instance_from_graphml_xz
from .plotting import plot_instance, plot_polygon

__all__ = [
    "Instance",
    "get_instance_from_graphml_xz",
    "plot_instance",
    "plot_polygon",
    "solve",
    "OptimizerParams",
    "SearchStrategy",
]
