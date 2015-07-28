import datetime

from pymongo import MongoClient

from core import Graph

__author__ = 'besil'

def lines(filename, skip=lambda line: False, split=lambda line: line):
    totLines = 0
    with open(filename, 'r') as fin:
        for line in fin:
            totLines += 1

    # widgets = [FormatLabel('Processed: %(value)d lines (in: %(elapsed)s)')]
    # p = ProgressBar(maxval=totLines).start()
    count = 0
    batch_size = 3000
    with open(filename, 'r') as fin:
        start = datetime.datetime.now()
        for line in fin:
            count += 1
            if (count % batch_size == 0):
                end = datetime.datetime.now()
                print(
                    "Consumed {} lines in {}.{}s".format(batch_size, (end - start).seconds, (end - start).microseconds),
                    end="\r")
                start = datetime.datetime.now()

            # p.update(count)
            if not skip(line):
                yield split(line.strip())


def acquire_graph(filename, db_name="database", split=lambda line: line, skip=lambda line: False):
    cl = MongoClient()
    cl.drop_database(db_name)

    g = Graph(db_name=db_name)

    for line in lines(filename, skip=skip, split=split):
        g.add_edge(src=line[0], dst=line[1])

    return g