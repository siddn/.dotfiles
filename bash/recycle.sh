#! /usr/bin/bash

recycle_dir=$HOME/Recycle

show_help() {
    echo "Usage:recycle [OPTION] [DIR]"
    echo
    echo "Sends the file to a folder located at $HOME/Recycle"
    echo
    echo "Options (Uses all the same options as mv):"
    echo
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

if [ ! -d $recycle_dir ]; then
  mkdir -p $recycle_dir
fi

mv "$@" $recycle_dir
