import subprocess
import os.path

class ConfigLevel:
    SYSTEM = "system"
    GLOBAL = "global"
    LOCAL = "local"

def get_config_level(level : str) -> ConfigLevel:
    if level == ConfigLevel.SYSTEM:
        return ConfigLevel.SYSTEM
    if level == ConfigLevel.GLOBAL:
        return ConfigLevel.GLOBAL
    if level == ConfigLevel.LOCAL:
        return ConfigLevel.LOCAL
    return None

def try_command(command : str) -> bool:
    try:
        return subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    except:
        return False

def remove_end(source : str) -> str:
    return source.replace("\n", "").replace("\r", "")

def have_git() -> bool:
    return try_command("git --version")
    
def have_repo() -> bool:
    return try_command("git status")

def set_config_value(name : str, value : str, level : ConfigLevel) -> bool:
    return try_command("git config --" + level + " " + name + " " + value)
    
def reset_config_value(name : str, level : ConfigLevel) -> bool:
    return try_command("git config --" + level + " --unset " + name)

def get_config_value(name : str) -> str:
    try:
        return remove_end(subprocess.run("git config --get " + name, capture_output=True, text=True).stdout)
    except:
        return ""

def add_git_attribute(pattern : str, attribute : str, value : str) -> None:
    path = ".gitattributes"
    new_line = pattern + " " + attribute + "=" + value + "\n"
    rewrite = False
    lines = []
    if os.path.isfile(path):
        with open(path, "r") as file:
            for line in file:
                line_content = [item for item in line.replace("=", " ").split(" ") if item]
                if (line_content[0] == pattern) and (line_content[1] == attribute):
                    lines += [new_line]
                    rewrite = True
                else:
                    lines += [line]
    if rewrite:
        with open(path, "w") as file:
            file.writelines(lines)
    else:
        with open(path, "a") as file:
            file.write(new_line)

def remove_git_attribute(pattern : str, attribute : str) -> None:
    path = ".gitattributes"
    rewrite = False
    lines = []
    if os.path.isfile(path):
        with open(path, "r") as file:
            for line in file:
                line_content = [item for item in line.replace("=", " ").split(" ") if item]
                if (line_content[0] == pattern) and (line_content[1] == attribute):
                    rewrite = True
                else:
                    lines += [line]
    if rewrite:
        with open(path, "w") as file:
            file.writelines(lines)
