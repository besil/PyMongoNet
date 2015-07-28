from pymongo import MongoClient

__author__ = 'besil'

graph_collection = "graph"
graph_edges = "edges"

graph_id = "_id"
neigh_attr = "_neighs"
edges_attr = "_edges"


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
        d[graph_id] = id
        self.graph.insert(d)

    def add_edge(self, src, dst, **kwargs):
        d = kwargs
        edgeId = self.edge_count
        self.edge_count += 1

        edge_doc = {
            graph_id: edgeId,
            "src": src,
            "dst": dst,
        }

        for k, v in kwargs.items():
            edge_doc[k] = v

        self.graph_edges.insert(edge_doc)

        self.graph.update_one({graph_id: src}, {"$push": {neigh_attr: dst}})
        self.graph.update_one({graph_id: src}, {"$push": {edges_attr: edgeId}})

        self.graph.update_one({graph_id: dst}, {"$push": {neigh_attr: src}})
        self.graph.update_one({graph_id: dst}, {"$push": {edges_attr: edgeId}})

    def are_connected(self, src, dst):
        return dst in self[src][neigh_attr] or src in self[dst][neigh_attr]

    def get_edge(self, edgeId):
        return self.graph_edges.find_one({graph_id: edgeId})

    def __getitem__(self, id):
        return self.graph.find_one({graph_id: id})

    def contains(self, id):
        return sum([1 for _ in self.graph.find({graph_id: id})]) == 1

    def remove(self, id):
        node = self[id]

        edges = node[edges_attr]
        neighs = node[neigh_attr]

        self.graph.delete_one({graph_id: id})
        for edge in edges:
            self.edge_count -= 1
            self.graph_edges.delete_one({graph_id: edge})

        for neigh in neighs:
            neigh_doc = self[neigh]
            neigh_doc[neigh_attr].remove(id)
            for edge in edges:
                neigh_doc[edges_attr].remove(edge)
            self.graph.replace_one({graph_id: neigh}, neigh_doc)

    def nodes(self):
        for n in self.graph.find():
            yield n