#!/bin/bash

# https://github.com/wusanxi-2025/L-DAG_New_Deductive_Reasoning_Algorithm_Enabling_AI_Solving_All_Logical_Problems.git
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
# name="a-8v-15p-256r.txt"
# name="a-8v-15p-256r.out.xlsx"
# name="L-DAG_Deductive_Reasoning_Algorithm-2025-07-22.docx"
# name="L-DAG_Deductive_Reasoning_Algorithm-2025-07-16.pdf"
# name="test-a-8v-15p-256r.txt"
# name="8v.docx"
# name="cl4.py"
# name="d-8v-15p-256r.txt"
# name="d-8v-15p-256r.out.xlsx"
# name="c-8v-15p-256r.txt"
# name="c-8v-15p-256r.out.xlsx"
# name="c-v8-DAG.docx"
# name="./AI_test/Claude-4-2025-08-17-test-example-1.pdf"
# name="./AI_test/Claude-4-2025-08-14-test-example-2.pdf"
# name="./AI_test/gemini-2.5-2025-08-17-test-example-1.pdf"

git ls-files

name="update.sh"

#git rm "$name"

git add "$name"

# Commit with a message (you can edit this)
git commit -m "Update $name"

# Push to GitHub
git push

git ls-files