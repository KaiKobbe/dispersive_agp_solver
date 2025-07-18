"""
This file implements geometric computations for making sure that we cover the whole area.
"""

import logging
import typing

from rvispoly import Point, Polygon, PolygonWithHoles, VisibilityPolygonCalculator

from dispersive_agp_solver.instance import Instance
from dispersive_agp_solver._utils.timer import Timer as StopWatch


class GuardCoverage:
    """
    Computes the visibility polygons of all guards and can compute the missing area of a set of guards.
    """

    def __init__(
        self, instance: Instance, logger: typing.Optional[logging.Logger] = None
    ) -> None:
        if logger is None:
            self._logger = logging.getLogger("DispAgpSatModel")
        else:
            self._logger = logger
        self._instance = instance
        stop_watch = StopWatch()
        self._visibility_polygon_calculator = VisibilityPolygonCalculator(
            instance.as_cgal_polygon()
        )
        self._vis_polys = self._compute_visibilities()
        self._stats = {"time_compute_vispolys": stop_watch.time()}

    def _compute_visibilities(self) -> typing.List[Polygon]:
        return [
            PolygonWithHoles(
                self._visibility_polygon_calculator.compute_visibility_polygon(
                    self._instance.as_cgal_position(i)
                )
            )
            for i in range(self._instance.num_positions())
        ]

    def can_guards_see_each_other(self, guard_a: int, guard_b: int) -> bool:
        return self.get_visibility_of_guard(guard_a).contains(
            self._instance.as_cgal_position(guard_b)
        )

    def get_visibility_of_guard(self, guard: int):
        return self._vis_polys[guard]

    def compute_uncovered_area(
        self, guards: typing.List[int]
    ) -> typing.List[PolygonWithHoles]:
        missing_area = [self._instance.as_cgal_polygon()]
        coverages = [self.get_visibility_of_guard(guard) for guard in guards]

        def diff(poly_a, poly_b):
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Polygons: %s and %s", poly_a, poly_b)
                self._logger.debug(
                    "Areas: %s and %s", float(poly_a.area()), float(poly_b.area())
                )
            res = poly_a.difference(poly_b)
            self._logger.debug("Result: %s", res)
            return res

        for coverage in coverages:
            assert all(isinstance(p, PolygonWithHoles) for p in missing_area)
            assert isinstance(coverage, PolygonWithHoles)
            # difference is always a list of polygons as it can split a polygon into multiple parts
            missing_area = sum((diff(poly, coverage) for poly in missing_area), [])
        return missing_area

    def compute_guards_within_polygon(self, poly: Polygon) -> typing.List[int]:
        """
        Compute which vertex guard can see the given witness.
        """
        return [
            i
            for i in range(self._instance.num_positions())
            if poly.contains(self._instance.as_cgal_position(i))
        ]

    def compute_guards_for_witness(self, witness: Point) -> typing.List[int]:
        """
        Compute which vertex guard can see the given witness.
        """
        vis_poly = self._visibility_polygon_calculator.compute_visibility_polygon(
            witness
        )
        guards = self.compute_guards_within_polygon(vis_poly)
        assert guards, "Should not be empty."
        return guards
    
    def get_stats(self):
        return self._stats