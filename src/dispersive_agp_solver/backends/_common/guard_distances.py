"""
This code computes the geodesic distances between all pairs of positions in an instance.
It is based on the visibility polygon calculator from the rvispoly package.
It is a well known result that the geodesic distance between two points in a polygon
can be computed purely by connecting all vertices that can view each other and then
computing the shortest path between the two points in the resulting graph.
"""

import itertools
import math
import typing

import rustworkx as rw

from dispersive_agp_solver.instance import Instance
from dispersive_agp_solver._utils.timer import Timer as StopWatch

from .guard_coverage import GuardCoverage


class GuardDistances:
    def __init__(
        self, instance: Instance, guard_coverage: typing.Optional[GuardCoverage]
    ) -> None:
        guard_coverage = guard_coverage if guard_coverage else GuardCoverage(instance)
        stop_watch = StopWatch()
        self._graph = rw.PyGraph()
        self._graph.add_nodes_from(range(instance.num_positions()))
        for i in range(instance.num_positions()):
            for j in range(i + 1, instance.num_positions()):
                if guard_coverage.can_guards_see_each_other(i, j):
                    dist = abs(instance.positions[i][0] - instance.positions[j][0]) + abs(instance.positions[i][1] - instance.positions[j][1])
                    self._graph.add_edge(i, j, dist)
        if not rw.is_connected(self._graph):
            msg = "Instance is not connected"
            raise ValueError(msg)
        self._apsp = None
        self._sorted_distances = None
        self._stats = {"time_build_distance_graph": stop_watch.time()}

    def compute_all_distances(self) -> None:
        """
        Compute all distances.
        """
        if not self._apsp is not None:
            stop_watch = StopWatch()
            self._apsp = dict(
                rw.all_pairs_dijkstra_path_lengths(self._graph, lambda e: float(e))
            )
            guards = list(range(self._graph.num_nodes()))
            self._sorted_distances = [
                ((i, j), self._apsp[i][j]) for i, j in itertools.combinations(guards, 2)
            ]
            self._sorted_distances.sort(key=lambda x: x[1])
            self._stats["time_compute_distances_from_graph"] = stop_watch.time()

    def get_next_higher_distance(self, d: float) -> float:
        """
        Get the next higher distance.
        """
        self.compute_all_distances()
        assert self._sorted_distances is not None
        for (_i, _j), dist in self._sorted_distances:
            if dist > d:
                return dist
        return math.inf

    def get_next_lower_distance(self, d: float) -> float:
        """
        Get the next lower distance.
        """
        self.compute_all_distances()
        assert self._sorted_distances is not None
        for (_i, _j), dist in reversed(self._sorted_distances):
            if dist < d:
                return dist
        return 0.0

    def min_distance_of_guards(self, guards: typing.List[int]) -> float:
        """
        Compute the minimum distance of the given guards.
        """
        self.compute_all_distances()
        assert self._apsp is not None
        if not guards:
            msg = "Empty list of guards."
            raise ValueError(msg)
        if len(guards) == 1:
            return math.inf
        return min(self._apsp[i][j] for i, j in itertools.combinations(guards, 2))

    def max(self) -> float:
        """
        Compute the maximum distance.
        """
        self.compute_all_distances()
        assert self._sorted_distances is not None
        return self._sorted_distances[-1][1]

    def distance(self, i: int, j: int) -> float:
        if self._apsp:
            return self._apsp[i][j]
        return rw.dijkstra_shortest_path_lengths(self._graph, i, lambda e: float(e))[j]

    def shortest_path(self, i: int, j: int) -> typing.List[int]:
        sp = rw.dijkstra_shortest_paths(self._graph, i, lambda e: float(e))[j]
        assert isinstance(sp, list)
        return sp
    
    def get_stats(self):
        return self._stats