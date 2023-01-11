# This file contains functions to parse connections between two components
# The type of connection is stored as a json file  './Data/part_connectiontype.json' as a dictionary

import pandas as pd
import json
import numpy as np
from ast import literal_eval


def parse_connection():
    # TODO: Convert a connection adjacency matrix to a list, containing tuples (m, n),
    # where m is the connection type and n is the part to connect
    connectiondic = {}
    datafile = pd.ExcelFile("/Users/davidw/medjw/code/MscProject/data/Data.xlsx")
    # Read the data in "Connection" Sheet
    pd_connection = pd.read_excel(
        datafile, index_col=0, sheet_name="Connection")

    for column, series in pd_connection.iteritems():
        for row, v in series.items():
            if pd.notnull(v) and v != 'x' and v != 0:
                connectiondic.setdefault(column, [])
                connectiondic.setdefault(row, [])
                connection_methods = str(v).split(',')
                for method in connection_methods:
                    connectiondic[column].append((int(method), row))
                    connectiondic[row].append((int(method), column))

    pd_connectiondic = pd.Series(connectiondic)
    pd_connectiondic.to_csv("/Users/davidw/medjw/code/MscProject/data/connectionparse.csv")


def component_connection_list():
    parsedconnections = []
    datafile = pd.ExcelFile("/Users/davidw/medjw/code/MscProject/data/Data.xlsx")
    mydata = pd.read_excel(
        datafile, index_col=None, sheet_name='Electric Motor Systems')
    connectionlist = mydata["Connection"].tolist()
    connections = [literal_eval(i) for i in connectionlist]
    components = mydata["Component Number"].tolist()

    with open("/Users/davidw/medjw/code/MscProject/data/part_connectiontype.json", 'r') as f:
        typedic = json.load(f)
    for i in range(len(components)):
        component1 = components[i]
        for connection_pair in connections[i]:
            component2 = connection_pair[1]
            connectiontype = typedic[str(connection_pair[0])]
            parsedconnections.append(
                (component1, component2, connectiontype))
    return parsedconnections


if __name__ == '__main__':
    parse_connection()
