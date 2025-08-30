#!/bin/bash
set -e

error() {
    echo -e "${RED}ERROR: $1${NC}"
    sleep 5
    exit 1
}

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}>>> setting up environment...${NC}"

if [ ! -d "eda_env" ]; then
    echo "Virtual environment not found. Creating one..."
    if ! python -m venv eda_env; then
        error "failed to create virtual environment."
    fi
fi

echo -e "${GREEN}>>> activating environment...${NC}"
source eda_env/bin/activate 2>/dev/null || source eda_env/Scripts/activate 2>/dev/null || error "failed to activate virtual environment."

echo -e "${GREEN}>>> installing dependencies...${NC}"
if ! pip install -r requirements.txt; then
    error "dependency installation failed."
fi

echo -e "${GREEN}>>> preparing dataset...${NC}"
if ! python clean_dataset.py; then
    error "dataset preparation failed."
fi

echo -e "setup complete!"

sleep 5
