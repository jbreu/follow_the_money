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
JSON=$(cat data_sources.json)
SOURCES=$(echo "$JSON" | jq -r '.sources[]')

echo "$SOURCES" | while IFS= read -r source; do
    filename=$(echo "$source" | jq -r '.filename')
    link=$(echo "$source" | jq -r '.link')
    download_if_not_exists "$filename" "$link"
done