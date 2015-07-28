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

        # Mongo Stuff
        self.cl = conn
        self.db = conn.get_database(db_name)
        self.graph = self.db.get_collection(graph_collection)
        self.graph_edges = self.db.get_collection(graph_edges)

        # Graph metrics
        self.edge_count = 0

    def add_node(self, id, **kwargs):
        d = kwargs
        d["_id"] = id
        d["neighs"] = []
        self.graph.insert(d)

    def add_edge(self, src, dst, **kwargs):
        d = kwargs
        edgeId = self.edge_count
        self.edge_count += 1

        edge_doc = {
            "_id": edgeId,
            "src": src,
            "dst": dst,
        }

        for k, v in kwargs.items():
            edge_doc[k] = v

        self.graph_edges.insert(edge_doc)

        self.graph.update_one({"_id": src}, {"$push": {"neighs": dst}})
        self.graph.update_one({"_id": src}, {"$push": {"edges": {"node": dst, "edge": edgeId}}})

        self.graph.update_one({"_id": dst}, {"$push": {"neighs": src}})
        self.graph.update_one({"_id": dst}, {"$push": {"edges": {"node": src, "edge": edgeId}}})

    def get_edge(self, id):
        return self.graph_edges.find_one({"_id": id})

    def __getitem__(self, id):
        return self.graph.find_one({"_id": id})
