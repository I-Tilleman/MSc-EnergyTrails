#!/usr/bin/env python3.10

from ColoredTrails import Game_ct
from ToM_CT import *
import time 

# this is used to run a single negotiation between agents

def test():
    test_game = Game_ct()
    test_game.init(location_goal = False)        # Generate a random setting
    test_game.print_boards()
    
    print("0:", test_game.goal_compositions[0], test_game.chips_for_completion[0], "-", Game_ct.convert_code(test_game.chip_sets[0], test_game.bin_max))
    print("1:", test_game.goal_compositions[1], test_game.chips_for_completion[1], "-", Game_ct.convert_code(test_game.chip_sets[1], test_game.bin_max))

    test_agent = [Agent_ct(0,0), Agent_ct(2,1)]
                            # Create theory of mind agents with ids 0 and 1, the first parameter sets the order of theory of mind used by the agents
    test_agent[0].init(test_game)
    test_agent[1].init(test_game)
                            # Initialize the agent to play test_game

    current_player = 0
    previous_offer = test_game.flip_array[test_game.chip_sets[current_player]]
    offer_made = test_agent[current_player].make_offer()
    max_rounds = 50
    print("Offer by:", current_player,"\n\t", current_player, "gets:", Game_ct.convert_code(offer_made, test_game.bin_max),"\n\t", 1 - current_player,"gets:",Game_ct.convert_code(test_game.flip_array[offer_made], test_game.bin_max))

    while (max_rounds > 0 and offer_made != test_game.chip_sets[current_player] and offer_made != test_game.flip_array[previous_offer]):
        current_player = 1 - current_player
        previous_offer = offer_made
        offer_made = test_agent[current_player].make_offer(test_game.flip_array[previous_offer])
        print("Offer by:", current_player,"\n\t", current_player, "gets:", Game_ct.convert_code(offer_made, test_game.bin_max),"\n\t", 1 - current_player,"gets:",Game_ct.convert_code(test_game.flip_array[offer_made], test_game.bin_max))
        max_rounds -= 1
    if (offer_made == test_game.chip_sets[current_player]):
      print("Withdrawn")
    elif (offer_made == test_game.flip_array[previous_offer]):
      print("Accepted")
      if (current_player == 0):
        print(offer_made)
        print("Final scores:\n0:", test_agent[0].get_score(offer_made),"\n1:",test_agent[1].get_score(test_game.flip_array[offer_made]))
      else:
        print(offer_made)
        print("Final scores:\n0:", test_agent[0].get_score(test_game.flip_array[offer_made]),"\n1:",test_agent[1].get_score(offer_made))
    else:
      print("Timeout")

start_time = time.time()
test()
print("--- %s seconds ---" % (time.time() - start_time))
