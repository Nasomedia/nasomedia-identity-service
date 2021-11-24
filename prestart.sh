#! /usr/bin/env bash

# Let the DB start
python app/script/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/script/initial_data.py