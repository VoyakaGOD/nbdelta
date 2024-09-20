from stop import stop
from constants import *
from diff import *
import json

class Cell:
    def __init__(self, jsonObj):
        if ("cell_type" not in jsonObj) or ("source" not in jsonObj):
            stop("Bad cell(has no type or no source)!")
        self.type = jsonObj["cell_type"]
        self.source = jsonObj["source"]
        if "outputs" in jsonObj:
            self.output = jsonObj["outputs"]

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        if self.type != other.type:
            return False
        distance = get_editorial_matrix(self.source, other.source)[len(self.source)][len(other.source)]
        return distance <= EXPECTED_CELLS_SIMILARITY * (len(self.source) + len(other.source))

def get_cells(path : str) -> list[Cell]:
    data = None
    try:
        with open(path) as file:
            data = json.loads(file.read())
    except:
        stop("Can't open file[" + path + "] in correct format!")
    if "cells" not in data:
        stop("[" + path + "] is not a notebook file!")
    return [Cell(item) for item in data["cells"]]

def show_cells_diff(old : Cell, new : Cell):
    pass