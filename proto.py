class ProtoBot:
    def __init__(self):
        self.is_enabled=True
        self.verbosity=50
        # 5 : rare messages only
        # 10: messages every game
        # 20: messages multiple times per game
        # 30: messages every move
        # 50: all messages
    def enable(self):
        """Enable the bot"""
        self.is_enabled=True
    def disable(self):
        """Disable the bot"""
        self.is_enabled=False
    def set_verbosity(self,value=100):
        """Set the verbosity level"""
        self.is_verbose=value
    def debug_print(self, verbosity, s):
        if verbosity <= self.verbosity:
            print(s)
    def ping(self,s):
        if self.is_enabled:
            return "pong"
        else:
            print("=====================================")
            print("BOT IS OFFLINE: DID NOT REPLY TO PING")
            print("=====================================")
            return "The bot is currently offline"
    def start_game(self, game_id, player_id, initial_discard, other_player_id):
        """The start_game function will be called at the beginning of a game,
giving you the opportunity to initialize any state you may need.

        Keyword arguments:
        game_id -- An integer representing the game you are currently playing. This is purely advisory, but may be useful in your debugging and logging. This integer may also be used to lookup the game on the website.
        player_id -- A zero-based index indicating which player you are this round. Player 0 goes first, player 1 goes second.
        initial_discard -- A number indicating what the initial discard is.
        other_player_id -- The team ID of the other player, which can be used to go to the team page by feeding it in the obvious manner to the /team/ URI.

        Return value: None
        """
        self.debug_print(10,"#%d: Began game with player ID %d, initial discard %d" % (game_id, player_id, initial_discard))
    def get_move(self, game_id, rack, discard, remaining_microseconds, other_player_moves):
        """ The get_move function will be called to obtain the move your player wishes to make.

        Keyword arguments:
        game_id -- An integer matching the one sent with the corresponding start_game call.
        rack -- This is an array of ints, corresponding to the current 20 cards in your rack.
        discard -- This is a single int, corresponding to the top card on the discard pile.
        remaining_microseconds -- An integer which is the approximate count of the remaining microseconds available to your bot in this game.
        other_player_moves -- A list of moves (dictionary type), see below. List will have one element, or be empty (on player 0's first turn)

        Format of one of other player's moves:
        "move" : one of:
           "take_discard" # meaning that your opponent took the discard and placed in the idx slot in their rack.
           "take_deck" # meaning that your opponent took a card from the deck and placed it in the idx slot in their rack.
           "no_move" # meaning your opponent failed to successfully make a move
           "illegal" # meaning your opponent made an illegal move, which was illegal for the reason given in the reason field
           "timed_out" # meaning your opponent has run out of time and they can no longer make moves in this game
        "idx": [Optionally!] idx will appear for the moves mentioned as having that parameter bove
        "reason": [Optionally!] reason will appear for the illegal move case

        Return value:
        either {"move": "request_deck"} or {"move": "request_discard", "idx":index_of_card_to_replace}

        Recommended: instead use one of
        return self.request_deck()
        return self.request_discard(index)
        """
        self.debug_print (30,"#%d: Asked to make move with rack %s and discard pile %d" %(game_id, rack, discard))
        return self.request_discard(0)
    def request_deck(self):
        """ Creates output for requesting a card from the deck

        Usage: return self.request_deck()
        """
        self.debug_print(30,"Requesting a card from the deck")
        return {"move": "request_deck"}
    def request_discard(self, index):
        """Creates output for discarding a card

        Usage: return self.request_discard(index)

        Keyword arguments:
        index -- zero-based index of the card to replace
        """
        self.debug_print(30, "Requesting to discard card with index %d" % index)
        return {"move": "request_discard", "idx":index}

    def get_deck_exchange(self,game_id, remaining_microseconds, rack, card):
        """If you return a move of type request_deck for a get_move call, the server will make this call to you.

        Keyword arguments:
        game_id -- An integer matching the one sent with the corresponding start_game call.
        remaining_microseconds -- An integer which is the approximate
        rack -- A list of 20 integers corresponding to your rack, for your convenience. (There will have been no changes since the get_move call.)
        card -- An integer representing the card number that you must place in your rack.

        Return value:
        An integer which is the zero-based index of which slot in your rack you wish to place this card.
        """
        self.debug_print(30,"#%d: Asked to exchange one of rack %s for card %d" % (game_id, rack, card))
        return 0

    def move_result(self,game_id, move, reason=""):
        """After making a move, which may be a discard swap, a deck swap, or a failed move, the game driver will make this advisory call to your program to notify you about the outcome of your move.

        Keyword arguments:
        game_id -- An integer matching the one sent with the corresponding start_game call.
        move -- one of "next_player_move", "move_ended_game", "illegal"
        reason -- human-readable reason of why the move was illegal or ended the game

        Note: reason is an empty string if the move was legal and the game continues as normal.

        Return value:
        None
"""
        if move=="move_ended_game":
            print ("#%d: Game ended after my move. Reason: %s" % (game_id, reason))
        elif move=="illegal":
            print ("#%d: Illegal move. Reason: %s" % (game_id, reason))
        else:
            self.debug_print (35,"#%d: Move successful" % (game_id))

    def game_result(self,game_id, your_score, other_score, reason):
        """After a game completes, the game driver will make this advisory call to your program to notify it about the outcome of the game.

After this call is received, you will receive no further communication for the game corresponding to the given game_id.

        game_id -- A number corresponding to the game_ids received previously.
        your_score -- Your score for this game, as an integer.
        other_score -- The score of your opponent, as an integer.
        reason -- A human-readable string explaining why the game is over"""
        self.debug_print(10,"#%d: The game is over. Our score: %d. Opponent score: %d. Reason: %s" % (game_id,your_score, other_score, reason))

