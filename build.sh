#!/bin/bash

# Build the project
echo "Building the project..."
python3 -m pip install -r requirements.txt

# Make Migrations
echo "Making migrations..."
python3 manage.py makemigrations 
python3 manage.py migrate 

