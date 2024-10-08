from sys import argv
from cell import *
from os import system
import gitUtils as git
from os import getcwd

def stop(message : str) -> None:
    print(message)
    exit(-1)

def get_config_level_for_cmd(index : int) -> git.ConfigLevel:
    if not git.have_git():
        stop("You need git to use enable command...")
    level = git.ConfigLevel.LOCAL
    if len(argv) > index:
        level = git.get_config_level(argv[index])
        if level == None:
            stop("git config level may have only three values: local, global, system...")
    return level

def cmd_help() -> None:
    print("""commands list(= shows default value):
    help
        shows list of commands with args info
          
    config
        shows configuration info, stored in git config
          
    enable [interpreter=python] [config_level=local] [similarity=0.4] [auxiliary=-1]
        adds configuration info to appropriate config file
        similarity - value from 0 to 1 of similarity required to consider cells equals
        auxiliary - count of not changed lines around changed ones, negative values means show all
          
    disable [config_level=local]
        remove values added by previous command
          
    add-attribute
        adds line '*.ipynb diff=nbdelta' to .gitattribute file(create if it doesn't exist)
          
    rm-attribute
        remove line '*.ipynb diff=nbdelta' from .gitattribute file
          
    diff [old] [new]
        shows diff without settings
          
    git-diff [old] [new]
        shows diff using settings from git config file
""")

def cmd_config():
    print("command=(" + git.get_config_value("diff.nbdelta.command") + ")")
    print("similarity=(" + git.get_config_value("diff.nbdelta.similarity") + ")")
    print("auxiliary=(" + git.get_config_value("diff.nbdelta.auxiliary") + ")")

def cmd_enable() -> None:
    level = get_config_level_for_cmd(3)
    interpreter = "python"
    if len(argv) > 2:
        interpreter = argv[2]
    if not git.set_config_value("diff.nbdelta.command", "\"" + interpreter + " '" + getcwd() + "\\" + argv[0] + "' git-diff\"", level):
        print("Something went wrong: can't change diff.nbdelta.command in git " + level + " config...")
    if len(argv) > 4:
        if not git.set_config_value("diff.nbdelta.similarity", argv[4], level):
            print("Something went wrong: can't change diff.nbdelta.similarity in git " + level + " config...")
    if len(argv) > 5:
        if not git.set_config_value("diff.nbdelta.auxiliary", argv[5], level):
            print("Something went wrong: can't change diff.nbdelta.auxiliary in git " + level + " config...")

def remove_diff_config_value(value : str, level : git.ConfigLevel) -> None:
    if not git.reset_config_value(f"diff.nbdelta.{value}", level):
        print(f"Something went wrong: can't remove diff.nbdelta.{value} from git {level} config...")

def cmd_disable() -> None:
    level = get_config_level_for_cmd(2)
    remove_diff_config_value("command", level)
    remove_diff_config_value("similarity", level)
    remove_diff_config_value("auxiliary", level)

def cmd_add_attribute() -> None:
    git.add_git_attribute("*.ipynb", "diff", "nbdelta")
    if not git.have_repo():
        print("Success! But, there is no git repository...")

def cmd_remove_attribute() -> None:
    git.remove_git_attribute("*.ipynb", "diff")
    if not git.have_repo():
        print("Success! But, there is no git repository...")

def cmd_diff() -> None:
    if len(argv) < 4:
        stop("You should enter 2 file paths at least!")
    old_path = argv[2]
    new_path = argv[3]
    print(Colors.DARK_GOLD + "old" + Colors.STD + " " + old_path)
    print(Colors.GOLD + "new" + Colors.STD + " " + new_path)
    old_notebook = get_cells(old_path)
    new_notebook = get_cells(new_path)
    show_notebooks_delta(old_notebook, new_notebook)

def cmd_git_diff() -> None:
    if not git.have_git():
        stop("You need git to use git-diff command! Use diff intstead...")
    similarity = const.EXPECTED_CELLS_SIMILARITY
    try:
        similarity = float(git.get_config_value("diff.nbdelta.similarity"))
    except:
        pass
    if (0 <= similarity) and (similarity <= 1):
        const.EXPECTED_CELLS_SIMILARITY = similarity
    try:
        const.AUXILIARY_LINES_COUNT = int(git.get_config_value("diff.nbdelta.auxiliary"))
    except:
        pass
    cmd_diff()

commands = {
    "help" : cmd_help,
    "config" : cmd_config,
    "enable" : cmd_enable,
    "disable" : cmd_disable,
    "add-attribute" : cmd_add_attribute,
    "rm-attribute" : cmd_remove_attribute,
    "diff" : cmd_diff,
    "git-diff" : cmd_git_diff
}

if len(argv) == 1:
    stop("You should enter command as first argument...")

if argv[1] not in commands:
    stop("Unknown command [" + argv[1] + "]...")

commands[argv[1]]()
