"""Remove numba on-disk caches so every experiment run compiles from the current source.

Numba's cache invalidation does not track changes in njit functions imported from other modules,
so stale cross-module caches are possible; clearing before each run removes that risk.
"""
import glob
import os


def clear_numba_cache(root=os.path.dirname(__file__)):
    n = 0
    for pat in ("**/*.nbi", "**/*.nbc"):
        for f in glob.glob(os.path.join(root, pat), recursive=True):
            os.remove(f)
            n += 1
    return n
