import random
import itertools
from shapely.ops import unary_union
from shapely.geometry import Polygon

from src.rectangle import Rectangle

class RandomOfficeGenerator:
    """
    Creates a random office-like polygon with a specified number of rooms and corridors in total.
    The generator should be used only for small polygons (<= 1700 vertices) since it is not designed to be runtime-efficient.
    """

    def random_office(self, num_rooms_and_corridors: int, hole_free=False):
        """
        returns outer_boundary and inner_boundary where
        (i) outer_boundary is a list of points, and
        (ii) inner_boundary is a list of lists of points
        """
        self.density = max(1, int(0.05 * num_rooms_and_corridors))
        self.room_max_size = num_rooms_and_corridors

        # Init office
        self.rooms = [Rectangle(random.randint(1, num_rooms_and_corridors), random.randint(1, num_rooms_and_corridors), (num_rooms_and_corridors*self.density)//2, (num_rooms_and_corridors*self.density)//2)]
        self.corridors = []
        self.free_corridors = [] # can be deleted without losing connectivity

        # Bounding box of the office so far
        self.max_x = self.rooms[0].x + self.rooms[0].width
        self.min_x = self.rooms[0].x
        self.max_y = self.rooms[0].y + self.rooms[0].height
        self.min_y = self.rooms[0].y

        if num_rooms_and_corridors < 3: return self.rooms_corridors_to_graph(self.rooms + self.corridors), self.corridors

        # Add second room to allow adding corridors later
        room, corridor = self.add_room()
        self.rooms.append(room)
        self.corridors.append(corridor)

        num = num_rooms_and_corridors-3

        # Randomly choose to either add a room (with connecting corridor) or a corridor between two existing rooms
        while num > 0:
            choice = random.choice([1,2])
            if (choice == 1 and num >= 2) or hole_free:
                room, corridor = self.add_room()
                self.rooms.append(room)
                self.corridors.append(corridor)
                num = num-2
            else:
                corridor = self.add_corridor()
                if corridor == "impossible":
                    room, corridor = self.add_room()
                    self.rooms.append(room)
                    self.corridors.append(corridor)
                    num = num-2
                else:
                    self.corridors.append(corridor)
                    self.free_corridors.append(corridor)
                    num = num-1

        if num == -1: self.delete_corridor()

        return self.rooms_corridors_to_graph(self.rooms + self.corridors)
    
    def update_bounding_box(self, room):
        self.max_x = max(self.max_x, room.x + room.width)
        self.min_x = min(self.min_x, room.x)
        self.max_y = max(self.max_y, room.y + room.height)
        self.min_y = min(self.min_y, room.y)

    def add_room(self):
        """chooses random room size/position and a connecting corridor"""

        # determine room size
        room_a = Rectangle(random.randint(1, self.room_max_size), random.randint(3, self.room_max_size))
        room_b = Rectangle(random.randint(3, self.room_max_size), random.randint(1, self.room_max_size))
        room = random.choice([room_a, room_b])

        # determine room position
        possible_corridors = []
        while not possible_corridors:
            iter = 1
            rndm_var = random.choice([0,1])
            if rndm_var == 0:
                room.x = random.randint(self.min_x-room.width, self.max_x) 
                room.y = random.randint(int(1 - (iter-1) * self.density), int(iter * self.density * self.room_max_size))
            elif rndm_var == 1: 
                room.x = random.randint(int(1 - (iter-1) * self.density), int(iter*self.density * self.room_max_size))
                room.y = random.randint(self.min_y-room.height, self.max_y) 
            if (any(self.is_overlapping(room, room2) for room2 in self.rooms) or any(self.is_overlapping(room, corr) for corr in self.corridors)):
                iter = iter + 0.5
                continue
            for room2 in self.rooms:
                possible_corridors += self.compute_possible_corridors(room, room2)
            

        # choose connecting corridor
        corridor = random.choice(possible_corridors)
        corridor[1].incident_corridors[corridor[2]].append(corridor[0])
        corridor[3].incident_corridors[corridor[4]].append(corridor[0])
        
        self.update_bounding_box(room)

        return room, corridor[0]

    def add_corridor(self): 
        """returns a randomly positioned corridor between two randomly chosen rooms so that the corridor can be added without overlap"""
        possible_pairs = [pair for pair in itertools.combinations(self.rooms,2) if self.is_eventual_connectable(pair[0], pair[1])]
        possible_corridors = []
        for pair in possible_pairs:
            possible_corridors += self.compute_possible_corridors(*pair)
        if not possible_corridors: return "impossible"
        corridor = random.choice(possible_corridors)
        corridor[1].incident_corridors[corridor[2]].append(corridor[0])
        corridor[3].incident_corridors[corridor[4]].append(corridor[0])
        return corridor[0]

    def delete_corridor(self):
        """deletes a random corridor from the set of free corridors; returns true if possible, else None"""
        if not self.free_corridors: return
        corridor = random.choice(self.free_corridors)
        self.free_corridors.remove(corridor)
        self.corridors.remove(corridor)
        return True

    def is_eventual_connectable(self, room_a, room_b):
        """returns true if there is some possibility to add a corridor between room_a and room_b and this does not lead to overlaps, else false"""
        if room_a.y + room_a.height >= room_b.y + 3 and room_b.y + room_b.height >= room_a.y + 3: return True
        if room_a.x + room_a.width >= room_b.x + 3 and room_b.x + room_b.height >= room_a.x + 3: return True
        return False
    
    def is_overlapping(self, rect_a, rect_b):
        if rect_a.x + rect_a.width < rect_b.x or rect_b.x + rect_b.width < rect_a.x: return False
        if rect_a.y + rect_a.height < rect_b.y or rect_b.y + rect_b.height < rect_a.y: return False
        return True

    def rooms_corridors_to_graph(self, rectangles): 
   
        polys = [Polygon(rect.corners) for rect in rectangles]
        polygon = unary_union(polys)
    
        exterior_coords = []
        interiors_coords = []
        exterior_coords.extend(list(polygon.exterior.coords))
        for interior in polygon.interiors:
            interiors_coords.append(list(interior.coords))

        return exterior_coords, interiors_coords

    def interval_intersection(self, i1, i2):
        """For two parallel walls of different rooms, determines where a corridor between them could be added"""
        intervals = []
        for pair in itertools.product(i1, i2):
            endpoints = sorted([pair[0][0], pair[0][1], pair[1][0], pair[1][1]])
            interval = (endpoints[1], endpoints[2])
            if interval == (pair[0][1], pair[1][0]) or interval == (pair[1][1], pair[0][0]): continue
            intervals.append(interval)
        return intervals

    def compute_possible_corridors(self, room_a, room_b):
        """function that returns a list of all possible corridors between two rooms so that the corridor fits nicely to the walls and does not overlap with other corridors/rooms."""
        if not self.is_eventual_connectable(room_a, room_b): return []
        possible_corridors = []

        # start configuration
        if room_b.y + room_b.height < room_a.y or room_b.x + room_b.width < room_a.x:
            temp = room_a
            room_a = room_b
            room_b = temp
        if room_a.y + room_a.height < room_b.y:
            a_wall = "top"
            b_wall = "bottom"
        else:
            a_wall = "left"
            b_wall = "right"

        # enumerate possible corridors
        intervals_a = room_a.get_free_intervals(a_wall)
        intervals_b = room_b.get_free_intervals(b_wall)
        free_space = self.interval_intersection(intervals_a, intervals_b)
        for space in free_space:
            for start in range(space[0], space[1]):
                for end in range(start+1, space[1]+1):
                    if room_a.y + room_a.height < room_b.y:
                        corridor = Rectangle(room_b.y - (room_a.y + room_a.height), end-start, start, room_a.y + room_a.height)
                    else: 
                        corridor = Rectangle(end-start, room_b.x - (room_a.x + room_a.width), room_a.x + room_a.width, start)
                    if any([self.is_overlapping(corridor, room) for room in self.rooms if room not in {room_a, room_b}]) or any([self.is_overlapping(corridor, corr) for corr in self.corridors]):
                        break
                    possible_corridors.append((corridor, room_a, a_wall, room_b, b_wall))

        return possible_corridors

