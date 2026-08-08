#!/bin/sh
# Build the exact cache-optimized C scan kernel into a shared library.
# Output suffix matches what phase1/scankernel.py loads per platform.
set -e
cd "$(dirname "$0")/../phase1"
case "$(uname -s)" in
  Darwin) OUT=_scankernel.dylib ;;
  *)      OUT=_scankernel.so ;;
esac
cc -O2 -shared -fPIC -o "$OUT" _scankernel.c -lm
shasum -a 256 _scankernel.c "$OUT" 2>/dev/null || sha256sum _scankernel.c "$OUT"
