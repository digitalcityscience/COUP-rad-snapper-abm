import osmnx as ox

ox.config(log_console=True)

# get outline poly
from shapely.geometry import shape
import fiona
c = fiona.open('data/project_area.shp')
polygon = c.next()
polygon = shape(polygon['geometry'])

# download/model a street network for some city then visualize it
G = ox.graph.graph_from_polygon(polygon, network_type='walk')

# save graph as a shapefile
ox.save_graph_shapefile(G, filepath='./data/paths')