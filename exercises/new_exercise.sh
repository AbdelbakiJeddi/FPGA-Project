#!/usr/bin/env bash
set -e
[ $# -eq 2 ] || { echo "Usage: ./new_exercise.sh <folder_name> <tb_entity_name>"; exit 1; }
mkdir -p "$1"
printf 'TOP = %s\ninclude ../common/Makefile.inc\n' "$2" > "$1/Makefile"
echo "Created exercise directory: $1"
echo "Add .vhd files inside, then run: cd $1 && make sim && make wave"
