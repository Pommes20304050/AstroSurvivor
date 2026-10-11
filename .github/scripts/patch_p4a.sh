#!/usr/bin/env bash
# Clones p4a to ./python-for-android (used via p4a.source_dir in buildozer.spec)
# and monkey-patches python3 recipe to disable _lzma + _uuid optional modules.
# NDK sysroot has neither lzma.h nor libuuid; a pygame app does not need them.
set -euo pipefail

P4A_DIR=./python-for-android

if [ ! -d "$P4A_DIR" ]; then
  git clone --depth 1 --branch v2024.01.21 \
    https://github.com/kivy/python-for-android.git "$P4A_DIR"
fi

RECIPE="$P4A_DIR/pythonforandroid/recipes/python3/__init__.py"

if grep -q "astrosurvivor disabled modules" "$RECIPE"; then
  echo "python3 recipe already patched"
  exit 0
fi

cat >> "$RECIPE" <<'PYEOF'

# astrosurvivor disabled modules patch
import os as _as_os

_as_orig_prebuild_arch = Python3Recipe.prebuild_arch


def _as_patched_prebuild_arch(self, arch):
    _as_orig_prebuild_arch(self, arch)
    src = self.get_build_dir(arch.arch)
    setup_local = _as_os.path.join(src, 'Modules', 'Setup.local')
    with open(setup_local, 'a') as _f:
        _f.write('\n*disabled*\n_lzma\n_uuid\n')
    print('[astrosurvivor] disabled _lzma and _uuid via Setup.local')


Python3Recipe.prebuild_arch = _as_patched_prebuild_arch
PYEOF

echo "Patched python3 recipe. Tail:"
tail -20 "$RECIPE"
