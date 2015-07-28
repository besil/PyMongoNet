from pymongo import MongoClient

__author__ = 'besil'

graph_collection = "graph"
graph_edges = "edges"


class Graph(object):
    def __init__(self, db_name="database", conn=MongoClient()):
        self.db_name = db_name
        self.__graph_id = "_id"
        self.__neigh_attr = "_neighs"
        self.__edges_attr = "_edges"

        # Mongo Stuff
        self.cl = conn
        self.db = conn.get_database(db_name)
        self.graph = self.db.get_collection(graph_collection)
        self.graph_edges = self.db.get_collection(graph_edges)

        # Graph metrics
        self.edge_count = 0

    @property
    def graph_id(self):
        return self.__graph_id

    @property
    def neigh_attr(self):
        return self.__neigh_attr

    @property
    def edges_attr(self):
        return self.__edges_attr

    def add_node(self, id, **kwargs):
        d = kwargs
        d[self.graph_id] = id
        self.graph.insert(d)

    def add_edge(self, src, dst, **kwargs):
        d = kwargs
        edgeId = self.edge_count
        self.edge_count += 1

        edge_doc = {
            self.graph_id: edgeId,
            "src": src,
            "dst": dst,
        }

        for k, v in kwargs.items():
            edge_doc[k] = v

        self.graph_edges.insert(edge_doc)

        self.graph.update_one({self.graph_id: src}, {"$push": {self.neigh_attr: dst}}, upsert=True)
        self.graph.update_one({self.graph_id: src}, {"$push": {self.edges_attr: edgeId}}, upsert=True)

        self.graph.update_one({self.graph_id: dst}, {"$push": {self.neigh_attr: src}}, upsert=True)
        self.graph.update_one({self.graph_id: dst}, {"$push": {self.edges_attr: edgeId}}, upsert=True)

    def are_connected(self, src, dst):
        return dst in self[src][self.neigh_attr] or src in self[dst][self.neigh_attr]

    def get_edge(self, edgeId):
        return self.graph_edges.find_one({self.graph_id: edgeId})

    def contains(self, id):
        return sum([1 for _ in self.graph.find({self.graph_id: id})]) == 1

    def remove(self, id):
        node = self[id]

        edges = node[self.edges_attr]
        neighs = node[self.neigh_attr]

        self.graph.delete_one({self.graph_id: id})
        for edge in edges:
            self.edge_count -= 1
            self.graph_edges.delete_one({self.graph_id: edge})

        for neigh in neighs:
            neigh_doc = self[neigh]
            neigh_doc[self.neigh_attr].remove(id)
            for edge in edges:
                neigh_doc[self.edges_attr].remove(edge)
            self.graph.replace_one({self.graph_id: neigh}, neigh_doc)

    def nodes(self):
        for n in self.graph.find():
            yield n

    def __getitem__(self, id):
        return self.graph.find_one({self.graph_id: id})

    def __str__(self):
        res = ""
        for n in self.nodes():
            res += "{}: {}\n".format( n[self.graph_id], n[self.neigh_attr] )
        return res