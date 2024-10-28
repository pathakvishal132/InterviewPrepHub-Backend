#!/bin/bash

# Build the project
pip install setuptools
pip install -r requirements.txt
echo "Making migrations..."
python manage.py makemigrations 
python manage.py migrate 

