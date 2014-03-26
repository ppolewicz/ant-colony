#!/bin/sh
dot -Tsvg "$1.dot" > "$1.svg"
xsltproc notugly.xsl "$1.svg" > "$1-notugly.svg"

