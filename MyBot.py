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
save_me = False
game.ready("DeliriumBot")

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
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    spaces_around_base = me.shipyard.position.get_surrounding_cardinals()
    occupied_space_around_base = [x for x in spaces_around_base if game_map[x].is_occupied]
    if game.turn_number < constants.MAX_TURNS - 35 and not save_me and game_map[me.shipyard.position].is_occupied and (not me.has_ship(game_map[me.shipyard.position].ship.id) or len(occupied_space_around_base) == 4):
        save_me = True    

    for ship in me.get_ships():
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.


        if save_me and game_map.calculate_distance(ship.position, me.shipyard.position) == 1:
            command_queue.append(ship.move(game_map.get_unsafe_moves(ship.position, me.shipyard.position)[0]))
            save_me = False
        elif ship.halite_amount < 950 and not ship.id in back_to_base:                 
            #Here we want to navigate to a Halite surplus
            move_options = ship.position.get_surrounding_cardinals()
            greatest_safe_move = Position(-1,-1)
            greatest_halite = 0
            for option in move_options:
                if ship.position == me.shipyard.position and not game_map[option].is_occupied or game_map[option].halite_amount >= greatest_halite and not game_map[option].is_occupied and game_map[ship.position].halite_amount < game_map[option].halite_amount:
                    greatest_halite = game_map[option].halite_amount #We dont check if this space could become occupied which leads to collisions
                    greatest_safe_move = option
            if greatest_safe_move == Position(-1,-1) or game_map[ship.position].halite_amount > 100:
                command_queue.append(ship.stay_still())
            else:
                command_queue.append(ship.move(game_map.naive_navigate(ship, greatest_safe_move)))
        else:
            if game_map.calculate_distance(ship.position, me.shipyard.position) != 1 or game.turn_number < constants.MAX_TURNS - 35:
                command_queue.append(ship.move(safest_path_to_base(me.shipyard, ship, game_map)))
            elif game_map.calculate_distance(ship.position, me.shipyard.position) == 1:
                if ship.position != me.shipyard.position:
                    command_queue.append(ship.move(game_map.get_unsafe_moves(ship.position, me.shipyard.position)[0]))
            if not ship.id in back_to_base:
                back_to_base.append(ship.id)
            elif ship.id in back_to_base and ship.position == me.shipyard.position:
                back_to_base.remove(ship.id)

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    if game.turn_number == constants.MAX_TURNS - 35:
        for ship in me.get_ships():
            back_to_base.append(ship.id)
    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
