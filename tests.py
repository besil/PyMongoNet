from pymongo import MongoClient

from core import Graph, graph_collection, graph_edges, neigh_attr, edges_attr
import unittest

__author__ = 'besil'

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.db_name = "test_db"
        self.cl = MongoClient()
        self.g = Graph(db_name=self.db_name, conn=self.cl)
        self.db = self.cl.get_database(self.db_name)
        self.graph_coll = self.db.get_collection(graph_collection)
        self.graph_edges = self.db.get_collection(graph_edges)

    def tearDown(self):
        self.cl.drop_database(self.db_name)
        self.cl.close()

    def test_add_node(self):
        self.g.add_node(id=1, name="Silvio")
        expected = {
            "_id": 1,
            "name": "Silvio",
        }
        self.assertEqual(self.g[1], expected, msg="Node and expected are different!")
        self.assertEquals(1, self.graph_coll.count({"_id": 1}))

    def test_delete_node(self):
        self.g.add_node(id=1, name="Silvio")
        self.g.add_node(id=2, name="Aurora")

        self.g.add_edge(src=1, dst=2)

        self.assertEquals(1, self.graph_coll.count({"_id": 1}))
        self.assertEquals(2, self.graph_coll.count())

        self.g.remove(id=1)
        self.assertEquals(0, self.graph_coll.count({"_id": 1}))
        self.assertEquals(1, self.graph_coll.count())

        self.assertFalse(self.g.contains(id=1))
        self.assertEqual(self.g[1], None, msg="Found something when nothing should be found")

        self.assertTrue(1 not in self.g[2][neigh_attr])
        self.assertTrue(0 not in self.g[2][edges_attr])

    def test_add_edge(self):
        self.g.add_node(id=1, name="Silvio")
        self.g.add_node(id=2, name="Aurora")

        self.assertEquals(1, self.graph_coll.count({"_id": 1}))
        self.assertEquals(1, self.graph_coll.count({"_id": 2}))
        self.assertEquals(2, self.graph_coll.count())

        self.g.add_edge(src=1, dst=2, weight=1.0, rel_type="love")
        self.assertEquals(1, self.graph_edges.count())
        edge = self.g.get_edge(0)

        expected_edge = {
            "_id": 0,
            "src": 1,
            "dst": 2,
            "weight": 1.0,
            "rel_type": "love"
        }

        self.assertEquals(edge, expected_edge, msg="Edge[0] is different from expected!")

        silvio = self.g[1]
        aurora = self.g[2]

        silvio_expected = {
            "_id": 1,
            "name": "Silvio",
            neigh_attr: [2],
            edges_attr: [0]
        }
        aurora_expected = {
            "_id": 2,
            "name": "Aurora",
            neigh_attr: [1],
            edges_attr: [0]
        }

        self.assertEqual(silvio, silvio_expected, msg="Silvio is different from the expected")
        self.assertEqual(aurora, aurora_expected, msg="Aurora is different from the expected")

        self.assertTrue(self.g.are_connected(src=1, dst=2), msg="Silvio and Aurora are not connected!")
        self.assertTrue(self.g.are_connected(src=2, dst=1), msg="Silvio and Aurora are not connected!")

        self.assertEqual(self.g[1][neigh_attr], silvio_expected[neigh_attr])
        self.assertEqual(self.g[2][neigh_attr], aurora_expected[neigh_attr])

        self.assertEquals(self.g[1][edges_attr], silvio_expected[edges_attr])
        self.assertEquals(self.g[2][edges_attr], aurora_expected[edges_attr])

        expected_edge = {"_id": 0, "src": 1, "dst": 2, "weight": 1.0, "rel_type": "love"}
        self.assertEquals(self.g.get_edge(edgeId=0), expected_edge)
        self.assertEquals(self.g.get_edge(edgeId=0), expected_edge)

    def test_nodes_it(self):
        self.g.add_node(id=1)
        self.g.add_node(id=2)

        expected_nodes = [{
            "_id": 1,
        }, {
            "_id": 2,
        }]

        for n in self.g.nodes():
            self.assertTrue(n in expected_nodes)

    def test_incremental_add(self):
        self.g.add_edge(src=1, dst=2)

        expected_silvio = {
            "_id": "silvio",
        }


if __name__ == '__main__':
    unittest.main()
