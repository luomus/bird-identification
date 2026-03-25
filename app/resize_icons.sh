#!/bin/bash

# Usage: ./resize_icons.sh path/to/original.png path/to/dest_dir

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 path/to/original.png path/to/dest_dir"
    exit 1
fi

SRC="$1"
DEST_DIR="$2"

mkdir -p "$DEST_DIR"

for SIZE in 16 32 48 256; do
    convert "$SRC" -resize ${SIZE}x${SIZE} "$DEST_DIR/sirkku-logo${SIZE}x${SIZE}.png"
done

echo "Icons created in $DEST_DIR:"
ls -1 "$DEST_DIR"/sirkku-logo*.png
