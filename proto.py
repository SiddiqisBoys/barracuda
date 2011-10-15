from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import os

# Proto functions
class ProtoBot:
    def __init__(self):
        pass
    def ping(self,s):
        global bot_enabled
        if bot_enabled:
            return "pong"
        else:
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
        pass
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
        return self.request_deck()
    def request_deck(self):
        """ Creates output for requesting a card from the deck

        Usage: return self.request_deck()
        """
        return {"move": "request_deck"}
    def request_discard(self, index):
        """ Creates output for discarding a card

        Usage: return self.request_discard(index)

        Keyword arguments:
        index -- zero-based index of the card to replace
        """
        return {"move": "request_deck", "idx":index}

    def get_deck_exchange(game_id, remaining_microseconds, rack, card):
        """If you return a move of type request_deck for a get_move call, the server will make this call to you.

        Keyword arguments:
        game_id -- An integer matching the one sent with the corresponding start_game call.
        remaining_microseconds -- An integer which is the approximate
        rack -- A list of 20 integers corresponding to your rack, for your convenience. (There will have been no changes since the get_move call.)
        card -- An integer representing the card number that you must place in your rack.

        Return value:
        An integer which is the zero-based index of which slot in your rack you wish to place this card.
        """
        return 0

    def move_result(game_id, move, reason=""):
        """After making a move, which may be a discard swap, a deck swap, or a failed move, the game driver will make this advisory call to your program to notify you about the outcome of your move.

        Keyword arguments:
        game_id -- An integer matching the one sent with the corresponding start_game call.
        move -- one of "next_player_move", "move_ended_game", "illegal"
        reason -- human-readable reason of why the move was illegal or ended the game

        Note: reason is an empty string if the move was legal and the game continues as normal.

        Return value:
        None
"""
        pass

    def game_result(game_id, your_score, other_score, reason):
        """After a game completes, the game driver will make this advisory call to your program to notify it about the outcome of the game.

After this call is received, you will receive no further communication for the game corresponding to the given game_id.

        game_id -- A number corresponding to the game_ids received previously.
        your_score -- Your score for this game, as an integer.
        other_score -- The score of your opponent, as an integer.
        reason -- A human-readable string explaining why the game is over"""
        pass


# SETUP
the_bot = ProtoBot()
server_ip="172.16.114.240"
server_port=8000
bot_enabled = True




# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer((server_ip, server_port),
                            requestHandler=RequestHandler)
server.register_introspection_functions()


server.register_function(the_bot.ping, 'ping')

def start_game_helper(data):
    the_bot.start_game(data["game_id"],
                       data["player_id"],
                       data["initial_discard"],
                       data["other_player_id"])
    return ""
server.register_function(start_game_helper, "start_game")

def get_move_helper(data):
    other_player_moves=[ x[1] for x in data["other_player_moves"] ]

    return the_bot.get_move(data["game_id"],
                            data["rack"],
                            data["discard"],
                            data["remaining_microseconds"],
                            other_player_moves)
server.register_function(get_move_helper, "get_move")

def get_deck_exchange_helper(data):
    return the_bot.get_exchange(data["game_id"],
                                data["remaining_microseconds"],
                                data["rack"],
                                data["card"])

server.register_function(get_deck_exchange_helper, "get_deck_exchange")

def move_result_helper(data):
    move = data["move"]
    if move=="next_player_move" or move=="move_ended_game":
        reason = data["reason"]
    else:
        reason = ""
    the_bot.get_move_result(data["game_id"],
                            move,
                            reason)
    return ""

server.register_function(move_result_helper, "move_result")

def game_result_helper(data):
    the_bot.get_move_result(data["game_id"],
                            data["your_score"],
                            data["other_score"],
                            data["reason"])
    return ""

server.register_function(move_result_helper, "move_result")


# Run the server's main loop
server.serve_forever()
