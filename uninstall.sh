#!/bin/bash

echo "$(tput setaf 2)[INF]$(tput sgr0) Removing symbolic links for the build tools..."
echo

rm /usr/local/bin/base_compress.py
rm /usr/local/bin/css_compress.py
rm /usr/local/bin/js_compress.py
rm /usr/local/bin/utley.py

echo
echo "$(tput setaf 2)[INF]$(tput sgr0) Uninstall complete."

