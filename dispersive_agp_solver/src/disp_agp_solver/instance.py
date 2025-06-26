import typing
import networkx as nx
import lzma
from pathlib import Path

from rvispoly import Point, Polygon, PolygonWithHoles

Position = typing.Tuple[int, int]


class Instance:
    def __init__(
        self,
        positions: typing.List[Position],
        boundary: typing.List[int],
        holes: typing.Optional[typing.List[typing.List[int]]] = None,
    ) -> None:
        if holes is None:
            holes = []
        indices = set(boundary) | {i for hole in holes for i in hole}
        # check if boundary and holes are valid
        if min(indices) != 0 or max(indices) != len(positions) - 1:
            msg = "Invalid boundary or holes"
            raise ValueError(msg)
        self.positions = positions
        self.boundary = boundary
        self.holes = holes

    def num_holes(self) -> int:
        return len(self.holes)

    def num_positions(self) -> int:
        return len(self.positions)

    def as_cgal_position(self, i: int) -> Point:
        return Point(self.positions[i][0], self.positions[i][1])

    def as_cgal_polygon(self) -> PolygonWithHoles:
        boundary = Polygon([self.as_cgal_position(i) for i in self.boundary])
        if float(boundary.area()) <= 0:
            self.boundary = self.boundary[::-1]
            boundary = Polygon([self.as_cgal_position(i) for i in self.boundary])
        holes = [
            Polygon([self.as_cgal_position(i) for i in hole]) for hole in self.holes
        ]
        for i, hole in enumerate(self.holes):
            if float(holes[i].area()) >= 0:
                hole = hole[::-1]  # noqa: PLW2901
                self.holes[i] = hole
                holes[i] = Polygon([self.as_cgal_position(i) for i in hole])
        if float(boundary.area()) <= 0 or not boundary.is_simple():
            msg = "Boundary is not valid"
            raise ValueError(msg)
        if any(float(hole.area()) >= 0 or not hole.is_simple() for hole in holes):
            msg = "Holes are not valid"
            raise ValueError(msg)
        return PolygonWithHoles(boundary, holes)

def get_instance_from_graphml_xz(filepath):
    assert Path(filepath).is_file()
    with open(filepath, "rb") as fp:
            with lzma.open(fp) as xz:
                g = nx.read_graphml(xz)
                return _convert(g)

def _integralize(g: nx.Graph, s: int):
    for n in g.nodes:
        g.nodes[n]["vertex-coordinate-x"] = round(
            s * float(g.nodes[n]["vertex-coordinate-x"])
        )
        g.nodes[n]["vertex-coordinate-y"] = round(
            s * float(g.nodes[n]["vertex-coordinate-y"])
        )


def _vertex_to_position(graph, vertex):
    return (
        round(graph.nodes[vertex]["vertex-coordinate-x"]),
        round(graph.nodes[vertex]["vertex-coordinate-y"]),
    )


def _graph_to_list(graph: nx.Graph):
    components = [
        [
            _vertex_to_position(graph, v)
            for v in nx.dfs_preorder_nodes(graph, source=next(iter(comp)))
        ]
        for comp in nx.connected_components(graph)
    ]
    if len(components) == 1:
        return components[0][::-1], []
    else:
        # move outer face to front
        components.sort(key=min)
        return components[0][::-1], components[1:]
    
def _list_to_instance(outer_face, holes):
    positions = outer_face + sum(holes, [])
    position_to_index = {p: i for i, p in enumerate(positions)}
    boundary = [position_to_index[p] for p in outer_face]
    holes = [[position_to_index[p] for p in hole] for hole in holes]
    return Instance(positions, boundary, holes)
    
def _convert(g: nx.Graph):
        # integralize
        _integralize(g, 1000)
        # convert to list representation
        outer_face, holes = _graph_to_list(g)
        # convert to instance
        return _list_to_instance(outer_face, holes)
