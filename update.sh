#!/bin/bash

# Enter your project directory
cd ./L-DAG_New_Deductive_Reasoning_Algorithm_Enabling_AI_Solving_All_Logical_Problems

# Add the specific files you want to update
# L-DAG_Deductive_Reasoning_Algorithm.pdf 
# README.md
# all-cl4-1.py
# dag_DFS.py

name="61-paper.txt"
git add "$name"

# Commit with a message (you can edit this)
git commit -m "Update $name"

# Push to GitHub
git push
