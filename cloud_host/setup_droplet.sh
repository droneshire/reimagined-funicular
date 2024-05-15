#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color


THIS_DIR=`pwd`
HOME_DIR=$HOME

echo -e "${GREEN}Setting up the droplet${NC}"

PACKAGES="\
nginx \
nmap \
net-tools \
ca-certificates \
curl \
gnupg \
lsb-release \
build-essential \
make \
"
echo -e "${GREEN}Installing packages${NC}"
echo -e "${BLUE}Packages: $PACKAGES${NC}"
apt -y update
apt -y install $PACKAGES

echo -e "${GREEN}Setting up SSH${NC}"
SSH_KEY=~/.ssh/id_ed25519
KEYADD_WAIT=false
if [ ! -f $SSH_KEY]; then
    ssh-keygen -t ed25519 -C $REPO_NAME -f $SSH_KEY -q -N ""
    KEYADD_WAIT=true
fi

# Clear all old keys
ssh-add -D || eval "$(ssh-agent -s)" > /dev/null
# Add the new key
ssh-add $SSH_KEY

# Install docker
echo -e "${GREEN}Installing Docker${NC}"
./install_docker.sh

mkdir $HOME_DIR || true
cd $HOME_DIR

ssh-add -L

cd $HOME_DIR
mkdir -p ./logs || true

echo -e "${GREEN}Setting up containers${NC}"
cd $THIS_DIR
./run_containers.sh

echo -e "${GREEN}SETUP COMPLETE! Exiting...${NC}"
