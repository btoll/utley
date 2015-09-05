#!/bin/bash

echo "$(tput setaf 2)[INF]$(tput sgr0) Installing Python build tools..."

ln -s "$PWD"/lib/base.py /usr/local/bin/base.py
ln -s "$PWD"/compressors/css.py /usr/local/bin/css_compress.py
ln -s "$PWD"/compressors/js.py /usr/local/bin/js_compress.py
ln -s "$PWD"/utley.py /usr/local/bin/utley.py

if [ -f ~/.bashrc ]; then
    echo "export PYTHONPATH=\$PYTHONPATH:/usr/local/bin/" >> ~/.bashrc
    . ~/.bashrc
else if [ -f ~/.bash_profile ]; then
    echo "export PYTHONPATH=\$PYTHONPATH:/usr/local/bin/" >> ~/.bash_profile
    . ~/.bash_profile
else
    export PYTHONPATH=$PYTHONPATH:/usr/local/bin/
    echo -e "The location of the Python3 build tools has been added to your PYTHONPATH for this terminal session.\nHowever, it's highly recommended to put the following in one of your shell's login scripts:\n\n\texport PYTHONPATH=\$PYTHONPATH:/usr/local/bin/"
fi

echo
echo "$(tput setaf 2)[INF]$(tput sgr0) Installation complete."

