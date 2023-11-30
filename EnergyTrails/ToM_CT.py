#!/usr/bin/env python3.10

import random
import traceback
from ColoredTrails import Game_ct
import pickle
from tqdm import tqdm
from datetime import datetime
import numpy as np 


CT_LEARNING_SPEED = 0.8 
CT_PRECISION = 0.00001

#ToM0 agent class 
class Tom0_model_ct:
    player_id = 0
    goal = 0
    learning_speed = CT_LEARNING_SPEED
    saved_beliefs = []
    saved_beliefs_count_positive = [] 
    saved_beliefs_count_total=[] 
    save_count = 0
    beliefs_count_positive = [[5 for i in range(33)] for j in range(33)]    
    beliefs_count_total = [[5 for i in range(33)] for j in range(33)] 
    belief_offer = []
    game_to_play = None
    saved_beliefs = None 

    def __init__(self, player_id):
        self.player_id = player_id

    # initialise player 
    def init(self, game, player_id=None):
        if player_id is not None:
            self.player_id = player_id
        self.belief_offer = []
        self.game_to_play = game
        for i in range(len(game.utilities[self.player_id])): 
            self.belief_offer.append(self.get_acceptance_rate(i))
        self.saved_beliefs = []
    
    # save beliefs 
    def save_beliefs(self):
        self.saved_beliefs.append(self.belief_offer.copy())

    # restore beliefs 
    def restore_beliefs(self):
        self.belief_offer = self.saved_beliefs.pop() 

    # observe an incoming offer and update beliefs accordingly 
    def observe(self, offer, is_accepted, player_id):
        pos = 0
        neg = 0
        diff = Game_ct.get_chip_difference(
            self.game_to_play.chip_sets[self.player_id],
            offer,
            self.game_to_play.bin_max,
        )
        for i in range(len(diff)):
            if diff[i] > 0:
                pos += diff[i]
            else:
                neg -= diff[i]
        self.beliefs_count_total[pos][neg] += 1
        if player_id != self.player_id:
            self.beliefs_count_positive[pos][neg] += 1
            self.increase_color_beliefs(offer)
        elif is_accepted:
            self.beliefs_count_positive[pos][neg] += 1
        else:
            self.decrease_color_beliefs(offer)

    # increase ebeliefs for a color 
    def increase_color_beliefs(self, new_my_chips):
        new_bins = Game_ct.convert_code(new_my_chips, self.game_to_play.bin_max)
        for i in range(len(self.belief_offer)):
            current_offer = Game_ct.convert_code(i, self.game_to_play.bin_max)
            for j in range(len(current_offer)):
                if current_offer[j] > new_bins[j]:
                    self.belief_offer[i] = (
                        1 - self.learning_speed
                    ) * self.belief_offer[i]

    # generalises for new boards, such that they can be compared through chip amount differences. This gives the ToM0 agent a better chance.
    def get_acceptance_rate(self, offer):
        pos = 0
        neg = 0
        diff = Game_ct.get_chip_difference(
            self.game_to_play.chip_sets[self.player_id],
            offer,
            self.game_to_play.bin_max,
        )
        for i in range(len(diff)):
            if diff[i] > 0:
                pos += diff[i]
            else:
                neg -= diff[i]
        return (
            self.beliefs_count_positive[pos][neg] / self.beliefs_count_total[pos][neg]
        )

    # get the value for an offer, which adjust the expected score with the beliefs the agent has about whether the offer wil be accepted    
    def get_expected_value(self, offer):
        return (
            self.belief_offer[offer]
            * self.get_offer(self.goal, offer)['max_utility']
        )
    
    # get the score for a particular offer 
    def get_offer(self, goal, offer):
        return next(item for item in self.game_to_play.utilities[goal] if item['offer_code'] == offer)
    
    def prepare_values(self):
        pass 


# general agent class 
class Agent_ct:
    learning_speed = CT_LEARNING_SPEED
    order = 0
    player_id = 0
    confidence_locked = False
    confidence = 1.0
    goal_beliefs = []
    saved_beliefs = [] # stores results from get_valid_offers 
    goal = 0
    last_accuracy = 0
    game_to_play = None
    saved_values = [] # temporary storage to keep the values when going through hypothetical situations 
    values = None # the active values that are stored from get_value
    all_offers = None # the active all offers stored from get_valid_offers
    saved_all_offers = [] # temporary storage to keep the values when going through hypothetical situations

    # initialise agent 
    def __init__(self, order, player_id, shortcut = False):
        self.order = order
        self.player_id = player_id
        self.skip_count = 0
        self.shortcut = shortcut
        
        # set which agents should use the reasoning shortcut 
        if self.order >= 2 or self.shortcut:
            self.shortcut = True
            
        if order > 0:
            self.opponent_model = Agent_ct(order - 1, 1 - player_id, self.shortcut)
            self.opponent_model.confidence_locked = True
            self.self_model = Agent_ct(order - 1, player_id, self.shortcut)
        else:
            self.opponent_model = Tom0_model_ct(player_id)
            self.self_model = None
        pass

    def init(self, game, player_id=None, shortcut = False):
        if player_id is not None:
            self.player_id = player_id
        self.game_to_play = game
        self.goal = game.goal_composition_code[self.player_id]
        self.all_offers = None
        self.saved_beliefs = []
        self.shortcut = shortcut
        self.shortcut_order = 2 
        random.seed(game.seed)

        if self.game_to_play.number_of_boards < 4:
            self.shortcut_order = 5
            self.shortcut = False 
        
        # set which agents should use the reasoning shortcut 
        if self.order >= self.shortcut_order or self.shortcut:
            self.shortcut = True
            
        if self.order > 0:
            self.opponent_model.init(game, 1 - self.player_id, self.shortcut)
            self.self_model.init(game, self.player_id, self.shortcut)
            self.goal_beliefs = [1.0 / len(game.utilities)] * len( 
                game.utilities
            )
        else:
            self.opponent_model.init(game, player_id)

    # save beliefs 
    def save_beliefs(self):
        if self.values is not None: 
            self.saved_values.append(self.values.copy())
        if self.all_offers is not None: 
            self.saved_all_offers.append(self.all_offers.copy())
        if self.order > 0:
            self.saved_beliefs.append(self.goal_beliefs.copy())
            self.self_model.save_beliefs()
        self.opponent_model.save_beliefs()

    # restore beliefs 
    def restore_beliefs(self):
        try:
            self.values = self.saved_values.pop()
        except:
            pass
        
        try:
            self.all_offers = self.saved_all_offers.pop()
        except:
            pass
        if self.order > 0:
            self.goal_beliefs = self.saved_beliefs.pop()
            self.self_model.restore_beliefs()
        self.opponent_model.restore_beliefs()

    # get the beliefs for a particular goal adjusted with the confidence 
    def get_goal_beliefs(self, goal): 
        if self.confidence_locked:
            return self.goal_beliefs[goal]
        if self.order > 0:
            return 1 / len(self.game_to_play.utilities)
        return self.confidence * self.goal_beliefs[goal] + (
            1 - self.confidence
        ) * self.self_model.get_goal_beliefs(goal)

    # inform goal
    def inform_goal(self): 
        self.goal = self.game_to_play.goal_compositions[self.player_id]
        if self.order > 0:
            for i in range(len(self.goal_beliefs)):
                self.goal_beliefs[i] = 0
            self.goal_beliefs[self.game_to_play.goal_compositions[1 - self.player_id]] = 1
            self.self_model.inform_goal()
            self.opponent_model.goal()
    
    # get the value of an offer based on the potential shared score that can be received 
    def get_opponent_value(self, offer):
        value = 0 
        for count, belief in enumerate(self.goal_beliefs):
            value += belief * self.opponent_model.get_offer(count, offer)['shared_score']
        return value 

    # get the value of an offer adjusted with the goal beliefs 
    def get_goal_value(self, offer_to_me):
        response = self.opponent_model.select_offer(
            self.game_to_play.flip_array[offer_to_me]
        )
        current_value = 0
        
        if self.game_to_play.point_sharing and self.order > 0: 
            if response == self.game_to_play.flip_array[offer_to_me]:
                # Partner accepts
                current_value += (
                    (self.get_offer(self.goal, offer_to_me)['max_utility'] + self.get_opponent_value(self.game_to_play.flip_array[offer_to_me]))- (self.get_offer(self.goal, self.game_to_play.chip_sets[self.player_id])['max_utility'] + self.get_opponent_value(self.game_to_play.chip_sets[1-self.player_id]))
                    - 1 
                )
            elif response != self.game_to_play.chip_sets[1 - self.player_id]:
                # Partner counters
                response = self.game_to_play.flip_array[response]
                current_value += max(
                    -1,
                    (self.get_offer(self.goal, offer_to_me)['max_utility'] + self.get_opponent_value(self.game_to_play.flip_array[offer_to_me]))- (self.get_offer(self.goal, self.game_to_play.chip_sets[self.player_id])['max_utility'] + self.get_opponent_value(self.game_to_play.chip_sets[1-self.player_id]))
                    - 2,  
                )
        else:
            if response == self.game_to_play.flip_array[offer_to_me]:
                # Partner accepts
                current_value += (
                    self.get_offer(self.goal, offer_to_me)['max_utility'] - self.get_offer(self.goal, self.game_to_play.chip_sets[self.player_id])['max_utility']
                    - 1
                )
            elif response != self.game_to_play.chip_sets[1 - self.player_id]:
                # Partner counters
                response = self.game_to_play.flip_array[response]
                current_value += max(
                    -1,
                    self.get_offer(self.goal, response)['max_utility'] - self.get_offer(self.goal, self.game_to_play.chip_sets[self.player_id])['max_utility']
                    - 2,
                )
                
        return current_value

    # set your own goal 
    def set_goal(self, goal):
        self.goal = goal
        if self.order > 0:
            self.self_model.set_goal(goal)
        else:
            self.opponent_model.goal = goal

    # get the score of a particular offer 
    def get_score(self, offer):
        return next(item for item in self.game_to_play.utilities[self.goal] if item['offer_code'] == offer)['max_utility']

    # get the value of an offer by simulating the offer selection procedure of the trading partner 
    def get_value(self, offer_to_me):
        if (
            self.get_offer(self.goal, offer_to_me)['max_utility'] <= self.get_offer(self.goal, self.game_to_play.chip_sets[self.player_id])['max_utility']
        ):
            self.skip_count +=1 
            return -1

        # only consider offers that haven't been offered before 
        if offer_to_me in self.game_to_play.offer_history[self.player_id]:
            return 0 
        
        if self.order == 0:
            return self.opponent_model.get_expected_value(offer_to_me)

        current_value = 0
        if self.confidence_locked or self.confidence > 0:
            self.opponent_model.save_beliefs()
            self.opponent_model.receive_offer(self.game_to_play.flip_array[offer_to_me], True)
            for l in range(len(self.goal_beliefs)):
                if self.goal_beliefs[l] > 0:
                    self.opponent_model.set_goal(l)
                    current_value += self.goal_beliefs[l] * self.get_goal_value(
                        offer_to_me
                    )
            self.opponent_model.restore_beliefs()
            if self.confidence_locked or self.confidence >= 1:
                return current_value
        return self.confidence * current_value + (
            1 - self.confidence
        ) * self.self_model.get_value(offer_to_me)

    # observe a played offer 
    def observe(self, offer, is_accepted, player_id):
        self.values = None
        self.all_offers = None 
        self.opponent_model.observe(offer, is_accepted, player_id)
        self.opponent_model.values = None
        self.opponent_model.all_offers = None 
        if self.order > 0:
            self.self_model.values = None
            self.self_model.all_offers = None
            self.self_model.observe(offer, is_accepted, player_id)
            if player_id != self.player_id and not self.confidence_locked:
                self.confidence = (
                    1 - self.learning_speed
                ) * self.confidence + self.learning_speed * (
                    max(0, self.opponent_model.get_value(offer)) + 1.0
                ) / (
                    max(0, self.opponent_model.get_best_value()) + 1.0
                )

    # select an offer 
    def select_offer(self, offer_to_me):
        all_offers = self.get_valid_offers(offer_to_me)
        return all_offers[random.randrange(len(all_offers))]

    # the full offer procedure, which calls on all steps that are taken when it's an agent's turn 
    def make_offer(self, offer_to_me=None):
        if offer_to_me == None:
            offer_to_me = self.game_to_play.chip_sets[self.player_id]
        self.receive_offer(offer_to_me)
        choice = self.select_offer(offer_to_me) 
        self.game_to_play.offer_history[self.player_id].append(choice) # add choice to offer history 
        self.send_offer(choice)
        return choice

    # go through all values and select the best one 
    def get_best_value(self):
        if self.values is not None and max(self.values) > 0:
            return max(self.values)

        best_value = 0
        pbar = tqdm(range(len(self.game_to_play.utilities[0])), leave=False, disable=False)
        pbar.set_description("Calculating best value")
        self.values = []
        for i in pbar: 
            value = self.get_value(i)
            self.values.append(value)
            best_value = max(best_value, value)
        return best_value
    
    # make it look though the dictionary to actually find the offer
    def get_offer(self, goal, offer):
        return self.game_to_play.utilities[goal][offer]

    # go through all valid offers and select the best one based on its value 
    def get_valid_offers(self, offer_to_me):
        all_offers = [self.game_to_play.chip_sets[self.player_id]]
        best_value = 0
        
        if self.values is None or self.all_offers is None:
            self.values = []
            self.all_offers = []
            pbar = tqdm(range(len(self.game_to_play.utilities[0])), leave=False, disable=False)
            pbar.set_description("SAVE valid offers for order " + str(self.order))
            for i in pbar:
                value = self.get_value(i)
                self.values.append(value)
                if value > best_value - CT_PRECISION:
                    if value > best_value + CT_PRECISION:
                        all_offers = []
                        best_value = value
                    all_offers.append(i)
            self.all_offers = all_offers
            self.best_value = best_value
        else:
            all_offers = self.all_offers
            best_value = self.best_value
            
                
        if (
            offer_to_me >= 0
            and self.get_offer(self.goal, offer_to_me)['max_utility'] - 
            self.get_offer(self.goal, self.game_to_play.chip_sets[self.player_id])['max_utility']
            > best_value - CT_PRECISION
        ):
            # Current offer on the table is at least as good as the expected value of any counteroffer
            all_offers = [offer_to_me]
            best_value = (self.get_offer(self.goal, offer_to_me)['max_utility'] - 
            self.get_offer(self.goal, self.game_to_play.chip_sets[self.player_id])['max_utility']
            )
        if (best_value < CT_PRECISION):
            # There are no good offers, agent withdraws from negotiation
            all_offers = [self.game_to_play.chip_sets[self.player_id]]
        return all_offers

    # update your goal beliefs based on the offer that has been received
    def update_goal_beliefs(self, offer_received):
        offer_to_other = self.game_to_play.flip_array[offer_received]
        accuracy = 0
        
        for l in range(len(self.goal_beliefs)): 
            self.opponent_model.set_goal(l)
            if not self.shortcut:
                self.opponent_model.values = None 
                self.opponent_model.all_offers = None 
            if (self.get_offer(l, offer_to_other)['max_utility'] <= self.get_offer(l, self.game_to_play.chip_sets[1-self.player_id])['max_utility']
            ):
                # If the goal of the other is l, the offer that has been made would not increase the score of the other
                # The agent considers it irrational to make such an offer, so it concludes the goal of the other is not l
                self.goal_beliefs[l] = 0
            else:
                self.goal_beliefs[l] *= max(
                    0,
                    (self.opponent_model.get_value(offer_to_other) + 1)
                    / (self.opponent_model.get_best_value() + 1),
                )
                accuracy += self.goal_beliefs[l]
            
        if accuracy > 0:
            inv_sum_beliefs = 1.0 / accuracy
            for l in range(len(self.goal_beliefs)):
                self.goal_beliefs[l] *= inv_sum_beliefs
        else:
            # None of the goals seem to match at all, reset the goal beliefs
            self.goal_beliefs = [
                1.0 / len(self.game_to_play.utilities)
            ] * len(self.game_to_play.utilities)
        if not self.confidence_locked:
            self.confidence = (
                1 - self.learning_speed
            ) * self.confidence + self.learning_speed * accuracy
        
    # prepare values 
    def prepare_values(self):
        self.values = []
        pbar = tqdm(range(len(self.game_to_play.utilities[0])), leave=False, disable=False)
        pbar.set_description("Prepare values")
        for i in pbar:
            self.values.append(self.get_value(i))

    # receive an offer and call all actions necessary to process the received offer 
    def receive_offer(self, offer_to_me, from_get_value = False):
        if offer_to_me >= 0:
            if self.order > 0:
                if not from_get_value or not self.shortcut: # if we did not come from get_value OR if the order of an agent is lower than two, we're resetting the beliefs
                    self.update_goal_beliefs(offer_to_me)
                    self.values = None 
                    self.all_offers = None 
                self.self_model.receive_offer(offer_to_me)
                self.opponent_model.send_offer(
                    self.game_to_play.flip_array[offer_to_me]
                )
            else:
                # Receiving an offer is like observing an offer being accepted
                self.opponent_model.observe(offer_to_me, True, 1 - self.player_id)
                if not from_get_value or not self.shortcut:
                    self.values = None
                    self.all_offers = None
                self.opponent_model.values = None 
                self.opponent_model.all_offers_saved = None

    # send a chosen offer to the simulated internal agents 
    def send_offer(self, offer_to_me):
        if self.order > 0:
            self.self_model.send_offer(offer_to_me)
            self.opponent_model.receive_offer(self.game_to_play.flip_array[offer_to_me])
        else:
            # Sending an offer is like observing an offer being rejected (the game only continues if the offer is rejected)
            self.opponent_model.observe(offer_to_me, False, 1 - self.player_id)
