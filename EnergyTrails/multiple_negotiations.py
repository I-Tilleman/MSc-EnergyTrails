#!/usr/bin/env python3.10

from ColoredTrails import Game_ct
from ToM_CT import *
from tqdm import tqdm
import pickle
from matplotlib import pyplot as plt
import logging
import sys
from datetime import datetime 
import os 
import errno
import csv

def log(agents, game, round):
    pass

# runs multiple negotiations between two agents

def multiple_negotiations(agents: str, backup_freq = 25, negotiations = 1000, rounds = 50, boards = 4, point_sharing = 1):
    
    total = 0
    withdrawn = 0
    accepted = []
    score_gain = [] # the score they gained after negotiating
    score_diff = [] # diff in final score between the players
    avg_gains = []
    avg_diff = []
    negotiation_rounds = [] # the nr. of negotiation rounds used in each negotiation
    log = []
    utilities = [] # this one might become really big
    beliefs_a = []
    beliefs_b = []
    goal_a = []
    goal_b = []
    
    
    backup = 0 # counter for making backups 
    
    test_agent = [Agent_ct(int(agents[0]),0), Agent_ct(int(agents[1]),1)]
    
    for i in tqdm(range(int(negotiations))):
        playera_start = 0
        playerb_start = 0 
        neg_beliefs_a = []
        neg_beliefs_b = []
        
        total +=1
        backup +=1 
        
        test_game = Game_ct(int(boards), int(point_sharing))
        test_game.init(location_goal = False)
        
        test_agent[0].init(test_game)
        test_agent[1].init(test_game)
        
        log.append({'offers_a': [], 'offer_codes_a': [], 'scores_a': [], 'beliefs_a': [], 'goal_a': [], 'offers_b': [], 'offer_codes_b': [], 'scores_b': [], 'beliefs_b': [], 'goal_b': []})
        
        current_player = 0
        previous_offer = test_game.flip_array[test_game.chip_sets[current_player]]
        offer_made = test_agent[current_player].make_offer()
        max_rounds = int(rounds)
        rounds_count = 0
        
        playera_start = test_agent[0].get_score(test_game.chip_sets[0])
        playerb_start = test_agent[1].get_score(test_game.chip_sets[1])
        
        # log
        log[i]['offer_codes_a'].append(test_game.chip_sets[0])
        log[i]['offer_codes_b'].append(test_game.chip_sets[1])
        log[i]['offers_a'].append(Game_ct.convert_code(test_game.chip_sets[0], test_game.bin_max))
        log[i]['offers_b'].append(Game_ct.convert_code(test_game.chip_sets[1], test_game.bin_max))
        log[i]['scores_a'].append(playera_start)
        log[i]['scores_b'].append(playerb_start)
        log[i]['goal_a'].append(test_agent[0].goal)
        log[i]['goal_b'].append(test_agent[1].goal)
        goal_a.append(test_agent[0].goal)
        goal_b.append(test_agent[1].goal)

        
        while (max_rounds > 0 and offer_made != test_game.chip_sets[current_player] and offer_made != test_game.flip_array[previous_offer]):
            current_player = 1 - current_player
            previous_offer = offer_made
            offer_made = test_agent[current_player].make_offer(test_game.flip_array[previous_offer])
            max_rounds -= 1
            rounds_count +=1
            
            #### LOG ####
            
            if (current_player == 0):
                score_a = test_agent[0].get_score(offer_made)
                score_b = test_agent[1].get_score(test_game.flip_array[offer_made])
                log[i]['offer_codes_a'].append(offer_made)
                log[i]['offer_codes_b'].append(test_game.flip_array[offer_made])
                log[i]['offers_a'].append(Game_ct.convert_code(offer_made, test_game.bin_max))
                log[i]['offers_b'].append(Game_ct.convert_code(test_game.flip_array[offer_made], test_game.bin_max))
            else:
                score_a = test_agent[0].get_score(test_game.flip_array[offer_made])
                score_b = test_agent[1].get_score(offer_made)
                log[i]['offer_codes_a'].append(test_game.flip_array[offer_made])
                log[i]['offer_codes_b'].append(offer_made)
                log[i]['offers_a'].append(Game_ct.convert_code(test_game.flip_array[offer_made], test_game.bin_max))
                log[i]['offers_b'].append(Game_ct.convert_code(offer_made, test_game.bin_max))
            log[i]['scores_a'].append(score_a)
            log[i]['scores_b'].append(score_b)
            if int(agents[0]) == 0:
                log[i]['beliefs_a'].append(None)
                neg_beliefs_a.append(None)
            else: 
                log[i]['beliefs_a'].append(test_agent[0].goal_beliefs) # maybe eventually create a function that returns this
                neg_beliefs_a.append(test_agent[0].goal_beliefs)
            if int(agents[1]) == 0:
                log[i]['beliefs_b'].append(None)
                neg_beliefs_b.append(None)
            else:
                log[i]['beliefs_b'].append(test_agent[1].goal_beliefs)
                neg_beliefs_b.append(test_agent[1].goal_beliefs)

        if (offer_made == test_game.chip_sets[current_player]):
            withdrawn += 1
            score_gain.append(0) # we are currently considering this to be a score gain of 0, but that is excluding the points lost for each additional negotiation round 
            accepted.append(0)
            score_diff.append(0)
        elif (offer_made == test_game.flip_array[previous_offer]):
            score_gain.append(((score_a-playera_start) + (score_b-playerb_start))/2)
            score_diff.append(abs(score_a-score_b))
            accepted.append(1)
        else:
            score_gain.append(0)
            accepted.append(0)
            score_diff.append(0)
            print("Timeout")
        
        avg_gains.append(sum(score_gain)/total)
        avg_diff.append(sum(score_diff)/total)
        negotiation_rounds.append(rounds_count)
        beliefs_a.append(neg_beliefs_a)
        beliefs_b.append(neg_beliefs_b)
        del test_game
        
        # write csv logs
        with open('tests/'+today.strftime('%Y%m%d')+ '/log-' + sys.argv[1] + '.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([i, list(log[i]['offers_a']), log[i]['offer_codes_a'], log[i]['scores_a'], log[i]['beliefs_a'], log[i]['goal_a'], log[i]['offers_b'], log[i]['offer_codes_b'], log[i]['scores_b'], log[i]['beliefs_b'], log[i]['goal_b']])
        
        if backup == int(backup_freq): 
            results_temp = {'total': total, 'accepted': accepted, 'scores': score_gain, 'avg_gains': avg_gains, 'avg_diff': avg_diff, 'score_diff': score_diff, 'negotiation_rounds':negotiation_rounds, 'log': log, 'utilities': utilities, 'beliefs_a': beliefs_a, 'beliefs_b':beliefs_b, 'goal_a': goal_a, 'goal_b': goal_b}
            with open('tests/'+today.strftime('%Y%m%d')+ '/outfile-'+ agents + '-temp', 'wb') as fp:
                pickle.dump(results_temp, fp)
            backup = 0
            
    print("----END----")
    
    if (int(agents[0]) > 0 and int(agents[1]) > 0) or int(negotiations) < 200:
        results = {'total': total, 'accepted': accepted, 'scores': score_gain, 'avg_gains': avg_gains, 'avg_diff': avg_diff, 'score_diff': score_diff, 'negotiation_rounds':negotiation_rounds, 'log': log, 'utilities': utilities, 'beliefs_a': beliefs_a, 'beliefs_b':beliefs_b, 'goal_a': goal_a, 'goal_b': goal_b}
    else:
        results = {'total': total-200, 'accepted': accepted[200:], 'scores': score_gain[200:], 'avg_gains': avg_gains[200:], 'avg_diff': avg_diff[200:], 'score_diff': score_diff[200:], 'negotiation_rounds':negotiation_rounds[200:], 'log': log[200:], 'utilities': utilities[200:],  'beliefs_a': beliefs_a[200:], 'beliefs_b':beliefs_b[200:], 'goal_a': goal_a[200:], 'goal_b': goal_b[200:]}
    
    with open('tests/'+today.strftime('%Y%m%d')+ '/outfile-' + agents, 'wb') as fp:
        pickle.dump(results, fp)
        
if __name__ == "__main__":

    today = datetime.now()
    header = ['negotiation_nr', 'offers_a', 'offer_codes_a', 'scores_a', 'beliefs_a', 'goal_a', 'offers_b', 'offer_codes_b', 'scores_b', 'beliefs_b', 'goal_b']

    try:
        os.mkdir("tests/"+today.strftime('%Y%m%d'))
    except OSError as e: 
        if e.errno != errno.EEXIST:
            raise
        
    with open('tests/'+today.strftime('%Y%m%d')+ '/log-' + sys.argv[1] + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    multiple_negotiations(*sys.argv[1:])
