import unittest

from pymongo import MongoClient

from core import Graph, graph_collection, graph_edges

__author__ = 'besil'


class TestCoreMethods(unittest.TestCase):
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
            self.g.graph_id: 1,
            "name": "Silvio",
        }
        self.assertEqual(self.g[1], expected, msg="Node and expected are different!")
        self.assertEqual(1, self.graph_coll.count({self.g.graph_id: 1}))

    def test_delete_node(self):
        self.g.add_node(id=1, name="Silvio")
        self.g.add_node(id=2, name="Aurora")

        self.g.add_edge(src=1, dst=2)

        self.assertEqual(1, self.graph_coll.count({self.g.graph_id: 1}))
        self.assertEqual(2, self.graph_coll.count())

        self.g.remove(id=1)
        self.assertEqual(0, self.graph_coll.count({self.g.graph_id: 1}))
        self.assertEqual(1, self.graph_coll.count())

        self.assertFalse(self.g.contains(id=1))
        self.assertEqual(self.g[1], None, msg="Found something when nothing should be found")

        self.assertTrue(1 not in self.g[2][self.g.neigh_attr])
        self.assertTrue(0 not in self.g[2][self.g.edges_attr])

    def test_add_edge(self):
        self.g.add_node(id=1, name="Silvio")
        self.g.add_node(id=2, name="Aurora")

        self.assertEqual(1, self.graph_coll.count({self.g.graph_id: 1}))
        self.assertEqual(1, self.graph_coll.count({self.g.graph_id: 2}))
        self.assertEqual(2, self.graph_coll.count())

        self.g.add_edge(src=1, dst=2, weight=1.0, rel_type="love")
        self.assertEqual(1, self.graph_edges.count())
        edge = self.g.get_edge(0)

        expected_edge = {
            self.g.graph_id: 0,
            "src": 1,
            "dst": 2,
            "weight": 1.0,
            "rel_type": "love"
        }

        self.assertEqual(edge, expected_edge, msg="Edge[0] is different from expected!")

        silvio = self.g[1]
        aurora = self.g[2]

        silvio_expected = {
            self.g.graph_id: 1,
            "name": "Silvio",
            self.g.neigh_attr: [2],
            self.g.edges_attr: [0]
        }
        aurora_expected = {
            self.g.graph_id: 2,
            "name": "Aurora",
            self.g.neigh_attr: [1],
            self.g.edges_attr: [0]
        }

        self.assertEqual(silvio, silvio_expected, msg="Silvio is different from the expected")
        self.assertEqual(aurora, aurora_expected, msg="Aurora is different from the expected")

        self.assertTrue(self.g.are_connected(src=1, dst=2), msg="Silvio and Aurora are not connected!")
        self.assertTrue(self.g.are_connected(src=2, dst=1), msg="Silvio and Aurora are not connected!")

        self.assertEqual(self.g[1][self.g.neigh_attr], silvio_expected[self.g.neigh_attr])
        self.assertEqual(self.g[2][self.g.neigh_attr], aurora_expected[self.g.neigh_attr])

        self.assertEqual(self.g[1][self.g.edges_attr], silvio_expected[self.g.edges_attr])
        self.assertEqual(self.g[2][self.g.edges_attr], aurora_expected[self.g.edges_attr])

        expected_edge = {self.g.graph_id: 0, "src": 1, "dst": 2, "weight": 1.0, "rel_type": "love"}
        self.assertEqual(self.g.get_edge(edgeId=0), expected_edge)
        self.assertEqual(self.g.get_edge(edgeId=0), expected_edge)

    def test_nodes_it(self):
        self.g.add_node(id=1)
        self.g.add_node(id=2)

        expected_nodes = [{
            self.g.graph_id: 1,
        }, {
            self.g.graph_id: 2,
        }]

        for n in self.g.nodes():
            self.assertTrue(n in expected_nodes)

    def test_incremental_add(self):
        self.g.add_edge(src=1, dst=2)

        print(self.g)
        print(self.g[1])

        self.assertEqual(self.g[1], {self.g.graph_id: 1, self.g.edges_attr: [0], self.g.neigh_attr: [2]}, msg="Node[1] should be created!")
        self.assertEqual(self.g[2], {self.g.graph_id: 2, self.g.edges_attr: [0], self.g.neigh_attr: [1]}, msg="Node[2] should be created!")

        self.assertEqual(self.g[1][self.g.edges_attr], [0])
        self.assertEqual(self.g[2][self.g.edges_attr], [0])

        self.assertEqual(self.g[1][self.g.neigh_attr], [2])
        self.assertEqual(self.g[2][self.g.neigh_attr], [1])


if __name__ == '__main__':
    unittest.main()
