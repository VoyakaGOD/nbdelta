# General

![GPL-3.0 license](https://img.shields.io/badge/license-GPL--3.0-red)
![git diff](https://img.shields.io/badge/git-diff-white)
![Jupyter Notebook](https://img.shields.io/badge/Jupyter_Notebook-F37726)
![repo size](https://img.shields.io/badge/repo_size-130_kb-blue)

**nbdelta** is a tool to compare two **.ipynb** files.

And there is some features to simplify and customize collaborative work with **git**.

![example1](example1.png)
![example2](example2.png)

# Commands list

*= - shows default value*

`help`

    shows list of commands with args info

`config`

    shows configuration info, stored in git config
      
`enable [interpreter=python] [config_level=local] [similarity=0.4] [auxiliary=-1]`

    adds configuration info to appropriate config file

    similarity - value from 0 to 1 of similarity required to consider cells equals
    
    auxiliary - count of not changed lines around changed ones, negative values means show all
      
`disable [config_level=local]`

    remove values added by previous command
      
`add-attribute`

    adds line '*.ipynb diff=nbdelta' to .gitattribute file(create if it doesn't exist)
      
`rm-attribute`

    remove line '*.ipynb diff=nbdelta' from .gitattribute file
      
`diff [old] [new]`

    shows diff without settings
      
`git-diff [old] [new]`

    shows diff using settings from git config file

# Usage

You can use nbdelta in 3 ways:

## I. As detached program

## II. As submodule

## III. As python module(coming soon)