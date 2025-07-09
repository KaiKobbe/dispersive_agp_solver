"""
This file implements the shadow witness strategy.
"""
import typing

from r_vis_poly import Point, Polygon, AVP_Arrangement

from dispersive_agp_solver.instance import Instance
from dispersive_agp_solver._utils.timer import Timer as StopWatch
from .guard_coverage import GuardCoverage

class WitnessStrategy:
    def __init__(
        self,
        instance: Instance,
        coverage: GuardCoverage
    ) -> None:
        self.instance = instance
        self.coverage = coverage
        self.visibility_polygons = self._get_visibility_polygons()
        self._stats = {}

    def _get_visibility_polygons(self):
        return {i: self.coverage.get_visibility_of_guard(i) for i in range(self.instance.num_positions())}
    
    def _compute_avps(visibility_polygons):
        if len(visibility_polygons) == 1:
            return AVP_Arrangement(list(visibility_polygons.values())[0], {list(visibility_polygons.keys())[0]})
        vis_A = dict(list(visibility_polygons.items())[:len(visibility_polygons)//2])
        vis_B = dict(list(visibility_polygons.items())[len(visibility_polygons)//2:])
        arr_A = WitnessStrategy._compute_avps(vis_A)
        arr_B = WitnessStrategy._compute_avps(vis_B)
        return arr_A.overlay(arr_B)
    
    def get_shadow_witnesses(self) -> typing.List[typing.Tuple[typing.Optional[Point], typing.List[int]]]:
        stop_watch = StopWatch()
        self.avps = WitnessStrategy._compute_avps(self.visibility_polygons)
        witnesses = self.avps.get_shadow_witnesses().values()
        unique_witnesses = list(map(set, {frozenset(s) for s in witnesses}))
        self._stats["time_compute_shadow_witnesses"] = stop_watch.time()
        return [(i,w) for i,w in enumerate(unique_witnesses)]
    
    def get_stats(self):
        return self._stats