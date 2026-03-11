#!/bin/sh
mkdir -p dist/dmg
[ -d dist/dmg ] && rm -rf dist/dmg/*
mv dist/sirkku.app dist/dmg/
test -f dist/sirkku-*.dmg && rm dist/sirkku-*.dmg
create-dmg \
  --volname "Sirkku" \
  --volicon "icons/sirkku-logo.icns" \
  --icon-size 128 \
  --icon "sirkku.app" 175 120 \
  --window-pos 200 120 \
  --window-size 600 300 \
  --hide-extension "sirkku.app" \
  --app-drop-link 425 120 \
  --format ULMO \
  "dist/sirkku-{{ version }}.dmg" \
  "dist/dmg/"
