from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import BooleanProperty, StringProperty

from flask import json


class LoginScreen(FloatLayout):
    connected = BooleanProperty(False)
    url = StringProperty('http://localhost:5000')
    name = StringProperty('')

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.connected = False
        self.url = 'http://localhost:5000'
        self.name = ''
        self.add_widget(Label(text="Log In", font_size=25, size_hint=(.5, .15), pos_hint={'center_x': .5, 'center_y': .9}))

        url_label = Label(text="URL", halign='right', valign='center', size_hint=(.2, .2), pos_hint={'right': .25, 'center_y': .7})
        url_label.text_size = url_label.size
        self.add_widget(url_label)

        url_input = TextInput(text='http://localhost:5000', multiline=False, size_hint=(.6,None), height=30, pos_hint={'x': .3, 'center_y': .7})
        url_input.bind(text=self.setter('url'))
        self.add_widget(url_input)

        name_label = Label(text="Name", halign='right', valign='center', size_hint=(.2, .2), pos_hint={'right': .25, 'center_y': .6})
        name_label.text_size = name_label.size
        self.add_widget(name_label)

        name_input = TextInput(text='', multiline=False, size_hint=(.6,None), height=30, pos_hint={'x': .3, 'center_y': .6})
        name_input.bind(text=self.setter('name'))
        self.add_widget(name_input)

        self.add_widget(Button(text='Connect', size_hint=(.2, .2), pos_hint={'center_x': .5, 'center_y': .25}, on_release=self.connect))

    def connect(self, instance):
        print(f"Connecting {self.name} to {self.url}")
        req = UrlRequest(url=f"{self.url}/new_user", on_success=self.handle_response,
                         on_failure=self.show_error_msg, on_error=self.show_error_msg,
                         req_body=json.dumps({'player_name': self.name}),
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
    def __init__(self, **kwargs):
        super(LoginApp, self).__init__(**kwargs)
        self.page = None

    def build(self):
        self.page = LoginScreen()
        return self.page


if __name__ == "__main__":
    ns = LoginApp()
    ns.run()
