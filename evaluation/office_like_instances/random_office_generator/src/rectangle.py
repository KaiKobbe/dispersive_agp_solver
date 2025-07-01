class Rectangle:
    """Simple class for rectangles representing rooms and corridors."""

    def __init__(self, height, width, x=None, y=None):
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.incident_corridors = {"top": [],"left": [], "bottom": [], "right": []} 

    @property
    def position(self):
        return (self.x, self.y)
    
    @property
    def corners(self):
        return [(self.x, self.y), (self.x + self.width, self.y), (self.x + self.width, self.y + self.height), (self.x, self.y + self.height)]
    
    def get_free_intervals(self, wall: str) -> list[tuple[int, int]]:
        """Determines, for a specified wall, at which parts there is no corridor placed so far; only used for rooms"""
        assert wall in {"top", "left", "bottom", "right"}
        endpoints = []
        if wall in {"top", "bottom"}:
            endpoints += [self.x, self.x + self.width]
            for corridor in self.incident_corridors[wall]:
                endpoints += [corridor.x, corridor.x + corridor.width]
        if wall in {"left", "right"}:
            endpoints += [self.y, self.y + self.height]
            for corridor in self.incident_corridors[wall]:
                endpoints += [corridor.y, corridor.y + corridor.height]
        endpoints = sorted(endpoints)
        intervals = [(endpoints[i], endpoints[i+1]) for i in range(0, len(endpoints), 2)]
        return [(i[0]+1, i[1]-1) for i in intervals if i[1] - i[0] >= 3]
