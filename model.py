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
        self.db = conn.get_database(db_name)
        self.graph = self.db.get_collection(graph_collection)
        self.graph_edges = self.db.get_collection(graph_edges)

    def add_node(self, id=None, **kwargs):
        d = kwargs
        d["_id"] = id
        d["neighs"] = []
        self.graph.insert(d)

    def __getitem__(self, id):
        # return self.graph.findOne({"_id": id})
        return self.graph.find_one({"_id": id})
