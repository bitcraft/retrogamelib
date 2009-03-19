import sys
sys.path.insert(0, "..")

from nesgamelib import display
from nesgamelib.constants import *
import menu

def main():
    display.init(3.0, "BubbMan", res=GBRES)
    menu.run_menu()
