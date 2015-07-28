from pymongo import MongoClient

from model import Graph, graph_collection, graph_edges

__author__ = 'besil'
import unittest


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.db_name = "test_db"
        self.graph_collection = graph_collection
        self.graph_edges = graph_edges
        self.cl = MongoClient()
        self.g = Graph(db_name=self.db_name, conn=self.cl)
        self.test_coll = self.cl.get_database(self.db_name).get_collection(self.graph_collection)

    def tearDown(self):
        self.cl.close()

    def test_add_node(self):
        self.g.add_node(id=1, name="Silvio")
        expected = {
            "_id": 1,
            "name": "Silvio",
            "neighs": []
        }
        self.assertEqual(self.g[1], expected, msg="Node and expected are different!")

        self.assertEquals(1, self.graph_coll.count({"_id": 1}))

    def test_delete_node(self):
        self.g.add_node(id=1, name="Silvio")
        self.assertEquals(1, self.graph_coll.count({"_id": 1}))

        self.g.remove[1]
        self.assertEquals(0, self.graph_coll.count({"_id": 1}))

        self.assertFalse(self.g.contains(1))
        self.assertEqual(self.g[1], dict(), msg="Found something when nothing should be found")

    def test_add_edge(self):
        self.g.add_node(id=1, name="Silvio")
        self.g.add_node(id=2, name="Aurora")

        self.assertEquals(1, self.graph_coll.count({"_id": 1}))
        self.assertEquals(1, self.graph_coll.count({"_id": 2}))
        self.assertEquals(2, self.graph_coll.count())

        self.g.add_edge(src=1, dst=2, weight=1.0, rel_type="love")
        self.assertEquals(1, self.graph_edges.count())

        silvio = self.g[1]
        aurora = self.g[2]

        silvio_expected = {
            "_id": 1,
            "name": "Silvio",
            "neighs": [2],
            "edges": [(2, 0)]
        }
        aurora_expected = {
            "_id": 2,
            "name": "Aurora",
            "neighs": [1],
            "edges": [(1, 0)]
        }

        self.assertEqual(silvio, silvio_expected, msg="Silvio is different from the expected")
        self.assertEqual(aurora, aurora_expected, msg="Aurora is different from the expected")

        self.assertTrue(self.g.are_connected(src=1, dst=2))
        self.assertTrue(self.g.are_connected(src=2, dst=1))

        self.assertEqual(self.g[1]["neighs"], [2])
        self.assertEqual(self.g[2]["neighs"], [1])

        self.assertEquals(self.g[1]["edges"], [(2, 0)])
        self.assertEquals(self.g[2]["edges"], [(1, 0)])

        expected_edge = {"_id": 0, "weight": 1.0, "rel_type": "love"}
        self.assertEquals(self.g.get_edge(src=1, dst=2), expected_edge)
        self.assertEquals(self.g.get_edge(src=2, dst=1), expected_edge)


if __name__ == '__main__':
    unittest.main()
