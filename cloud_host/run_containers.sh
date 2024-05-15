#!/bin/bash

set -e

HOME_DIR=$HOME
cd $HOME_DIR

make docker_compose_down
make docker_compose_clean
make docker_compose_up

echo "Docker containers are up and running"

echo "You can stop the containers by running the following command:"
echo "make docker_compose_down"
