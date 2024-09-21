from sys import argv
from cell import *

if len(argv) < 3:
    stop("You should enter 2 file paths at least!")

old_path = argv[1]
new_path = argv[2]

print(Colors.DARK_GOLD + "old" + Colors.STD + " " + old_path)
print(Colors.GOLD + "new" + Colors.STD + " " + new_path)

old_notebook = get_cells(old_path)
new_notebook = get_cells(new_path)

show_notebooks_delta(old_notebook, new_notebook)
