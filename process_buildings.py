# import shapefile

import os
import shapefile
from shapely.geometry import Polygon, Point, MultiLineString
from shapely.ops import nearest_points

def clip_buildings(data_file, clip_file, clip_layer, output_file):
    """clip a shapefile by another shapefile

    Keyword arguments:
    data_file -- shapefile of data to be clipped
    clip_file -- shapefile containing a clipping polygon
    clip_layer -- the layer in the clip_file that contains the clipping geometry
    output_file -- filename where to store the clipped data
    """
    if output_file[-3:] != "shp":
        raise NotImplementedError("please choose an output file ending with .shp")
    
    batcmd = "ogr2ogr -f 'ESRI Shapefile' %s '%s' -t_srs EPSG:4326 -clipdst %s -clipdstlayer %s" % (output_file, data_file, clip_file, clip_layer)
    os.system(batcmd)

def calc_and_store_centroids(buildings_file, centroids_file):
    """create a shapefile of centroids of the geometries of another shapefile

    Keyword arguments:
    buildings_file -- shapefile of data which we want centroids of
    centroids_file -- output shapefile where we will store centroids
    """
    # open buildings polygons file
    with shapefile.Reader(buildings_file) as sf:
        srs = sf.shapeRecords()

        # store as new shapefile
        with shapefile.Writer(centroids_file, shapeType=1) as outfile: # point shapes type

            for field in sf.fields:
                outfile.field(*field)

            for sr in srs:
                # calculate the centroid for each polygon in input file
                shape = sr.shape
                poly = Polygon(shape.points)
                centroid = poly.centroid

                # add the centroids with the same data attributes as the polys
                outfile.point(centroid.x,centroid.y)
                outfile.record(*sr.record)

def snap_and_store_centroids(edges_file, centroids_file, outfile):
    """snaps points to a line network and creates a new shapefile of these points.

    Keyword arguments:
    edges_file -- shapefile with the line network
    centroids_file -- shapefile with points
    outfile -- output shapefile where we will store snapped points
    """
    # read the road network from disk
    coords = []
    with shapefile.Reader(edges_file) as sf:
        shapes = sf.shapes()
        for shape in shapes:
            line = shape.points
            coords.append(line)
    lines = MultiLineString(coords)

    # store the snapped centroids
    with shapefile.Reader(centroids_file) as sf:
        srs = sf.shapeRecords()

        with shapefile.Writer(outfile, shapeType=1) as outfile: # point shapes

            for field in sf.fields:
                outfile.field(*field)

            for sr in srs:
                shape = Point(*sr.shape.points) # this point will be snapped to the road network

                newPoint = nearest_points(shape, lines) # the closest point in the network is newPoint[1]

                # write the snapped building points to file with the same attributes
                outfile.point(newPoint[1].x, newPoint[1].y)
                outfile.record(*sr.record)

def create_prj_file(filename):
    """creates a prj file (EPSG:4326) for a shapefile

    Keyword arguments:
    filename -- filename to use (without extension)
    """
    epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
    with open("%s.prj" % filename, "w") as prj:
        prj.write(epsg) 

if __name__ == "__main__":
    print("clipping buildings...")
    clip_buildings("data/ALKIS/Hamburg Alkis.shp","data/project_area.shp","project_area","data/clipped_buildings.shp")
    create_prj_file("data/clipped_buildings")
    print("calculating centroids..")
    calc_and_store_centroids("data/clipped_buildings.shp","data/centroids")
    create_prj_file("data/centroids")
    print("snapping centroids...")
    snap_and_store_centroids("data/paths/edges.shp","data/centroids.shp","data/snapped")
    create_prj_file("data/snapped")