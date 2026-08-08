#!/bin/sh
# Build the exact C scan kernel (phase1/_scankernel.c -> _scankernel.dylib).
set -e
cd "$(dirname "$0")/../phase1"
cc -O2 -shared -fPIC -o _scankernel.dylib _scankernel.c
shasum -a 256 _scankernel.c _scankernel.dylib
