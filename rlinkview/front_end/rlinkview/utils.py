import os

def which(path, exefile):
    """Locate a file in a PATH """
    for p in (path or "").split(':'):
        next = os.path.join(p, exefile)
        if os.path.exists(next):
            return next

    return ""

def opj(path):
    """Convert paths to the platform-specific separator"""
    st = apply(os.path.join, tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        st = '/' + st
    return st

# vim: ts=4:sw=4:et:sts=4:ai:tw=80
