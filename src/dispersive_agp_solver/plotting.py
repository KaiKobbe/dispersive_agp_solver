import matplotlib.pyplot as plt
from rvispoly import PolygonWithHoles
from .backends._common.guard_distances import GuardDistances
from .backends._common.guard_coverage import GuardCoverage
import itertools

LINE_WIDTH = {"normal": 0.2, "heavier": 0.8, "fat": 1.2, "ultrafat": 2}
SYMBOL_SIZE = {"tiny": 1, "small": 2.5, "normal": 3, "large": 3}
COLORS = {"red": "#BC403A", "green": "#45B26C", "blue": "#2065B8", "black": "#000000", "dark_grey": "#7E7F7F", "grey": "#BCBCBE", "light_grey": "#EAEDEF"}

# Note that the function is not very efficient but should suffice for our purposes
def plot_polygon(polygon, color=COLORS["light_grey"], ax=None, lined=True, alpha=1, line_width=None):
        if not line_width: line_width = LINE_WIDTH["normal"]
        if ax is None:
            ax = plt.gca()
        if type(polygon) == PolygonWithHoles:
            plot_polygon(polygon.outer_boundary(), color=color, ax=ax, lined=lined, alpha=alpha)
            for hole in polygon.holes():
                plot_polygon(hole, color="white", lined=lined, alpha=alpha)
        else:
            x = [float(p.x()) for p in polygon.boundary()]
            x += [x[0]]
            y = [float(p.y()) for p in polygon.boundary()]
            y += [y[0]]
            ax.fill(x, y, color=color, linewidth=line_width, alpha=alpha)
            if lined:
                ax.plot(x, y, color=COLORS["black"], linewidth=line_width)

def plot_solution(instance, guards=[], bottleneck=True, axis=False, scale=1, path=None, show=True):
    fig, ax = plt.subplots(figsize=(6.4*scale, 4.8*scale))
    if not axis: ax.set_axis_off()

    # Plotting polygon
    plot_polygon(instance.as_cgal_polygon(), ax=ax)
    ax.set_aspect("equal")

    # Plotting guards
    for guard in guards:
        ax.plot(instance.positions[guard][0], 
                instance.positions[guard][1],
                "o",
                color=COLORS["red"],
                markersize=SYMBOL_SIZE["tiny"]
                )
    
    # Plotting bottleneck
    if bottleneck:
        gd = GuardDistances(instance, GuardCoverage(instance))
        obj = min(gd.distance(g[0], g[1]) for g in itertools.combinations(guards, 2))
        for g in itertools.combinations(guards, 2):
            if gd.distance(g[0], g[1]) == obj:
                bottleneck_guards = [*g]
                break
        for guard in bottleneck_guards:
            ax.plot(instance.positions[guard][0], 
                instance.positions[guard][1],
                "o",
                color=COLORS["blue"],
                markersize=SYMBOL_SIZE["tiny"]
                )

    plt.gca().set_aspect("equal", adjustable="box")

    if path:
        fig.savefig(path, dpi=1000, bbox_inches="tight")
        
    if show:    
        plt.show()
