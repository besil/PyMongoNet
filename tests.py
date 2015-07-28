from pymongo import MongoClient

from model import Graph, graph_collection, graph_edges

__author__ = 'besil'
import unittest


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
            "neighs": []
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

        self.assertTrue(1 not in self.g[2]["neighs"])
        self.assertTrue(0 not in self.g[2]["edges"])

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
            "neighs": [2],
            "edges": [0]
        }
        aurora_expected = {
            "_id": 2,
            "name": "Aurora",
            "neighs": [1],
            "edges": [0]
        }

        self.assertEqual(silvio, silvio_expected, msg="Silvio is different from the expected")
        self.assertEqual(aurora, aurora_expected, msg="Aurora is different from the expected")

        self.assertTrue(self.g.are_connected(src=1, dst=2), msg="Silvio and Aurora are not connected!")
        self.assertTrue(self.g.are_connected(src=2, dst=1), msg="Silvio and Aurora are not connected!")

        self.assertEqual(self.g[1]["neighs"], silvio_expected['neighs'])
        self.assertEqual(self.g[2]["neighs"], aurora_expected['neighs'])

        # self.assertEquals(self.g[1]["edges"], [{"node": 2, "edge": 0}])
        # self.assertEquals(self.g[2]["edges"], [{"node": 1, "edge": 0}])
        self.assertEquals(self.g[1]["edges"], silvio_expected['edges'])
        self.assertEquals(self.g[2]["edges"], aurora_expected['edges'])

        expected_edge = {"_id": 0, "src": 1, "dst": 2, "weight": 1.0, "rel_type": "love"}
        self.assertEquals(self.g.get_edge(edgeId=0), expected_edge)
        self.assertEquals(self.g.get_edge(edgeId=0), expected_edge)


if __name__ == '__main__':
    unittest.main()
