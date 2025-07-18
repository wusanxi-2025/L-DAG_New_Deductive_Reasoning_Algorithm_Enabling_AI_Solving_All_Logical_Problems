#!/bin/bash

git config --global user.name "wusanxi-2025"
git config --global user.email "wusanxi@gmail.com"

# Enter the directory where your files are
cd ./L-DAG_New_Deductive_Reasoning_Algorithm_Enabling_AI_Solving_All_Logical_Problems

# Initialize the Git repository
git init

# Add all files in this directory
git add .

# Commit with a message
git commit -m "Initial commit with all project files"

# Rename the default branch to main
git branch -M main

# Add the GitHub remote repository
git remote add origin https://github.com/wusanxi-2025/L-DAG_New_Deductive_Reasoning_Algorithm_Enabling_AI_Solving_All_Logical_Problems.git

# Push to GitHub
git push -u origin main
