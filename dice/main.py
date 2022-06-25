import os
import sys

from dice.lib.gameinterface import GameInterface


def main():
    os.system("")
    # check passed in arguments
    dc = 5
    ds = 6
    u = False
    so = True
    debug = False
    for arg in sys.argv[1:]:
        # dice count
        if arg.startswith("c="):
            dc = int(arg[2:])
        # dice size
        if arg.startswith("d="):
            ds = int(arg[2:])
        # no unicode
        if arg == "-u":
            u = True
        # debug
        if arg == "-d":
            debug = True
        # show odds
        if arg == "-no":
            so = False

    # Create a game and an interface
    game_interface = GameInterface(debug)
    game_interface.setup(dc, ds, u, so)
    game_interface.print()

    while not game_interface.game_over:
        game_interface.next()

    exit()


if __name__ == "__main__":
    main()
