#!/bin/bash
mkdir -p input

# Function to download if file doesn't exist
download_if_not_exists() {
    if [ ! -f "input/$1" ]; then
        echo "Downloading $1..."
        curl -o "input/$1" "$2"
    else
        echo "File $1 already exists, skipping download."
    fi
}

# Read and process JSON file
if [ ! -f "data_sources.json" ]; then
    echo "Error: data_sources.json not found"
    exit 1
fi

if ! JSON=$(jq '.' data_sources.json 2>/dev/null); then
    echo "Error: Invalid JSON format in data_sources.json"
    exit 1
fi

if ! echo "$JSON" | jq -r '.sources[] | "\(.filename)|\(.link)"' | while IFS='|' read -r filename link; do
    download_if_not_exists "$filename" "$link"
done; then
    echo "Error: Missing 'sources' array in JSON"
    exit 1
fi