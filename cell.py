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
        else:
            self.output = []

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

def show_cell(cell : Cell, format : EditorialAction):
    prefix = ". "
    if format == EditorialAction.INSERT:
        prefix = "+ "
        print(Colors.POSITIVE, end="")
    elif format == EditorialAction.DELETE:
        prefix = "- "
        print(Colors.NEGATIVE, end="")
    for line in cell.source:
        print(prefix + line, end="" if line[-1] == "\n" else "\n")
    print(Colors.STD, end="")

def show_cells_delta(old : Cell, new : Cell):
    prescription, inserts, deletions = get_editorial_prescription(old.source, new.source)
    old_index = 0
    new_index = 0
    title_color = (Colors.MARKDOWN if old.type == "markdown" else Colors.CODE)
    inserts_text = (" " + Colors.POSITIVE + "+" + str(inserts) + Colors.STD) if (inserts > 0) else ""
    deletions_text = (" " + Colors.NEGATIVE + "-" + str(deletions) + Colors.STD) if (deletions > 0) else ""
    print("<" + title_color + old.type + Colors.STD + inserts_text + deletions_text + ">")
    for action in prescription:
        if(action == EditorialAction.MATCH):
            print(". " + old.source[old_index], end="" if old.source[old_index][-1] == "\n" else "\n")
            old_index += 1
            new_index += 1
        if(action == 'D'):
            print(Colors.NEGATIVE + "- " + old.source[old_index] + Colors.STD, end="" if old.source[old_index][-1] == "\n" else "\n")
            old_index += 1
        if(action == 'I'):
            print(Colors.POSITIVE + "+ " + new.source[new_index] + Colors.STD, end="" if new.source[new_index][-1] == "\n" else "\n")
            new_index += 1
