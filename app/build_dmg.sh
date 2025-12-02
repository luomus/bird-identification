#!/bin/sh
mkdir -p dist/dmg
test -f dist/dmg/* && rm -r dist/dmg/*
cp -r dist/birdIdentifier.app dist/dmg
test -f dist/birdIdentifier-*.dmg && rm dist/birdIdentifier-*.dmg
# add volicon
# add icon-size
# add icon
create-dmg \
  --volname "Bird Identifier" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --hide-extension "birdIdentifier.app" \
  --app-drop-link 425 120 \
  "dist/birdIdentifier-{{ version }}.dmg" \
  "dist/dmg/"