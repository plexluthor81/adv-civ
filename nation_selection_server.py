from flask import Flask, json, request
from random import randrange

# Open a terminal run this with python3 drag_server.py

players = [{'player_name': 'Open', 'nation': 'Not Selected'}, {'player_name': 'Open', 'nation': 'Not Selected'},
           {'player_name': 'Open', 'nation': 'Not Selected'}, {'player_name': 'Open', 'nation': 'Not Selected'},
           {'player_name': 'Open', 'nation': 'Not Selected'}, {'player_name': 'Open', 'nation': 'Not Selected'},
           {'player_name': 'Open', 'nation': 'Not Selected'}, {'player_name': 'Open', 'nation': 'Not Selected'}]

valid_nations = ['Africa', 'Italy', 'Illyria', 'Thrace', 'Crete', 'Asia', 'Assyria', 'Bablyon', 'Egypt']

api = Flask(__name__)


@api.route('/nation_selection', methods=['GET', 'POST'])
def get_nation_selection():
    if request.method == 'GET':
        return json.dumps(players)
    if request.method == 'POST':
        nation_selection_dict = request.get_json(force=True)
        player_names = [p['player_name'] for p in players]
        nations = [p['nation'] for p in players]
        if ('player_name' not in nation_selection_dict) \
                or ('nation' not in nation_selection_dict) \
                or (nation_selection_dict['player_name'] not in player_names) \
                or (nation_selection_dict['nation'] not in valid_nations):
            return json.dumps({"success": False}), 400
        nations = [p['nation'] for p in players]
        if nation_selection_dict['nation'] in nations:
            return json.dumps({"success": False}), 409
        index = player_names.index(nation_selection_dict['player_name'])
        player_names[index]['nation'] = nation_selection_dict['nation']
        return json.dumps(players), 200


@api.route('/new_user', methods=['POST'])
def get_new_user():
    # Expecting a dictionary with a player_name entry
    if request.method == 'POST':
        new_user_dict = request.get_json(force=True)
        player_names = [p['player_name'] for p in players]
        if new_user_dict['player_name'] not in player_names:
            if 'Open' not in player_names:
                # No room for a new player
                return json.dumps({"success": False}), 409

            # If you want to place players randomly, and then let lucky ones pick first:
            # index = randrange(0, 8)
            # while players[index]['player_name'] != 'Open':
            #    index = randrange(0, 8)

            # If you want to place players first-come-first-pick:
            index = player_names.index('Open')

            players[index]['player_name'] = new_user_dict['player_name']
            return json.dumps(players), 201
        else:
            # Existing player
            return json.dumps({"success": False}), 409
    return json.dumps({"success": False}), 400

if __name__ == '__main__':
    api.run()
