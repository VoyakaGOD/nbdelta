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
            self.set_output(jsonObj["outputs"])
        else:
            self.output = []

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
    color = Colors.STD
    if format == EditorialAction.INSERT:
        prefix = "+ "
        color = Colors.POSITIVE
    elif format == EditorialAction.DELETE:
        prefix = "- "
        color = Colors.NEGATIVE
    for line in cell.source:
        print(color + prefix + line + Colors.STD, end=get_end(line))
    if cell.output == []:
        return
    print("[" + Colors.OUTPUT + "output" + Colors.STD + "]:")
    color = Colors.GRAY
    if format == EditorialAction.INSERT:
        color = Colors.DARK_POSITIVE
    elif format == EditorialAction.DELETE:
        color = Colors.DARK_NEGATIVE
    for line in cell.output:
        print(color + prefix + line + Colors.STD, end=get_end(line))

def display_lines_prescription(prescription : list[EditorialAction], old : list[str], new : list[str], M, I, D):
    old_index = 0
    new_index = 0
    for action in prescription:
        if(action == EditorialAction.MATCH):
            print(M + ". " + old[old_index] + Colors.STD, end=get_end(old[old_index]))
            old_index += 1
            new_index += 1
        if(action == 'D'):
            print(D + "- " + old[old_index] + Colors.STD, end=get_end(old[old_index]))
            old_index += 1
        if(action == 'I'):
            print(I + "+ " + new[new_index] + Colors.STD, end=get_end(new[new_index]))
            new_index += 1

def show_cells_delta(old : Cell, new : Cell) -> tuple[int, int]:
    prescription, insertions, deletions = get_editorial_prescription(old.source, new.source)
    out_prescription, out_insertions, out_deletions = get_editorial_prescription(old.output, new.output)
    out_tag = "" if (out_insertions + out_deletions == 0) else Colors.GOLD + " out" + Colors.STD
    print("<" + get_cell_type_title(old.type) + get_insertions_tag(insertions) + get_deletions_tag(deletions) + out_tag + ">")
    display_lines_prescription(prescription, old.source, new.source, Colors.STD, Colors.POSITIVE, Colors.NEGATIVE)
    if (old.output == []) and (new.output == []):
        return 0, 0
    print("[" + Colors.OUTPUT + "output" + Colors.STD + "]:")
    display_lines_prescription(out_prescription, old.output, new.output, Colors.GRAY, Colors.DARK_POSITIVE, Colors.DARK_NEGATIVE)
    return insertions, deletions

def show_notebooks_delta(old : list[Cell], new : list[Cell]) -> None:
    prescription, inserts, deletions = get_editorial_prescription(old, new)
    old_index = 0
    new_index = 0
    line_inserts = 0 
    line_deletions = 0
    for action in prescription:
        if(action == EditorialAction.MATCH):
            delta = show_cells_delta(old[old_index], new[new_index])
            line_inserts += delta[0]
            line_deletions += delta[1]
            old_index += 1
            new_index += 1
        if(action == 'D'):
            print("<" + get_cell_type_title(old[old_index].type)
                + get_deletions_tag(len(old[old_index].source)) + Colors.DARK_GOLD + " deleted" + Colors.STD + ">")
            show_cell(old[old_index], EditorialAction.DELETE)
            line_deletions += len(old[old_index].source)
            old_index += 1
        if(action == 'I'):
            print("<" + get_cell_type_title(new[new_index].type)
                + get_insertions_tag(len(new[new_index].source)) + Colors.GOLD + " inserted" + Colors.STD + ">")
            show_cell(new[new_index], EditorialAction.INSERT)
            line_inserts += len(new[new_index].source)
            new_index += 1
        print()
    print("Cells:" + get_insertions_tag(inserts) + get_deletions_tag(deletions))
    print("Lines:" + get_insertions_tag(line_inserts) + get_deletions_tag(line_deletions))
