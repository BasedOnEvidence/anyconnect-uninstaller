import os
import sys


def get_resource_path(current_relative_path, target_relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        curernt_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '.', target_relative_path)
        )
        base_path = os.environ.get("_MEIPASS2", curernt_path)
    return os.path.join(base_path, current_relative_path)


def get_paths_to_delete(filename):
    if ('.txt') in filename:
        folder = 'data'
    elif ('.exe') in filename:
        folder = 'executable'
    else:
        folder = '.'
    with open(get_resource_path(filename, folder), "r") as path_file:
        paths_list = path_file.read().splitlines()
    return paths_list
