from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty

from contextlib import suppress

kv = '''

<NationDropDown>:
    Button:
        id: btn
        text: 'Not Selected'
        size_hint: (.5, .8)
        pos_hint: {'x': 0, 'center_y': .5}
        on_release: dropdown.open(self)
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
       

FloatLayout:
    Label:
        text: "Nation Selection"
        font_size: 25
        size_hint: (.5, .15)
        pos_hint: {'center_x': .5, 'center_y': .9}
    PlayerRow:
        id: pr
        player_num: 1
        player_name: 'Steve'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .75}
    PlayerRow:
        player_num: 2
        player_name: 'Ren'
        size_hint: (1, .1)
        pos_hint: {'x': 0, 'y': .65}
    PlayerRow:
        player_num: 3
        player_name: 'Kyle'
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
        App.get_running_app().show_stuff()

    def update(self):
        root = App.get_running_app().root
        print(root.children)
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
        print(selected_nations)
    
        with suppress(ValueError):
            selected_nations.remove(self.ids['btn'].text)
            selected_nations.remove('Not Selected')

        print(self.ids)
        print(self.ids['dropdown'].ids)

        self.ids['btn_africa'].disabled = 'Africa' in selected_nations
        self.ids['btn_italy'].disabled = 'Italy' in selected_nations
        self.ids['btn_illyria'].disabled = 'Illyria' in selected_nations
        self.ids['btn_thrace'].disabled = 'Thrace' in selected_nations
        self.ids['btn_crete'].disabled = 'Crete' in selected_nations
        self.ids['btn_asia'].disabled = 'Asia' in selected_nations
        self.ids['btn_assyria'].disabled = 'Assyria' in selected_nations
        self.ids['btn_babylon'].disabled = 'Bablyon' in selected_nations
        self.ids['btn_egypt'].disabled = 'Egypt' in selected_nations


class PlayerRow(FloatLayout):
    player_num = NumericProperty(-1)
    player_name = StringProperty('Player Name')
        

class NationSelectorApp(App):
    def update_buttons(self):
        pass

    def show_stuff(self, root=None):
        if not root:
            root = self.root
        pr = root.ids['pr']
        lnum = pr.ids['lnum']
        lname = pr.ids['lname']
        ndd = pr.ids['ndd']
        btn = ndd.ids['btn']
        dd = ndd.ids['dropdown']
        
        print('pr', pr.size, pr.pos)
        print('lnum', lnum.size, lnum.pos)
        print('lname', lname.size, lname.pos)
        print('ndd', ndd.size, ndd.pos)
        print('btn', btn.size, btn.pos)
        print('dd', dd.size, dd.pos)

    def build(self):
        root = Builder.load_string(kv)   
        self.show_stuff(root)
        return root

NationSelectorApp().run()

        
