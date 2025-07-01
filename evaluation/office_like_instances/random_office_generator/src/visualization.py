import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import matplotlib.patches as patches

def visualize_polygon(vertices, holes=[], dark_grey_rects=[], tried=[]):
    """Visualization for given office-like polygons"""
    fig, ax = plt.subplots()
    polygon = Polygon(vertices)
    
    # plot the exterior
    x, y = polygon.exterior.xy
    ax.plot(x, y, color='black')
    ax.fill(x, y, color='lightgrey', alpha=0.5)
    
    # plot the holes
    for hole in holes:
        hx, hy = zip(*hole)
        ax.plot(hx, hy, color='black')
        ax.fill(hx, hy, color='white', alpha=1.0)
    
    # make corridors dark grey
    for rect in dark_grey_rects:
        x_rect = rect.x
        y_rect = rect.y
        rectangle_patch = patches.Rectangle((x_rect, y_rect), rect.width, rect.height, linewidth=1, edgecolor='black', facecolor='darkgrey')
        ax.add_patch(rectangle_patch)
    

    ax.set_aspect('equal', adjustable='box')

    all_x = list(x) + [hx for hole in holes if len(hole) >= 3 for hx, _ in hole]
    all_y = list(y) + [hy for hole in holes if len(hole) >= 3 for _, hy in hole]
    for rect in dark_grey_rects:
        all_x.extend([rect.x, rect.x + rect.width])
        all_y.extend([rect.y, rect.y + rect.height])
    plt.xlim(min(all_x) - 1, max(all_x) + 1)
    plt.ylim(min(all_y) - 1, max(all_y) + 1)
    
    ax.axis('off')
    
    plt.show()
