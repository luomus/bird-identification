#!/bin/sh
mkdir -p dist/dmg
[ -d dist/dmg ] && rm -rf dist/dmg/*
mv dist/Sirkku.app dist/dmg/
test -f dist/sirkku-*.dmg && rm dist/sirkku-*.dmg
create-dmg \
  --volname "Sirkku" \
  --volicon "icons/logo/sirkku-logo.icns" \
  --icon-size 128 \
  --icon "Sirkku.app" 175 120 \
  --window-pos 200 120 \
  --window-size 600 300 \
  --hide-extension "Sirkku.app" \
  --app-drop-link 425 120 \
  --format ULMO \
  --codesign "$MACOS_CERTIFICATE_ID" \
  --notarize "$NOTARY_PROFILE" \
  "dist/sirkku-{{ version }}-{{ architecture }}.dmg" \
  "dist/dmg/"
