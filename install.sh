#!/bin/bash -eu

function install()
{
    p="$1"
    if dpkg -l "$p" >/dev/null 2>&1; then
        echo "$p found"
    else
        echo "$p not found, installing"
        sudo apt-get install "$p"
    fi
}

install python-dev
install python-numpy
install libfreetype6-dev
install python-matplotlib
pip install -r requirements.txt

