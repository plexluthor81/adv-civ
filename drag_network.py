from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.behaviors import DragBehavior
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

from flask import json

# Open two terminals, and run this twice (same exact file on both, and actually you can run as many as you like)

# You could also put the following in your kv file...
kv = '''
<DragLabel>:
    # Define the properties for the DragLabel
    drag_rectangle: self.x, self.y, self.width, self.height
    drag_timeout: 10000000
    drag_distance: 0

FloatLayout:
    # Define the root widget
    DragLabel:
        id: africa
        size_hint: 0.25, 0.2
        text: 'africa'
    DragLabel:
        id: italy
        size_hint: 0.25, 0.2
        text: 'italy'
'''


class DragLabel(DragBehavior, Label):
    def __init__(self, **kwargs):
        Clock.schedule_interval(self.do_network_get, 0.5)
        self.moving = False
        super(DragLabel, self).__init__(**kwargs)

    def do_network_get(self, *args):
        print(f"Sending GET from {self.text}")
        req = UrlRequest(url=f'http://localhost:5000/{self.text}', on_success=self.handle_get_result, 
                 on_failure=self.show_error_msg, on_error=self.show_error_msg,
                 req_body=None, req_headers=None,
                 timeout=None, method='GET', decode=True, debug=False, file_path=None, ca_file=None,
                 verify=False)

    def handle_get_result(self, req, result):
        result = json.loads(result)
        if self.text == result['id']:
            if self.moving:
                print(f"Ignoring GET result in {self.text} because it's moving")
            else:
                self.pos_hint = result['pos_hint']
        else:
            print(f"IDs didn't match: {self.text} got {result['id']}")

    def show_error_msg(self, *args):
        print('Something went wrong with a network request')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pos_hint = {}
            self.moving = True
        return super(DragLabel, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.moving:
            self.moving = False
            self.pos_hint = {'x': self.pos[0]/self.parent.size[0], 'y': self.pos[1]/self.parent.size[1]}
            print(f"POSTing from {self.text}")
            req = UrlRequest(url=f'http://localhost:5000/{self.text}', on_success=self.check_post_response, 
                 on_failure=self.show_error_msg, on_error=self.show_error_msg,
                 req_body=json.dumps({"id": self.text, "pos_hint": self.pos_hint}), req_headers={'Content-Type': 'application/json'},
                 timeout=None, method='POST', decode=True, debug=False, file_path=None, ca_file=None,
                 verify=False)
        return super(DragLabel, self).on_touch_up(touch)

    def check_post_response(self, *args):
        print("POST response received (and not actually checked, because I'm lazy")



class TestApp(App):
    def build(self):
        return Builder.load_string(kv)

TestApp().run()
