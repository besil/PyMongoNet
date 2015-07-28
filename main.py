from utils import acquire_graph

__author__ = 'besil'

if __name__ == '__main__':
    filename = "data/petster.dat"

    g = acquire_graph(filename, db_name="petster", split=lambda l: l.split(" "), skip=lambda l: l[0] == "%")

    print(g)