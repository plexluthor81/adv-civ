from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

from contextlib import suppress
from flask import json

# the dropdown weakly reference error from unwanted GC was fixed based on this:
# https://stackoverflow.com/questions/46060693/referenceerror-weakly-referenced-object-no-longer-exists-kivy-dropdown

nation_selector_kv = '''

<NationDropDown>:
    btn: btn.__self__
    __safe_id: [dropdown.__self__]
    Button:
        id: btn
        text: 'Close'
        size_hint: (.5, .8)
        pos_hint: {'x': 0, 'center_y': .5}
        on_release: root.release(self)
        on_parent: dropdown.dismiss()
        on_press: root.update()

    DropDown:
        id: dropdown
        btn_africa: btn_africa.__self__
        on_select: root.parent.parent.select(root.parent, f"{args[1]}")
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
    ndd: ndd.__self__
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
    pr1: pr1.__self__ 
    Label:
        text: "Nation Selection"
        font_size: 25
        size_hint: (.5, .15)
        pos_hint: {'center_x': .5, 'center_y': .9}
    PlayerRow:
        id: pr1
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

    def release(self, button):
        if button.text in ["Close", "Open"]:
            self.parent.parent.select(self.parent, button.text)
            return

        dd = self.ids['dropdown']
        dd.open(button)
        dd.x += self.ids['btn'].width
        dd.pos_hint = {'center_y': 0.5}

    def update(self):
        nss = self.parent.parent
        selected_nations = [self.ids['btn'].text]
        for pr in nss.children:
            if pr == self:
                continue
            if isinstance(pr, PlayerRow):
                selected_nation = pr.ids['ndd'].ids['btn'].text
                if selected_nation in selected_nations:
                    player = pr.ids['lname'].text
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
    player_name = StringProperty('')
    player_num = NumericProperty(0)
    nation = StringProperty('')
    refs = []
    finished = BooleanProperty(False)

    def __init__(self, server_url='', player_name='', **kwargs):
        self.server_url = server_url
        self.player_name = player_name
        self.finished = False
        Builder.load_string(nation_selector_kv)
        Clock.schedule_once(self.request_update)
        super(NationSelectionScreen, self).__init__(**kwargs)

    def get_selected_nations(self):
        prs = sorted([pr for pr in self.children if isinstance(pr, PlayerRow)], key=lambda pr: pr.player_num)
        selected_nations = [pr.ids['ndd'].ids['btn'].text for pr in prs]
        while 'Open' in selected_nations:
            selected_nations.remove('Open')
        return selected_nations

    def request_update(self, *args):
        if self.server_url and self.player_name and not self.finished:
            req = UrlRequest(url=f"{self.server_url}/nation_selection", on_success=self.handle_update,
                             on_failure=self.show_error_msg, on_error=self.show_error_msg,
                             req_body=None,
                             req_headers={'Content-Type': 'application/json'},
                             timeout=None, method='GET', decode=True, debug=False, file_path=None, ca_file=None,
                             verify=False)

    def handle_update(self, req, res):
        res_list = json.loads(res)
        print(res_list)
        prs = sorted([pr for pr in self.children if isinstance(pr, PlayerRow)], key=lambda pr: pr.player_num)
        if self.player_num == 0:
            player_names = [p['player_name'] for p in res_list]
            self.player_num = player_names.index(self.player_name) + 1
            print(f"I'm player #{self.player_num}")
            mypr = prs[self.player_num-1]
            mypr.player_name = self.player_name
            mypr.ids['ndd'].ids['btn'].text = res_list[self.player_num-1]['nation']
        for i in range(8):
            if prs[i].player_name != res_list[i]['player_name']:
                # print(f"updating #{i+1} name to {res_list[i]['player_name']}")
                prs[i].player_name = res_list[i]['player_name']
            if prs[i].ids['ndd'].ids['btn'].text != res_list[i]['nation']:
                # print(f"updating #{i+1} nation to {res_list[i]['nation']}")
                if prs[i].player_name == 'Open':
                    prs[i].ids['ndd'].ids['btn'].text = 'Close'
                elif prs[i].player_name == 'Closed':
                    prs[i].ids['ndd'].ids['btn'].text = 'Open'
                else:
                    prs[i].ids['ndd'].ids['btn'].text = res_list[i]['nation']
            if prs[i].player_name not in [self.player_name, 'Open', 'Closed']:
                prs[i].ids['ndd'].ids['btn'].disabled = True
            else:
                prs[i].ids['ndd'].ids['btn'].disabled = False

        nations = [p['nation'] for p in res_list]
        if 'Not Selected' not in nations:
            self.finished = True
            return False
        if not req.req_body:
            Clock.schedule_once(self.request_update, 1)

    def post(self, post_dict):
        req = UrlRequest(url=f"{self.server_url}/nation_selection", on_success=self.handle_update,
                         on_failure=self.show_error_msg, on_error=self.show_error_msg,
                         req_body=json.dumps(post_dict),
                         req_headers={'Content-Type': 'application/json'},
                         timeout=None, method='POST', decode=True, debug=False, file_path=None, ca_file=None,
                         verify=False)

    def select(self, pr, selection_text):
        print(f'select: {selection_text} for #{pr.player_num}')
        if selection_text == 'Close':
            pr.ids['ndd'].ids['btn'].text = 'Open'
            self.post({"player_num": pr.player_num, "nation": selection_text})
            return
        if selection_text == 'Open':
            pr.ids['ndd'].ids['btn'].text = 'Close'
            self.post({"player_num": pr.player_num, "nation": selection_text})
            return
        if pr.player_num == self.player_num:
            pr.ids['ndd'].ids['btn'].text = selection_text
            self.post({"player_name": self.player_name, "nation": selection_text})

    @staticmethod
    def show_error_msg(request, error):
        print('Error')
        print(error)


class NationSelectorApp(App):
    page = None

    def build(self):
        self.page = NationSelectionScreen('http://localhost:5000', 'Ren')
        return self.page


if __name__ == "__main__":
    ns = NationSelectorApp()
    ns.run()


        
