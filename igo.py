'''/////////////////////////////////////////////////////////
File name: igo.py
File function: Generates a graph from a place in order to
get maps with its highways, congestions or paths between
two different points.
Date: 18_05_2021
/////////////////////////////////////////////////////////'''

###########################################################
#                         IMPORTS
###########################################################
# read / write Python data from / to files
import pickle
# download files from the web
import urllib
# allow us to read / write data in python
import csv
# retrieve, model, analyze, and visualize street networks from OpenStreetMap
import osmnx
# creation, manipulation, and study of the structure, dynamics, and functions
# of complex networks
import networkx as nx
# creates static, animated, and interactive visualizations
import matplotlib.pyplot as plt
# paints maps
import staticmap
# connects with Open Street Maps to generate maps with lines and markers
from staticmap import StaticMap, CircleMarker, Line
# helps to define tuples
import collections

import datetime


###########################################################
#                        CONSTANTS
###########################################################
# The place we will be treat in this file is Barcelona
PLACE = 'Barcelona, Catalonia'
# Name of the file where we will save the graph
GRAPH_FILENAME = 'barcelona.graph'
# Size of the images that will be saved
SIZE = 800
# URL from where we can get data from Barcelona's streets
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
# URL from where we can get data from Barcelona's congestions
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

###########################################################
#                          TYPES
###########################################################
# Tuple Highway will contain three attributes: way_id (number representing
# the street), name (of the street), coordinates (where does the street begin
# and end)
Highway = collections.namedtuple('Highway', 'way_id name coordinates')
# Tuple Congestion will contain four attributes: way_id (number representing
# the street), date, usual (usual congestion level), actual (actual congestion
# level). The congestion levels go from 0 to 6:
# 0 - No data available
# 1 - Very fluid
# 2 - Fluid
# 3 - Dense
# 4 - Very dense
# 5 - Congested
# 6 - Cut
Congestion = collections.namedtuple('Congestion', 'way_id date usual actual')


###########################################################
#                        FUNCTIONS
###########################################################

def exists_graph(file_name):
    '''----------------------------------------------------
    * Name: exists_graph
    * Function: Checks if the file containing the graph
    *           exists or not.
    * Parameters: file_name: Name of the file we need
    *             to check if it exists or not.
    * Return: True if the file exists; False otherwise.
    ----------------------------------------------------'''
    try:
        f = open(file_name)
    except FileNotFoundError:
        return False

    f.close()
    return True


def download_graph(place):
    '''----------------------------------------------------
    * Name: download_graph
    * Function: Downloads the graph of a place given
    *           thanks to the Osmnx library and saves
    *           it into a variable after adding the
    *           edge bearings.
    * Parameters: place: Name of the place from where we
    *             we want to get its graph.
    * Return: A graph of the place asked.
    ----------------------------------------------------'''
    # Get the graph of the place with attributes based on the driving system
    graph = osmnx.graph_from_place(place, network_type='drive', simplify=True)
    # Create a graph with the length attribute as the main weight
    graph = osmnx.utils_graph.get_digraph(graph, weight='length')
    # Transform the graph into a multidirected graph.
    G = nx.MultiDiGraph(graph)
    # Add the edge bearings
    graph = osmnx.bearing.add_edge_bearings(G)
    return graph


def save_graph(graph, file_name):
    '''----------------------------------------------------
    * Name: save_graph
    * Function: Saves a graph in a file thanks to Pickle.
    * Parameters: graph: Graph we want to save.
    *             file_name: Name of the file where we
    *                        want to save the graph.
    * Return: -
    ----------------------------------------------------'''
    with open(file_name, 'wb') as file:
        pickle.dump(graph, file)


def load_graph(file_name):
    '''----------------------------------------------------
    * Name: load_graph
    * Function: Loads a graph from a file thanks to Pickle.
    * Parameters: file_name: Name of the file from where
    *             we want to load the graph.
    * Return: The graph from the file given.
    ----------------------------------------------------'''
    with open(file_name, 'rb') as file:
        graph = pickle.load(file)
    return graph


def plot_graph(graph):
    '''----------------------------------------------------
    * Name: plot_graph
    * Function: Plots a given graph thanks to Osmnx.
    * Parameters: graph: Graph representing a place.
    * Return: -
    ----------------------------------------------------'''
    osmnx.plot.plot_graph(graph)


def download_highways(highways_url):
    '''----------------------------------------------------
    * Name: download_highways
    * Function: Downloads from a given URL
    *           data from a place streets and saves
    *           it into a list of tuple Highway.
    * Parameters: highways_url: URL from where the data
    *             must be downloaded.
    * Return: A list of data (tuple Congestion) from a
    *         place congestions.
    ----------------------------------------------------'''
    highways = []  # Will save the data of the csv lines
    with urllib.request.urlopen(highways_url) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # Ignore first line with description
        # Convert into Highway tuple each line and return a
        # list of Highway tuple
        for u_line in reader:
            way_id, name, coordinates = u_line
            highway = Highway(way_id, name, coordinates)
            highways.append(highway)
    return highways


def plot_highways(highways, file_name, size):
    '''----------------------------------------------------
    * Name: plot_highways
    * Function: Saves a map of a place streets thanks
    *           to StaticMap. The map can be ploted after
    *           using the function.
    * Parameters: highways: List of data from a place
    *             streets.
    *             file_name: Name of the file where the
    *             user wants to save the map.
    *             size: Size of the map.
    * Return: An image saved of a map of a place streets.
    ----------------------------------------------------'''
    # Create a map of dimensions (size x size)
    highways_map = StaticMap(size, size)
    for x in range(0, len(highways)):
        # Convert the coordinates string into a list
        coordinates = highways[x].coordinates.split(',')
        # Will save the coordinates in order to make a line between them
        line_coord = []
        for i in range(0, len(coordinates) - 1, 2):
            # Every two coordinates we read the longitude and latitude,
            # respectively, of a point
            longitude = float(coordinates[i])
            latitude = float(coordinates[i+1])
            # Put a circle on the point
            marker = CircleMarker((longitude, latitude), 'cyan', 3)
            highways_map.add_marker(marker)
            line_coord.append((longitude, latitude))
        # Add a line between the points marked on the map
        highways_map.add_line(Line(line_coord, 'cyan', 3))
    # Construct and save the map with the name indicated by the user
    image = highways_map.render()
    image.save(file_name)


def download_congestions(congestions_url):
    '''----------------------------------------------------
    * Name: download_congestions
    * Function: Downloads from a given URL
    *           data from a place congestions and saves
    *           it into a list of tuple Congestion.
    * Parameters: congestions_url: URL from where the data
    *             must be downloaded.
    * Return: A list of data (tuple Congestion) from a
    *         place congestions.
    ----------------------------------------------------'''
    congestions = []  # Will save the data of the csv lines
    with urllib.request.urlopen(congestions_url) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#')
        for u_line in reader:
            # Convert into Congestion tuple each line and return a
            # list of Congestion tuple
            way_id, date, usual, actual = u_line
            congestion = Congestion(way_id, date, usual, actual)
            congestions.append(congestion)
    return congestions


def congestion_color(congestion):
    '''----------------------------------------------------
    * Name: congestion_color
    * Function: Relates a color to a number of congestion
    *           in order to represent it.
    * Parameters: congestion: Number of congestion of
    *             a segment between two nodes of the
    *             graph.
    * Return: An string representing a color related to
    *         the congestion given.
    ----------------------------------------------------'''
    if congestion == "1":
        return "#68d46c"  # If very fluid return green
    elif congestion == "2":
        return "#68d46c"  # If fluid return green
    elif congestion == "3":
        return "#f87c04"  # If dense return orange
    elif congestion == "4":
        return "#e80404"  # If very dense return red
    elif congestion == "5":
        return "#a01414"  # If congested return darker red
    else:
        return "black"  # If cut return black


def get_congestion(congestion):
    '''----------------------------------------------------
    * Name: get_congestion
    * Function: Compares the usual value of the congestion
    *           in some way between the actual value and
    *           decides which one should be considered.
    *           If there is no data about the congestion,
    *           the function returns a congestion of level
    *           2 (fluid). Else, it returns the actual
    *           value if it is different from the usual one.
    * Parameters: congestion: Pair of values of a congestion
    *             between two nodes. There are the congestion
    *             usual value and the actual one.
    * Return: The final value of the congestion.
    ----------------------------------------------------'''
    # If we have no data we adjudicate the value of fluid to the
    # congestion level
    if congestion.usual == "0" and congestion.actual == "0":
        return "2"
    # If we have actual data and it is different to the usual one,
    # return the actual level
    elif congestion.usual != congestion.actual and congestion.actual != "0":
        return congestion.actual
    # Else return the usual level
    else:
        return congestion.usual


def plot_congestions(highways, congestions, file_name, size):
    '''----------------------------------------------------
    * Name: plot_congestions
    * Function: Saves a map of a place congestions thanks
    *           to StaticMap. The map can be ploted after
    *           using the function.
    * Parameters: congestions: List of data from a place
    *             congestions.
    *             file_name: Name of the file where the
    *             user wants to save the map.
    *             size: Size of the map.
    * Return: -
    ----------------------------------------------------'''
    # Create a map of dimensions (size x size)
    congestions_map = StaticMap(size, size)
    for x in range(0, len(highways)):
        # Convert the coordinates string into a list
        coordinates = highways[x].coordinates.split(',')
        for y in range(0, len(congestions)):
            # Will save the coordinates in order to make a line between them
            line_coord = []
            # Relate same streets by the way_id
            if highways[x].way_id == congestions[y].way_id:
                for i in range(0, len(coordinates) - 1, 2):
                    # Every two coordinates we read the longitude and latitude,
                    # respectively, of a point
                    longitude = float(coordinates[i])
                    latitude = float(coordinates[i+1])
                    # Decide which level of congestion will be added
                    congestion_level = get_congestion(congestions[y])
                    # Put a circle on the map corresponding to the point and of
                    # the color given by the congestion_color function
                    marker = CircleMarker((longitude, latitude), congestion_color(congestion_level), 3)
                    congestions_map.add_marker(marker)
                    line_coord.append((longitude, latitude))
                # Add a line between all points added on the map
                congestions_map.add_line(Line(line_coord, congestion_color(congestion_level), 3))
    # Construct and save the map with the name given by the user
    image = congestions_map.render()
    image.save(file_name)


def build_igraph(graph, highways, congestions):
    '''----------------------------------------------------
    * Name: build_igraph
    * Function: Adds "intelligent" attributes to a graph
    *           from a place. It adds the congestion level
    *           and the itime of each edge. Itime makes
    *           reference to the quantity of time a person
    *           would spend going through a concret street;
    *           this doesn't mean that it makes reference
    *           to the time directly, but it can help when
    *           comparing which way would take fewest time.
    * Parameters: graph: Graph of a place.
    *             highways: List of data from the streets
    *             of the place.
    *             congestion: List of data from the
    *             congestions of the place.
    * Return: The graph with the attributes congestion
    *         and itime.
    ----------------------------------------------------'''
    for x in range(0, len(highways)):
        # Convert the coordinates string into a list
        coordinates = highways[x].coordinates.split(',')
        for y in range(0, len(congestions)):
            # Relate same streets by the way_id
            if highways[x].way_id == congestions[y].way_id:
                # Decide which level of congestion will be added
                congestion_level = get_congestion(congestions[y])
                for i in range(0, len(coordinates) - 3, 4):
                    # Every four coordinates we define a segment of street
                    # (two pairs of points)
                    # Find the nodes from the osmnx graph nearer to the ones
                    # defined by the data in highway
                    node_start = osmnx.distance.nearest_nodes(graph, float(coordinates[i+1]), float(coordinates[i]))
                    node_end = osmnx.distance.nearest_nodes(graph, float(coordinates[i+3]), float(coordinates[i+2]))
                    try:
                        # Find the shortest path between the nodes if possible
                        # and add to the edge the congestion attribute
                        shortest_rute = osmnx.distance.shortest_path(graph, node_start, node_end, weight='length')
                        for x in range(0, len(shortest_rute)-1, 2):
                            for j in graph[x][x+1]:
                                graph[shortest_rute[x]][shortest_rute[x+1]][j]['congestion'] = congestion_level
                    except:
                        # If no shortest_path has been found, pass.
                        # A level 2 of congestion will be added later.
                        pass
    # Travese the entire graph
    for (u, v, length) in graph.edges.data('length'):
        for i in graph[u][v]:
            way = graph[u][v][i]
            # If the edge does not have the attribute congestion,
            # adjudicate level 2 (the standard one)
            if 'congestion' not in way:
                way['congestion'] = "2"
            # If the edge does not have the attribute maxspeed,
            # adjudicate 30 (the maximum pemitted in cities)
            if 'maxspeed' not in way:
                way['maxspeed'] = "30"
            # If there are more than one maxspeed for the same street
            if type(way['maxspeed']) == list:
                # Take the highest one if the congestion is low
                if way['congestion'] <= "2":
                    speed = way['maxspeed'][0]
                # Take the lowest one if the congestion level is considerable
                else:
                    speed = way['maxspeed'][1]
            else:
                speed = way['maxspeed']
            # The itime takes into consediration the time it takes going
            # through the street depending only on its length and maxspeed.
            # Then it is multiplied by the congestion level. The higher the
            # congestion level is, higher will be the itime attribute
            itime = float(length) * float(way['congestion']) / float(speed)
            # Add attribute to the graph
            way['itime'] = itime
    return graph


def get_shortest_path_with_ispeeds(igraph, actual_location, dest_location):
    '''----------------------------------------------------
    * Name: get_shortest_path_with_ispeeds
    * Function: Given two nodes of a graph, calculates
    *           the shortest path between them depending
    *           on the itime attribute.
    * Parameters: igraph: Graph of a place with congestion
    *             and itime attributes.
    *             actual_location: Node from where the
    *             user wants to go to the dest_location.
    *             dest_location: Node where we want to
    *             go from the actual_location.
    * Precondition: The graph should contain the itime
    *               attribute.
    * Return: The shortest path between actual_location
    *         and dest_location.
    ----------------------------------------------------'''
    # If the locations are not given as a word or a list, will force
    # it looks like them. Ex: if we have (41.2, 2.18), we want [41.2, 2.18]
    # Get the geocode of the locations
    if type(actual_location) == str:
        actual_location = actual_location.replace("(", "[")
        actual_location = actual_location.replace(")", "]")
        actual_loc = osmnx.geocode(actual_location)
    else:
        actual_location_str = str(actual_location)
        actual_loc = osmnx.geocode(actual_location_str)

    if type(dest_location) == str:
        dest_location = dest_location.replace("(", "[")
        dest_location = dest_location.replace(")", "]")
        dest_loc = osmnx.geocode(dest_location)
    else:
        dest_location_str = str(dest_location)
        dest_loc = osmnx.geocode(dest_location_str)
    # Get the nearest node from the one given by the geocode on the igraph
    actual_node = osmnx.distance.nearest_nodes(igraph, actual_loc[1], actual_loc[0])
    dest_node = osmnx.distance.nearest_nodes(igraph, dest_loc[1], dest_loc[0])
    # Get the shortest path between the nodes depending on the itime attribute
    path = osmnx.distance.shortest_path(igraph, actual_node, dest_node, weight='itime')
    return path


def plot_path(igraph, ipath, size):
    '''----------------------------------------------------
    * Name: plot_path
    * Function: Saves and image of a map of the place
    *           represented by the "intelligent" graph
    *           with a path between two points painted on
    *           it depending on the congestion color. The
    *           image can be ploted after using the
    *           function. This can be made thanks to
    *           StaticMap.
    * Parameters: igraph: Graph of a place with congestion
    *             and itime attributes.
    *             ipath: Shortest path between two points.
    *             size: Size of the image of the map.
    * Precondition: The path should be the shortest one
    *               between two points.
    * Return: -
    ----------------------------------------------------'''
    # Create a map of dimension (size x size)
    path_map = StaticMap(size, size)
    # Will help to know if the beginning point has been put or not
    first = True
    for i in range(1, len(ipath)-1):
        # For each node in the list of nodes that makes reference to the path,
        # mark it on the map
        # If it is the first point, mark it in blue color
        if first:
            first = False
            marker = CircleMarker((igraph.nodes[ipath[i]]['x'], igraph.nodes[ipath[i]]['y']), 'blue', 15)
        # Else mark it in the color of the congestion in that segment of
        # street and connect it to the previous point
        else:
            for j in igraph[ipath[i-1]][ipath[i]]:
                way = igraph[ipath[i-1]][ipath[i]][j]
                congestion = way['congestion']
                marker = CircleMarker((igraph.nodes[ipath[i-1]]['x'], igraph.nodes[ipath[i-1]]['y']), congestion_color(congestion), 5)
                line = path_map.add_line(Line(((igraph.nodes[ipath[i-1]]['x'], igraph.nodes[ipath[i-1]]['y']), (igraph.nodes[ipath[i]]['x'], igraph.nodes[ipath[i]]['y'])), congestion_color(congestion), 3))
        path_map.add_marker(marker)
    # The last point will be marked in red
    marker = CircleMarker((igraph.nodes[ipath[len(ipath)-1]]['x'], igraph.nodes[ipath[len(ipath)-1]]['y']), 'red', 15)
    path_map.add_marker(marker)
    # Add a line from the last point to the previous one
    line = path_map.add_line(Line(((igraph.nodes[ipath[len(ipath)-2]]['x'], igraph.nodes[ipath[len(ipath)-2]]['y']), (igraph.nodes[ipath[len(ipath)-1]]['x'], igraph.nodes[ipath[len(ipath)-1]]['y'])), 'red', 3))
    # Construct the map and save it using the name 'path.png'
    image = path_map.render()
    image.save('path.png')


def get_graph():
    '''-----------------------------------------------------
    * Name: get_graph
    * Function: Loads the graph if it exists or downloads
                it otherwise.
    * Parameters: -
    * Return: graph of a place
    -----------------------------------------------------'''
    # load/download graph (using cache)
    if not exists_graph(GRAPH_FILENAME):
        graph = download_graph(PLACE)
        save_graph(graph, GRAPH_FILENAME)
    else:
        graph = load_graph(GRAPH_FILENAME)

    return graph

def update_graph(start_time, current_time, igraph, graph, highways, congestions):
    # Compares if more than 5 minuts have passed since the last update
    if (current_time - start_time > datetime.timedelta(minutes=5)):
        # Downloads the current congestions
        congestions = download_congestions(CONGESTIONS_URL)
        # Creates a new igraph
        igraph = build_igraph(graph, highways, congestions)

    return igraph
