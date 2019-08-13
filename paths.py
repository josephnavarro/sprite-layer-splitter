#! usr/bin/env python3
"""
Path utility functions.
"""
import os


def fix_paths(path):
    """
    Ensures safety of output directories.
    """
    path = os.path.normpath(path)
    os.makedirs(path, exist_ok=True)
    return path
