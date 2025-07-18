import logging
import math
import typing
from enum import Enum

from rvispoly import Point

from dispersive_agp_solver._utils import Timer
from dispersive_agp_solver.instance import Instance

from .._common import GuardCoverage, GuardDistances, WitnessStrategy
from .distance_optimizer import DistanceOptimizer, SearchStrategy
from .params import OptimizerParams


class SatBasedOptimizer:
    class Status(Enum):
        OPTIMAL = 0
        FEASIBLE = 1
        UNKNOWN = 2

    def __init__(
        self,
        instance: Instance,
        logger: typing.Optional[logging.Logger],
        params: typing.Optional[OptimizerParams] = None,
        solver: str = "Glucose4",
    ) -> None:
        self._logger = logger if logger else logging.getLogger("DispAgpSolver")
        self.params = params if params else OptimizerParams()
        self.solver=solver
        self._logger.info("Setting up coverage calculator...")
        self._guard_coverage = GuardCoverage(instance, logger=self._logger)
        self._logger.info("Setting up guard distances...")
        self._guard_distances = GuardDistances(instance, self._guard_coverage)
        self._logger.info("Setting up witness strategy...")
        self._witness_strategy = WitnessStrategy(instance, self._guard_coverage)
        self.instance = instance
        self.upper_bound = math.inf
        self.objective = 0
        self.solution = list(range(instance.num_positions()))
        self._logger.info("Ready for optimization.")
        self._stats = {
            "iteration_statistics": [],
        }
        self._stats = self._stats | self._guard_coverage.get_stats()

    def add_upper_bound(self, upper_bound: float) -> None:
        self.upper_bound = min(self.upper_bound, upper_bound)
        self._logger.info("Setting upper bound to %f", self.upper_bound)

    def _compute_optimal_for_witness_set(
        self,
        witnesses: typing.List[typing.Tuple[Point, typing.List[int]]],
        timer: Timer,
        search_strategy: SearchStrategy,
        opt_tol: float,
    ) -> typing.Tuple[typing.List[int], float, float]:
        self._logger.info(
            "Computing optimal solution for %d witnesses...", len(witnesses)
        )
        dist_optimizer = DistanceOptimizer(
            self.instance, logger=self._logger, guard_distances=self._guard_distances, solver=self.solver
        )
        try:
            dist_optimizer.add_upper_bound(self.upper_bound)
            for _, guards in witnesses:
                dist_optimizer.add_coverage_constraint(guards)
            dist_optimizer.solve(
                timer=timer,
                callback=[],
                search_strategy=search_strategy,
                opt_tol=opt_tol,
            )
            self._logger.info(
                "Found optimal solution with objective %f for witness set",
                dist_optimizer.objective,
            )
            self.add_upper_bound(dist_optimizer.upper_bound)
        except TimeoutError as _:
            self.add_upper_bound(dist_optimizer.upper_bound)
            raise
        self._stats["iteration_statistics"].append(
            {
                "objective": dist_optimizer.objective,
                "upper_bound": dist_optimizer.upper_bound,
                "opt_gap": self.get_opt_gap(),
                "num_witnesses": len(witnesses),
                "solver": dist_optimizer.get_stats(),
                "search_strategy": search_strategy.name,
            }
        )
        return (
            dist_optimizer.solution,
            dist_optimizer.objective,
            dist_optimizer.upper_bound,
        )

    def get_opt_gap(self) -> float:
        """
        Return the optimality gap, similar to the one defined by CP-SAT
        """
        if self.objective == 0:
            return math.inf
        return (self.upper_bound - self.objective) / self.objective

    def get_stats(self) -> typing.Dict[str, typing.Any]:
        stats: dict = self._stats.copy()
        return stats

    def solve(
        self, time_limit: float = 900, opt_tol: float = 0.0001
    ) -> "SatBasedOptimizer.Status":
        try:
            timer = Timer(time_limit)
            solution, obj, ub = self._compute_optimal_for_witness_set(
                self._witness_strategy.get_shadow_witnesses(),
                timer,
                search_strategy=self.params.search_strategy_start,
                opt_tol=opt_tol,
            )
            self._stats = self._stats | self._witness_strategy.get_stats()
            # Found a solution
            self.solution = solution
            self.objective = obj
            self._logger.info("Found solution with objective %f", self.objective)
            return SatBasedOptimizer.Status.OPTIMAL
        except TimeoutError:
            self._logger.info("Timelimit reached.")
            if self.objective == self.upper_bound:
                return SatBasedOptimizer.Status.OPTIMAL
            if self.solution is not None:
                return SatBasedOptimizer.Status.FEASIBLE
        return SatBasedOptimizer.Status.UNKNOWN