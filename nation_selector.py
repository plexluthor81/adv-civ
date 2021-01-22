from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

from contextlib import suppress
from flask import json

# the dropdown weakly reference error from unwanted GC was fixed based on this:
# https://stackoverflow.com/questions/46060693/referenceerror-weakly-referenced-object-no-longer-exists-kivy-dropdown

nation_dropdown_kv = '''

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

'''


class NationDropDown(FloatLayout):
    def __init__(self, **kwargs):
        Builder.load_string(nation_dropdown_kv)
        super(NationDropDown, self).__init__(**kwargs)

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
        for pr in nss.prs:
            if pr == self:
                continue
            selected_nation = pr.ndd.ids['btn'].text
            if selected_nation not in selected_nations:
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

    def __init__(self, **kwargs):
        super(PlayerRow, self).__init__(**kwargs)
        self.player_num = -1
        self.player_name = ''
        self.ndd = None


class NationSelectionScreen(FloatLayout):
    server_url = StringProperty('')
    player_name = StringProperty('')
    player_num = NumericProperty(0)
    nation = StringProperty('')
    finished = BooleanProperty(False)
    nations = ListProperty(
        ['Not Selected', 'Not Selected', 'Not Selected', 'Not Selected', 'Not Selected', 'Not Selected', 'Not Selected',
         'Not Selected'])
    names = ListProperty(['Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open'])

    def __init__(self, server_url='', player_name='', **kwargs):
        self.server_url = server_url
        self.player_name = player_name
        self.player_num = 0
        self.nation = ''
        self.finished = False
        self.nations = ['Not Selected','Not Selected','Not Selected','Not Selected','Not Selected','Not Selected','Not Selected','Not Selected']
        self.names = ['Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open', 'Open']
        self.prs = [None, None, None, None, None, None, None, None]

        Clock.schedule_once(self.request_update)
        super(NationSelectionScreen, self).__init__(**kwargs)
        self.add_widget(Label(text="Nation Selection", font_size=25, size_hint=(.5, .15), pos_hint={'center_x':.5, 'center_y': .9}))
        for i in range(8):
            self.add_player_row(i)
        self.bind(names=self.update_pr_names)
        self.bind(nations=self.update_pr_nations)

    def update_pr_names(self):
        for i in range(8):
            if self.prs[i]:
                self.prs[i].player_name = self.names[i]

    def update_pr_nations(self):
        for i in range(8):
            if self.prs[i]:
                self.prs[i].player_name = self.names[i]

    def add_player_row(self, num):
        self.prs[num] = PlayerRow(size_hint=(1, .1), pos_hint={'x': 0, 'y': 0.75-num/10.0})
        self.prs[num].player_num = num+1
        print(self.names[num])
        self.prs[num].player_name = self.names[num]
        pr_label = Label(text="Player "+str(num+1), halign='right', valign='center', size_hint=(.33, 1), pos_hint={'right': 0.35, 'center_y': 0.5})
        pr_label.text_size = pr_label.size
        self.prs[num].add_widget(pr_label)
        pr_name = Label(text=self.prs[num].player_name, halign='center', valign='center', size_hint=(.33, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.prs[num].bind(player_name=pr_name.setter('text'))
        pr_name.text_size = pr_name.size
        self.prs[num].add_widget(pr_name)
        self.prs[num].ndd = NationDropDown(size_hint=(.33, 1), pos_hint={'x': .65, 'center_y': .5})
        self.prs[num].add_widget(self.prs[num].ndd)
        self.add_widget(self.prs[num])

    def get_selected_nations(self):
        selected_nations = [pr.ndd.ids['btn'].text for pr in self.prs]
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
        if self.player_num == 0:
            player_names = [p['player_name'] for p in res_list]
            self.player_num = player_names.index(self.player_name) + 1
            print(f"I'm player #{self.player_num}")
            mypr = self.prs[self.player_num-1]
            print(mypr)
            print(mypr.player_name)
            mypr.player_name = self.player_name
            print(mypr.player_name)
            print(mypr.ndd)
            print(mypr.ndd.ids)
            mypr.ndd.ids['btn'].text = res_list[self.player_num-1]['nation']
        for i in range(8):
            if self.prs[i].player_name != res_list[i]['player_name']:
                # print(f"updating #{i+1} name to {res_list[i]['player_name']}")
                self.prs[i].player_name = res_list[i]['player_name']
            if self.prs[i].ndd.ids['btn'].text != res_list[i]['nation']:
                # print(f"updating #{i+1} nation to {res_list[i]['nation']}")
                if self.prs[i].player_name == 'Open':
                    self.prs[i].ndd.ids['btn'].text = 'Close'
                elif self.prs[i].player_name == 'Closed':
                    self.prs[i].ndd.ids['btn'].text = 'Open'
                else:
                    self.prs[i].ndd.ids['btn'].text = res_list[i]['nation']
            if self.prs[i].player_name not in [self.player_name, 'Open', 'Closed']:
                self.prs[i].ndd.ids['btn'].disabled = True
            else:
                self.prs[i].ndd.ids['btn'].disabled = False
        self.nation = res_list[self.player_num-1]['nation']

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
            pr.ndd.ids['btn'].text = 'Open'
            self.post({"player_num": pr.player_num, "nation": selection_text})
            return
        if selection_text == 'Open':
            pr.ndd.ids['btn'].text = 'Close'
            self.post({"player_num": pr.player_num, "nation": selection_text})
            return
        if pr.player_num == self.player_num:
            pr.ndd.ids['btn'].text = selection_text
            self.post({"player_name": self.player_name, "nation": selection_text})

    @staticmethod
    def show_error_msg(request, error):
        print('Error')
        print(error)


class NationSelectorApp(App):
    def __init__(self, **kwargs):
        super(NationSelectorApp, self).__init__(**kwargs)
        self.page = None

    def build(self):
        self.page = NationSelectionScreen('http://localhost:5000', 'Steve')
        return self.page


if __name__ == "__main__":
    ns = NationSelectorApp()
    ns.run()
