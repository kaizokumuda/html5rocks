#!/usr/bin/env bash
rm index.html
cat header.html >> index.html
markdown index.md >> index.html
cat footer.html >> index.html
