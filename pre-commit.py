#![path to the python interpreter]
# It's a hook for calculating approximate size of a repository (.git + working directory)
# at the time of the last commit. The values are slightly smaller than the real ones 
# since they are obtained before the new commit.
# It's also saves size info into README.md file in line starts with "![repo size]"

import pygit2
import os

def traverse_tree(repo : pygit2.Repository, tree : pygit2.Tree):
    size = 0
    for entry in tree:
        if entry.type == pygit2.GIT_OBJECT_BLOB:
            blob = repo[entry.id]
            size += blob.size
        elif entry.type == pygit2.GIT_OBJECT_TREE:
            subtree = repo[entry.id]
            traverse_tree(repo, subtree)
    return size

def get_last_commit_size():
    repo = pygit2.Repository(os.getcwd())
    default_branch_name = repo.head.shorthand
    default_branch = repo.lookup_branch(default_branch_name)
    last_commit : pygit2.Commit = default_branch.peel()
    tree = last_commit.tree
    return traverse_tree(repo, tree)

def get_dir_size(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
            except FileNotFoundError:
                pass
    return total_size

def to_human_readable(size_in_bytes):
    size = size_in_bytes
    for unit in ["b", "Kb", "Mb", "Gb", "Tb"]:
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.0f} Pb"

if __name__ == "__main__":
    commit_size = get_last_commit_size()
    repo_size = get_dir_size(os.path.join(os.getcwd(), ".git")) + commit_size
    print(f". . . .commit size: {commit_size}({to_human_readable(commit_size)})")
    print(f". . . .repo size: {repo_size}({to_human_readable(repo_size)})")
    lines = []
    with open("README.md", "r") as file:
        for line in file:
            if line.startswith("![repo size]"):
                size_string = to_human_readable(repo_size).replace(" ", "_")
                line = f"![repo size](https://img.shields.io/badge/repo_size-{size_string}-blue)\n"
            lines += [line]
    with open("README.md", "w") as file:
        file.writelines(lines)
    print(". . . .README.md changed and staged...")
