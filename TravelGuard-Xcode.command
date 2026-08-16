#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ -d "$ROOT/ios/TravelGuard.xcworkspace" ]; then
  open "$ROOT/ios/TravelGuard.xcworkspace"
else
  open "$ROOT/ios/TravelGuard.xcodeproj"
fi
