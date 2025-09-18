"""Build a standalone executable with PyInstaller."""
from __future__ import annotations

import os
import sys

from PyInstaller.__main__ import run

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ROOT)

add_data_sep = ';' if os.name == 'nt' else ':'
assets_arg = f"assets{add_data_sep}assets"

args = [
    '--name', 'FluppyBird',
    '--onefile',
    '--clean',
    f'--add-data={assets_arg}',
    os.path.join(PROJECT_ROOT, 'game.py'),
]

print('Running PyInstaller with args:', args)
run(args)
