from flask import Flask, json, request

# Open a terminal run this with python3 drag_server.py

draglabels = [{"id": 'africa', "pos_hint": {'x': .5, 'y': .5}}, {"id": 'italy', "pos_hint": {'x': .5, 'y': .5}}]

api = Flask(__name__)

@api.route('/all', methods=['GET'])
def get_all():
  return json.dumps(draglabels)

@api.route('/africa', methods=['GET', 'POST'])
def get_africa():
    if request.method == 'GET':
        return json.dumps(draglabels[0])
    if request.method == 'POST':
        post_json = request.get_json(force=True)
        if post_json['id']==draglabels[0]['id']:
            draglabels[0]['pos_hint'] = post_json['pos_hint']
        else:
            print(f"IDs didn't match: expected {draglabels[0]['id']} got {post_json['id']}")
        return json.dumps({"success": True}), 201

@api.route('/italy', methods=['GET', 'POST'])
def get_italy():
    if request.method == 'GET':
        return json.dumps(draglabels[1])
    if request.method == 'POST':
        post_json = request.get_json(force=True)
        if post_json['id']==draglabels[1]['id']:
            draglabels[1]['pos_hint'] = post_json['pos_hint']
        else:
            print(f"IDs didn't match: expected {draglabels[1]['id']} got {post_json['id']}")
        return json.dumps({"success": True}), 201

if __name__ == '__main__':
    api.run()
