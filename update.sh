#!/bin/bash

# Enter your project directory
cd ./L-DAG_New_Deductive_Reasoning_Algorithm_Enabling_AI_Solving_All_Logical_Problems

# Add the specific files you want to update
# name="L-DAG_Deductive_Reasoning_Algorithm.pdf" 
# name="README.md"
# name="dag_DFS.py"
# name="61-paper.txt"
# name="update.sh"
# name="git.cmd"
# name=".gitconfig"
# name="3-6v-10p-64r.txt"
# name="3-6v-10p-64r.out.csv"
# name="FFL-allowed.png"
# name="cl4.py"
# name="a-8v-15p-256r.txt"
# name="a-8v-15p-256r.out.xlsx"
# name="L-DAG_Deductive_Reasoning_Algorithm-2025-07-22.docx"
# name="L-DAG_Deductive_Reasoning_Algorithm-2025-07-16.pdf"

git ls-files

#git rm "all-cl4.py"

# name="tem"
git add "$name"

# Commit with a message (you can edit this)
git commit -m "Update $name"

# Push to GitHub
git push

git ls-files