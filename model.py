from pymongo import MongoClient

__author__ = 'besil'

class Nodes(object):
    pass

class Edges(object):
    pass


graph_collection = "graph"
graph_edges = "edges"

class Graph(object):
    def __init__(self, db_name="database", conn=MongoClient()):
        self.db_name = db_name
        self.cl = conn

    def add_node(self, id=None, **kwargs):
        print(id)
        print(kwargs)
