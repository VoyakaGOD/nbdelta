from sys import argv
from cell import *

if len(argv) < 3:
    stop("You should enter 2 file paths at least!")

old_path = argv[1]
new_path = argv[2]

print(Colors.DARK_GOLD + "old" + Colors.STD + "  " + old_path)
print(Colors.GOLD + "new" + Colors.STD + "  " + new_path)

old_cells = get_cells(old_path)
new_cells = get_cells(new_path)

prescription, inserts, deletions = get_editorial_prescription(old_cells, new_cells)
old_index = 0
new_index = 0
for action in prescription:
    if(action == EditorialAction.MATCH):
        show_cells_delta(old_cells[old_index], new_cells[new_index])
        old_index += 1
        new_index += 1
    if(action == 'D'):
        print("<" + get_cell_type_title(old_cells[old_index].type) + Colors.GOLD + " deleted" + Colors.STD + ">")
        show_cell(old_cells[old_index], EditorialAction.DELETE)
        old_index += 1
    if(action == 'I'):
        print("<" + get_cell_type_title(new_cells[new_index].type) + Colors.GOLD + " inserted" + Colors.STD + ">")
        show_cell(new_cells[new_index], EditorialAction.INSERT)
        new_index += 1
    print()