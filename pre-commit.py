#! [path to the python interpreter]

import os
import sys

ignore_list = [".git\\", ".git/", ".ipynb", "__pycache__", ".gitattributes"]

def is_ignored(path):
    for part in ignore_list:
        if part in path:
            return True
    return False

def get_repo_size():
    total_size = 0
    repo_path = os.getcwd()
    for dir_path, dir_names, file_names in os.walk(repo_path):
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            if is_ignored(file_path):
                continue
            total_size += os.path.getsize(file_path)

    return total_size // 1024

size = get_repo_size()
print(". . . .repo size:", size, "kb")

lines = []
with open("README.md", "r") as file:
    for line in file:
        if line.startswith("![repo size]"):
            lines += [f"![repo size](https://img.shields.io/badge/repo_size-{size}_kb-blue)\n"]
        else:
            lines += [line]
with open("README.md", "w") as file:
    file.writelines(lines)

os.system("git add README.md")
print(". . . .README.md changed and staged...")