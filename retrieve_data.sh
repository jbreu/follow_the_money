#!/bin/bash
mkdir -p input
curl -o input/bmz-iati-export.xml https://www.transparenzportal.bund.de/api/v1/activities/download/xml/bmz-iati-export.xml
curl -o input/DE-1-Ressorts_R.xml https://teamwork.bmz.de/pub/bscw.cgi/9134919/DE-1-Ressorts_R.xml
curl -o input/DE-1-Ressorts_C.xml https://teamwork.bmz.de/pub/bscw.cgi/9134919/DE-1-Ressorts_C.xml
curl -o input/2008838.pdf https://dserver.bundestag.de/btd/20/088/2008838.pdf
curl -o input/2003843.pdf https://dserver.bundestag.de/btd/20/038/2003843.pdf