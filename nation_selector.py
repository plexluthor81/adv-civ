from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

from contextlib import suppress
from flask import json

nation_selector_kv = '''

<NationDropDown>:
    Button:
        id: btn
        text: 'Not Selected'
        size_hint: (.5, .8)
        pos_hint: {'x': 0, 'center_y': .5}
        on_release: root.open_at_right(self)
        on_parent: dropdown.dismiss()
        on_press: root.update()

    DropDown:
        id: dropdown
        on_select: btn.text = f"{args[1]}"
        Button:
            id: btn_africa
            text: 'Africa'
            size_hint_y: None
            height: 35
            on_release: dropdown.select('Africa')
        Button:
            id: btn_italy
            text: 'Italy'
            size_hint_y: None
            height: 35
            on_release: dropdown.select('Italy')
        Button:
            id: btn_illyria
            text: 'Illyria'
            size_hint_y: None
            height: 35
            on_release: dropdown.select('Illyria')
        Button:
            id: btn_thrace
            text: 'Thrace'
            size_hint_y: None
            height: 35
            on_release: dropdown.select('Thrace')
        Button:
            id: btn_crete
            text: 'Crete'
            size_hint_y: None
            height: 35
            on_release: dropdown.select('Crete')
        Button:
            id: btn_asia
            text: 'Asia'
            size_hint_y: None
            height: 35
            on_release: dropdown.select('Asia')
        Button:
            id: btn_assyria
            text: 'Assyria'
            size_hint_y: None
            height: 35
            on_release: dropdown.select('Assyria')
        Button:
            id: btn_babylon
            text: 'Babylon'
            size_hint_y: None
            height: 35
            on_release: dropdown.select('Babylon')
        Button:
            id: btn_egypt
            text: 'Egypt'
            size_hint_y: None
            height: 35
            on_release: dropdown.select('Egypt')

<PlayerRow>:
    Label:
        id: lnum
        text: "Player " + str(root.player_num)
        text_size: self.size
        halign: 'right'
        valign: 'center'
        size_hint: (.33, 1)
        pos_hint: {'right': .35, 'center_y': .5}
    Label:
        id: lname
        text: root.player_name
        text_size: self.size
        halign: 'center'
        valign: 'center'
        size_hint: (None, 1)
        pos_hint: {'center_x': .5, 'center_y': .5}
    NationDropDown:
        id: ndd
        size_hint: (.33, 1)
        pos_hint: {'x': .65, 'center_y': .5}
       

<NationSelectionScreen>:
    Label:
        text: "Nation Selection"
        font_size: 25
        size_hint: (.5, .15)
        pos_hint: {'center_x': .5, 'center_y': .9}
    PlayerRow:
        player_num: 1
        player_name: 'Open'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .75}
    PlayerRow:
        player_num: 2
        player_name: 'Open'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .65}
    PlayerRow:
        player_num: 3
        player_name: 'Open'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .55}
    PlayerRow:
        player_num: 4
        player_name: 'Open'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .45}
    PlayerRow:
        player_num: 5
        player_name: 'Open'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .35}
    PlayerRow:
        player_num: 6
        player_name: 'Open'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .25}
    PlayerRow:
        player_num: 7
        player_name: 'Open'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .15}
    PlayerRow:
        player_num: 8
        player_name: 'Open'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .05}
'''


class NationDropDown(FloatLayout):
    def on_press(self):
        pass
        # App.get_running_app().show_stuff()

    def open_at_right(self, button):
        dd = self.ids['dropdown']
        dd.open(button)

        dd.x += self.ids['btn'].width
        dd.pos_hint = {'center_y': 0.5}

    def update(self):
        root = App.get_running_app().root
        selected_nations = [self.ids['btn'].text]
        for pr in root.children:
            if pr == self:
                continue
            if isinstance(pr, PlayerRow):
                selected_nation = pr.ids['ndd'].ids['btn'].text
                if selected_nation in selected_nations:
                    player = pr.ids['lname'].text
                    print(f'Multiple people have selected {selected_nation}: {player} and at least one other')
                else:
                    selected_nations.append(selected_nation)
    
        with suppress(ValueError):
            selected_nations.remove(self.ids['btn'].text)
            selected_nations.remove('Not Selected')

        self.ids['btn_africa'].disabled = 'Africa' in selected_nations
        self.ids['btn_italy'].disabled = 'Italy' in selected_nations
        self.ids['btn_illyria'].disabled = 'Illyria' in selected_nations
        self.ids['btn_thrace'].disabled = 'Thrace' in selected_nations
        self.ids['btn_crete'].disabled = 'Crete' in selected_nations
        self.ids['btn_asia'].disabled = 'Asia' in selected_nations
        self.ids['btn_assyria'].disabled = 'Assyria' in selected_nations
        self.ids['btn_babylon'].disabled = 'Babylon' in selected_nations
        self.ids['btn_egypt'].disabled = 'Egypt' in selected_nations


class PlayerRow(FloatLayout):
    player_num = NumericProperty(-1)
    player_name = StringProperty('Player Name')
        

class NationSelectionScreen(FloatLayout):
    server_url = StringProperty('')

    def __init__(self, server_info='', **kwargs):
        self.server_info = server_info
        super(NationSelectionScreen, self).__init__(**kwargs)


class NationSelectorApp(App):
    player_name = 'Initializing'
    player_num = 0
    page = None
    server_info = {}

    def check_post_response(self, resp, *args):
        print(resp)

    def show_error_msg(self, *args):
        print('Some Error Happened')

    def set_server(self, url):
        self.server_info = {'url': url}

    def set_player(self, player_name):
        self.player_name = player_name

    def build(self):
        Clock.schedule_interval(self.refresh, 1)
        Builder.load_string(nation_selector_kv)
        self.page = NationSelectionScreen(self.server_info)
        return self.page

    def refresh(self, resp, *args):
        pass

    def initialize_from_server(self, resp, *args):
        pass


if __name__ == "__main__":
    ns = NationSelectorApp()
    # ns.set_server('http://localhost:5000')
    # ns.set_player('Steve')
    # req = UrlRequest(url=f"{ns.server_info['url']}/new_user", on_success=ns.initialize_from_server,
    #                  on_failure=ns.show_error_msg, on_error=ns.show_error_msg,
    #                  req_body=json.dumps({"player_name": ns.player_name}),
    #                  req_headers={'Content-Type': 'application/json'},
    #                  timeout=None, method='POST', decode=True, debug=False, file_path=None, ca_file=None,
    #                  verify=False)
    ns.run()


        
