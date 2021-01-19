from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import BooleanProperty

from flask import json

login_kv = '''

<LoginScreen>:  
    Label:
        text: "Log In"
        font_size: 25
        size_hint: (.5, .15)
        pos_hint: {'center_x': .5, 'center_y': .9}
    Label:
        text: 'URL'
        text_size: self.size
        halign: 'right'
        valign: 'center'
        size_hint: (.2, .2)
        pos_hint: {'right': .25, 'center_y': .70}
    TextInput:
        id: url
        text: 'http://localhost:5000'
        multiline: False
        size_hint: (.6, None)
        height: 30
        pos_hint: {'x': .3, 'center_y': .7}
    Label:
        text: 'Name'
        text_size: self.size
        halign: 'right'
        valign: 'center'
        size_hint: (.2, .2)
        pos_hint: {'right': .25, 'center_y': .6}
    TextInput:
        id: name
        text: ''
        multiline: False
        size_hint: (.6, None)
        height: 30
        pos_hint: {'x': .3, 'center_y': .6}
    Button:
        id: connect
        text: 'Connect'
        size_hint: (.2, .2)
        pos_hint: {'center_x': .5, 'center_y': .25}
        on_release: root.connect()

'''


class LoginScreen(FloatLayout):
    connected = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.connected = False
        Builder.load_string(login_kv)
        super(LoginScreen, self).__init__(**kwargs)

    def connect(self):
        print(f"Connecting {self.ids['name'].text} to {self.ids['url'].text}")
        req = UrlRequest(url=f"{self.ids['url'].text}/new_user", on_success=self.handle_response,
                         on_failure=self.show_error_msg, on_error=self.show_error_msg,
                         req_body=json.dumps({'player_name': self.ids['name'].text}),
                         req_headers={'Content-Type': 'application/json'},
                         timeout=None, method='POST', decode=True, debug=False, file_path=None, ca_file=None,
                         verify=False)

    def handle_response(self, req, res):
        self.connected = True

    @staticmethod
    def show_error_msg(req, error):
        print('Error')
        print(error)


class LoginApp(App):
    page = None

    def build(self):
        self.page = LoginScreen()
        return self.page


if __name__ == "__main__":
    ns = LoginApp()
    ns.run()
