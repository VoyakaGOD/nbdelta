from stop import stop
from constants import Colors
from diff import *
import json
import constants as const
from typing import Any

def get_short_string(obj : Any, max_len : int):
    raw = str(obj)
    max_len = max(3, max_len)
    return (raw[0:max_len - 3] + "...") if (len(raw) > max_len) else raw

class Cell:
    def __init__(self, jsonObj : dict):
        if ("cell_type" not in jsonObj) or ("source" not in jsonObj):
            stop("Bad cell(has no type or no source)!")
        self.type = jsonObj["cell_type"]
        self.source = jsonObj["source"]
        if "outputs" in jsonObj:
            self.set_output(jsonObj["outputs"])
        else:
            self.output = []

    def __eq__(self, other : Any):
        if type(self) != type(other):
            return False
        if self.type != other.type:
            return False
        distance = get_editorial_matrix(self.source, other.source)[len(self.source)][len(other.source)]
        return distance <= (1 - const.EXPECTED_CELLS_SIMILARITY) * (len(self.source) + len(other.source))
    
    def set_output(self, output : dict):
        max_len = const.MAX_OUTPUT_LINE_LENGTH
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
                    self.output += ["    " + key + ": " + get_short_string(data[key], max_len)]
            else:
                self.output += [item_type]

def get_cells(path : str):
    data = None
    try:
        with open(path, encoding="utf8") as file:
            data = json.loads(file.read())
    except:
        stop("Can't open file[" + path + "] in correct format!")
    if "cells" not in data:
        stop("[" + path + "] is not a notebook file!")
    return [Cell(item) for item in data["cells"]]

def get_cell_type_title(type : str):
    color_palette = {"code" : Colors.CODE, "markdown" : Colors.MARKDOWN}
    color = color_palette.get(type, Colors.STD)
    return color + type + Colors.STD

def get_end(line : str):
    return "" if line[-1] == "\n" else "\n"

def get_insertions_tag(count : int):
    return (" " + Colors.POSITIVE + "+" + str(count) + Colors.STD) if (count > 0) else ""

def get_deletions_tag(count : int):
    return (" " + Colors.NEGATIVE + "-" + str(count) + Colors.STD) if (count > 0) else ""

def show_cell(cell : Cell, format : EditorialAction):
    prefix_palette = {
        EditorialAction.INSERT : Colors.POSITIVE + "+ ",
        EditorialAction.DELETE : Colors.NEGATIVE + "- "
    }
    prefix = prefix_palette.get(format, Colors.STD + ". ")
    for line in cell.source:
        print(prefix + line + Colors.STD, end=get_end(line))
    if cell.output == []:
        return
    print("[" + Colors.OUTPUT + "output" + Colors.STD + "]")
    output_color_palette = {
        EditorialAction.INSERT : Colors.DARK_POSITIVE,
        EditorialAction.DELETE : Colors.DARK_NEGATIVE
    }
    color = output_color_palette.get(format, Colors.GRAY)
    for line in cell.output:
        print(color + prefix + line + Colors.STD, end=get_end(line))

def is_nearby_lines_changed(prescription : list[EditorialAction], index : int):
    if const.AUXILIARY_LINES_COUNT < 0:
        return True
    begin = max(0, index - const.AUXILIARY_LINES_COUNT)
    end = min(index + const.AUXILIARY_LINES_COUNT + 1, len(prescription))
    for i in range(begin, end):
        if prescription[i] != EditorialAction.MATCH:
            return True
    return False

def display_lines_prescription(prescription : list[EditorialAction], 
                               old : list[str],
                               new : list[str],
                               match_color : Colors,
                               insertion_color : Colors,
                               deletion_color : Colors):
    old_index = 0
    new_index = 0
    for index, action in enumerate(prescription):
        if (action == EditorialAction.MATCH) and is_nearby_lines_changed(prescription, index):
            print(match_color + ". " + old[old_index] + Colors.STD, end=get_end(old[old_index]))
            old_index += 1
            new_index += 1
        elif action == EditorialAction.DELETE:
            print(deletion_color + "- " + old[old_index] + Colors.STD, end=get_end(old[old_index]))
            old_index += 1
        elif action == EditorialAction.INSERT:
            print(insertion_color + "+ " + new[new_index] + Colors.STD, end=get_end(new[new_index]))
            new_index += 1

def show_cells_delta(old : Cell, new : Cell):
    prescription, insertions, deletions = get_editorial_prescription(old.source, new.source)
    out_prescription, out_insertions, out_deletions = get_editorial_prescription(old.output, new.output)
    out_tag = "" if (out_insertions + out_deletions == 0) else Colors.GOLD + " out" + Colors.STD
    print("<" + get_cell_type_title(old.type) + get_insertions_tag(insertions)
          + get_deletions_tag(deletions) + out_tag + ">")
    display_lines_prescription(prescription, old.source, new.source, Colors.STD, Colors.POSITIVE, Colors.NEGATIVE)
    if (old.output == []) and (new.output == []):
        return insertions, deletions
    print("[" + Colors.OUTPUT + "output" + Colors.STD + "]")
    display_lines_prescription(out_prescription, old.output, new.output,
        Colors.GRAY, Colors.DARK_POSITIVE, Colors.DARK_NEGATIVE)
    return insertions, deletions

def get_diff_summary(inserts, deletions):
    if inserts + deletions == 0:
        return Colors.DARK_GOLD + " @" + Colors.STD
    return get_insertions_tag(inserts) + get_deletions_tag(deletions)

def show_notebooks_delta(old : list[Cell], new : list[Cell]) -> None:
    prescription, inserts, deletions = get_editorial_prescription(old, new)
    old_index = 0
    new_index = 0
    line_inserts = 0 
    line_deletions = 0
    for action in prescription:
        if action == EditorialAction.MATCH:
            delta = show_cells_delta(old[old_index], new[new_index])
            line_inserts += delta[0]
            line_deletions += delta[1]
            old_index += 1
            new_index += 1
        if action == EditorialAction.DELETE:
            print("<" + get_cell_type_title(old[old_index].type)
                + get_deletions_tag(len(old[old_index].source)) + Colors.DARK_GOLD + " deleted" + Colors.STD + ">")
            show_cell(old[old_index], EditorialAction.DELETE)
            line_deletions += len(old[old_index].source)
            old_index += 1
        if action == EditorialAction.INSERT:
            print("<" + get_cell_type_title(new[new_index].type)
                + get_insertions_tag(len(new[new_index].source)) + Colors.GOLD + " inserted" + Colors.STD + ">")
            show_cell(new[new_index], EditorialAction.INSERT)
            line_inserts += len(new[new_index].source)
            new_index += 1
        print()
    print("Cells:" + get_diff_summary(inserts, deletions))
    print("Lines:" + get_diff_summary(line_inserts, line_deletions))
