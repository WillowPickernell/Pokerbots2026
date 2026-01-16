'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, DiscardAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        self.has_pair = False
        self.suit_match = False
        self.connected = False
        self.hand_strength = 1

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        # the total number of seconds your bot has left to play this game
        game_clock = game_state.game_clock
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0,2,3,4,5,6 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        # opponent's cards or [] if not revealed
        opp_cards = previous_state.hands[1-active]
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        street = round_state.street
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.board  # the board cards
        # the number of chips you have contributed to the pot this round of betting
        my_pip = round_state.pips[active]
        # the number of chips your opponent has contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]
        # the number of chips you have remaining
        my_stack = round_state.stacks[active]
        # the number of chips your opponent has remaining
        opp_stack = round_state.stacks[1-active]
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        # the number of chips you have contributed to the pot
        my_contribution = STARTING_STACK - my_stack
        # the number of chips your opponent has contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack

        # Only use DiscardAction if it's in legal_actions (which already checks street)
        # legal_actions() returns DiscardAction only when street is 2 or 3

        #Want to aim for a pair, as that gives the highest chance of a better hand
        translate = {
                "A": 14,
                "J": 11,
                "Q": 12,
                "K": 13,
                "T": 10
            }
        
        if DiscardAction in legal_actions:
            ranks = []
            suits = []
            min_rank = 20
            min_card = None
            for card, index in enumerate(my_cards):
                value = 0
                if not card[0].isdigit():
                    value = translate[card[0]]
                else:
                    value = int(card[0])

                if value < min_rank:
                    min_rank = value
                    min_card = index
                
                ranks.append(card[0])
                suits.append(card[1])

            for card_index in range(2):

                if ranks[card_index] == ranks[card_index+1]:
                    
                    self.has_pair = True
                    return DiscardAction(-2*card_index + 2)
                
            if ranks[0] == ranks[2]:

                self.has_pair = True
                return DiscardAction(1)
            
            for card_index in range(2):

                if suits[card_index] == suits[card_index+1]:

                    return DiscardAction(-2*card_index + 2)
                
            if suits[0] == suits[2]:
                return DiscardAction(1)
            
            return DiscardAction(min_card)
            
        if RaiseAction in legal_actions:
            # the smallest and largest numbers of chips for a legal bet/raise

            if len(board_cards) <= 3:
                return RaiseAction(min_raise)
            
            else:
                min_raise, max_raise = round_state.raise_bounds()
                #min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
                #max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
                board_rank_match = 0
                board_suit_match = 0

                for board_card in board_cards:

                    for card in my_cards:

                        if board_card[0] == card[0]:
                            board_rank_match += 1

                        if board_card[1] == card[1]:
                            board_suit_match += 1

                if self.has_pair:

                    #If we have 4 of a kind, max raise
                    if board_rank_match >= 4:
                        self.hand_strength = 5
                        return RaiseAction(max_raise)
                    
                    #Three of a kind, average between min and max
                    elif board_rank_match >= 2:
                        self.hand_strength = 3
                        return RaiseAction(min_raise + (max_raise - min_raise)//2)
                    
                    else:
                        pass
                    
                if self.suit_match:

                    #4 same suit cards and 2 left for the board -> max raise
                    if board_suit_match >= 4 and len(board_cards) == 4:
                        self.hand_strength = 4
                        return RaiseAction(max_raise)
                    
                    #4 same suit cards and 1 left for the board -> average between min and max
                    elif board_suit_match >= 4 and len(board_cards) == 5:
                        self.hand_strength = 3
                        return RaiseAction(min_raise + (max_raise - min_raise)//2)
                    
                    #Only 3 same suit cards and 2 left for the board, 5% chance to raise
                    elif board_suit_match >= 2 and len(board_cards) == 4:

                        self.hand_strength = 2
                        raise_check = random.random()

                        if raise_check > 0.95:
                            return RaiseAction(min_raise)
                        pass

        if CheckAction in legal_actions:  # check-call
            return CheckAction()
        
        if CallAction in legal_actions:

            hand_check = random.randint(0, 5)
            if self.hand_strength < hand_check:
                return FoldAction()
            
            return CallAction()
        
        return FoldAction()



if __name__ == '__main__':
    run_bot(Player(), parse_args())
