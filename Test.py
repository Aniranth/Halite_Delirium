#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction
from hlt.positionals import Position

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging



"""<<<User Written Functions>>>"""

def safest_path_to_base(yard, ship, map): #Rewrite this for better pathfinding for now I will use theirs
    direction = map.naive_navigate(ship, yard.position)
    return direction
 
""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
#Do preprocessing here
back_to_base = []
game.ready("DeliriumBot-bak")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    players = game.players
    logging.info("Players: {}".format(players))
    opponent = players.get(0)
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    for ship in me.get_ships():
        command_queue.append(ship.move(game_map.naive_navigate(ship, opponent.shipyard.position)))

    if me.halite_amount > constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())
    game.end_turn(command_queue)
