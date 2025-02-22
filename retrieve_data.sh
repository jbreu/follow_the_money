#!/bin/bash
mkdir -p input

# Function to download if file doesn't exist
download_if_not_exists() {
    if [ ! -f "$1" ]; then
        echo "Downloading $1..."
        curl -o "$1" "$2"
    else
        echo "File $1 already exists, skipping download."
    fi
}

# Download files only if they don't exist
download_if_not_exists "input/bmz-iati-export.xml" "https://www.transparenzportal.bund.de/api/v1/activities/download/xml/bmz-iati-export.xml"
download_if_not_exists "input/DE-1-Ressorts_R.xml" "https://teamwork.bmz.de/pub/bscw.cgi/9134919/DE-1-Ressorts_R.xml"
download_if_not_exists "input/DE-1-Ressorts_C.xml" "https://teamwork.bmz.de/pub/bscw.cgi/9134919/DE-1-Ressorts_C.xml"
download_if_not_exists "input/2008838.pdf" "https://dserver.bundestag.de/btd/20/088/2008838.pdf"
download_if_not_exists "input/2003843.pdf" "https://dserver.bundestag.de/btd/20/038/2003843.pdf"
download_if_not_exists "input/demokratie-leben1.pdf" "https://www.demokratie-leben.de/resource/blob/252438/699a8df5b62e79df459710d4108f99c7/fp1-bundesprogramm-abschlussbericht-2015-2019-data.pdf"