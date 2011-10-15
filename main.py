from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import traceback

from proto import ProtoBot
from racko import botdfs, bot_heur

# SETUP Variables
#the_bot = ProtoBot()
the_bot = bot_heur()
server_ip="172.16.114.240"
server_port=8000



# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer((server_ip, server_port),
                            requestHandler=RequestHandler)
server.register_introspection_functions()


# Register the functions
server.register_function(the_bot.ping, 'ping')

def start_game_helper(data):
    try:
        the_bot.start_game(data["game_id"],
                           data["player_id"],
                           data["initial_discard"],
                           data["other_player_id"])
    except Exception as e:
        traceback.print_exc()
    return ""
server.register_function(start_game_helper, "start_game")

def get_move_helper(data):
    try:
        other_player_moves=[ x[1] for x in data["other_player_moves"] ]
        return the_bot.get_move(data["game_id"],
                                data["rack"],
                                data["discard"],
                                data["remaining_microseconds"],
                                other_player_moves)
    except Exception as e:
        traceback.print_exc()
server.register_function(get_move_helper, "get_move")

def get_deck_exchange_helper(data):
    try:
        return the_bot.get_deck_exchange(data["game_id"],
                                         data["remaining_microseconds"],
                                         data["rack"],
                                         data["card"])
    except Exception as e:
        traceback.print_exc()


server.register_function(get_deck_exchange_helper, "get_deck_exchange")

def move_result_helper(data):
    try:
        move = data["move"]
        if move=="next_player_move" or move=="move_ended_game":
            reason = data["reason"]
        else:
            reason = ""
            the_bot.move_result(data["game_id"],
                                move,
                                reason)
    except Exception as e:
        traceback.print_exc()

    return ""

server.register_function(move_result_helper, "move_result")

def game_result_helper(data):
    try:
        the_bot.game_result(data["game_id"],
                            data["your_score"],
                            data["other_score"],
                            data["reason"])
    except Exception as e:
        traceback.print_exc()
    return ""

server.register_function(game_result_helper, "game_result")


# Run the server's main loop
server.serve_forever()
