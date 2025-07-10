from .cp import CpSatOptimizer
from .mip import GurobiOptimizer
from .sat import OptimizerParams, SatBasedOptimizer, SearchStrategy


def solve(
    instance,
    backend: str = "SAT[Glucose4]",
    time_limit=900.0,
    opt_tol=0.0001,
    logger=None,
    **params,
):
    if backend == "SAT":
        solver = SatBasedOptimizer(
            instance, logger=logger, params=OptimizerParams(**params)
        )
        solver.solve(time_limit, opt_tol)
        return solver.solution, solver.objective
    elif backend.startswith("SAT["):
        solver = SatBasedOptimizer(
            instance, logger=logger, params=OptimizerParams(**params), solver=backend[4:-1]
        )
        solver.solve(time_limit, opt_tol)
        return solver.solution, solver.objective
    elif backend == "CP-SAT":
        solver = CpSatOptimizer(instance, logger=logger)
        solver.solve(time_limit, opt_tol)
        return solver.solution, solver.objective
    elif backend == "MIP":
        solver = GurobiOptimizer(instance, logger=logger)
        solver.solve(time_limit, opt_tol)
        return solver.solution, solver.objective
    msg = f"Invalid backend: {backend}"
    raise NotImplementedError(msg)


__all__ = ["SatBasedOptimizer", "OptimizerParams", "solve", "SearchStrategy"]
