from stop import stop
from constants import *
from diff import *
import json

def get_short_string(obj):
    raw = str(obj)
    return (raw[0:61] + "...") if (len(raw) > 64) else raw

class Cell:
    def __init__(self, jsonObj):
        if ("cell_type" not in jsonObj) or ("source" not in jsonObj):
            stop("Bad cell(has no type or no source)!")
        self.type = jsonObj["cell_type"]
        self.source = jsonObj["source"]
        if "outputs" in jsonObj:
            self.output = jsonObj["outputs"]
            if self.output == []:
                self.output = None
            else:
                self.set_output(self.output)
        else:
            self.output = None

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        if self.type != other.type:
            return False
        distance = get_editorial_matrix(self.source, other.source)[len(self.source)][len(other.source)]
        return distance <= EXPECTED_CELLS_SIMILARITY * (len(self.source) + len(other.source))
    
    def set_output(self, output):
        self.output = []
        for item in output:
            item_type = item["output_type"]
            if item_type == "error":
                self.output += [item_type + "(" + item["ename"] + ")"]
            elif item_type == "stream":
                self.output += [item_type + "(" + item["name"] + ")"]
            elif (item_type == "display_data") or (item_type == "execute_result"):
                data = item["data"]
                self.output += [item_type + ":"]
                for key in data.keys():
                    self.output += ["    " + key + ": " + get_short_string(data[key])]
            else:
                self.output += [item_type]

def get_cells(path : str) -> list[Cell]:
    data = None
    try:
        with open(path, encoding="utf8") as file:
            data = json.loads(file.read())
    except:
        stop("Can't open file[" + path + "] in correct format!")
    if "cells" not in data:
        stop("[" + path + "] is not a notebook file!")
    return [Cell(item) for item in data["cells"]]

def get_cell_type_title(type):
    if type == "code":
        return Colors.CODE + type + Colors.STD
    if type == "markdown":
        return Colors.MARKDOWN + type + Colors.STD
    return type

def get_end(line):
    return "" if line[-1] == "\n" else "\n"

def get_insertions_tag(count):
    return (" " + Colors.POSITIVE + "+" + str(count) + Colors.STD) if (count > 0) else ""

def get_deletions_tag(count):
    return (" " + Colors.NEGATIVE + "-" + str(count) + Colors.STD) if (count > 0) else ""

def show_cell(cell : Cell, format : EditorialAction):
    prefix = ". "
    if format == EditorialAction.INSERT:
        prefix = "+ "
        print(Colors.POSITIVE, end="")
    elif format == EditorialAction.DELETE:
        prefix = "- "
        print(Colors.NEGATIVE, end="")
    for line in cell.source:
        print(prefix + line, end=get_end(line))
    print(Colors.STD, end="")
    if cell.output is None:
        return
    print("[" + Colors.OUTPUT + "output" + Colors.STD + "]:")
    if format == EditorialAction.INSERT:
        print(Colors.DARK_POSITIVE, end="")
    elif format == EditorialAction.DELETE:
        print(Colors.DARK_NEGATIVE, end="")
    else:
        print(Colors.GRAY, end="")
    for line in cell.output:
        print(prefix + line, end=get_end(line))
    print(Colors.STD, end="")

def show_cells_delta(old : Cell, new : Cell):
    prescription, insertions, deletions = get_editorial_prescription(old.source, new.source)
    old_index = 0
    new_index = 0
    print("<" + get_cell_type_title(old.type) + get_insertions_tag(insertions) + get_deletions_tag(deletions) + ">")
    for action in prescription:
        if(action == EditorialAction.MATCH):
            print(". " + old.source[old_index], end=get_end(old.source[old_index]))
            old_index += 1
            new_index += 1
        if(action == 'D'):
            print(Colors.NEGATIVE + "- " + old.source[old_index] + Colors.STD, end=get_end(old.source[old_index]))
            old_index += 1
        if(action == 'I'):
            print(Colors.POSITIVE + "+ " + new.source[new_index] + Colors.STD, end=get_end(new.source[new_index]))
            new_index += 1
    if old.output is None:
        return
    print("[" + Colors.OUTPUT + "output" + Colors.STD + "]:")
    for line in old.output:
        print(Colors.GRAY + ". " + line + Colors.STD)
