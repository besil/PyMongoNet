from core import Graph

__author__ = 'besil'

def lines(filename, skip=lambda line: False, split=lambda line: line):
    with open(filename, 'r') as fin:
        for line in fin:
            if not skip(line):
                yield split(line.strip())

def acquire_graph(filename, graph_name="database", split=lambda line: line, skip=lambda line: False):
    g = Graph(db_name=graph_name)

    for line in lines(filename, skip=skip, split=split):
        g.add_edge(src=line[0], dst=line[1])

    return g