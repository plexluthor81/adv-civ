from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.behaviors import DragBehavior
from kivy.lang import Builder
from kivy.uix.scatter import Scatter
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.graphics.vertex_instructions import Rectangle, Ellipse
from kivy.graphics.context_instructions import Color

from math import sqrt

# You could also put the following in your kv file...
kv = '''
<AstTokenWidget>:
    size_hint: (root.target_size/4058.0,root.target_size/2910.0)
    pos_hint: {'x': (208 + self.ast*60)/4058.0, 'y': (28 + self.track*60)/2910.0}
    canvas:
        Color:
            rgba: tuple([x/255 for x in self.color] + [.99])
        Rectangle:
            pos: self.pos
            size: self.size
<Token>:
    active_nation: app.active_nation
    # Define the properties for the DragLabel
    drag_rectangle: self.x, self.y, self.width, self.height
    drag_timeout: 10000000
    drag_distance: 0
    color: (0,0,0)

<UnitToken>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: root.nation.unit_icon if root.nation else 'default_unit.png'

<CityToken>:
    canvas.before:
        Color:
            rgba: tuple([x/255 for x in root.nation.color] + [.8]) if root.nation else (.5,.5,.5,.8)
        Ellipse:
            pos: self.pos
            size: self.size

BoxLayout:
    MapScatter:
        id: ms
        Image:
            source: 'civ_board.png'
            allow_stretch: True
			keep_ratio: False
			size: root.size
            FloatLayout:
                id: fl
                size: ms.size
                ScreenManager:
                    id: sm
                    pos_hint: {'x': 1660/4058.0, 'y': 3/2910.0}
                    size_hint: (3367-1660)/4058.0,(2907-2105)/2910.0
                    Screen:
                        name: 'Stock and Treasury'
                        FloatLayout:
                            Label:
                                text: "Units"
                                color: (0,0,0,1)
                                size_hint: .2,.2
                                canvas.before:
                                    Color:
                                        rgba: (0,0,0,1)
                                    Line:
                                        rectangle: (self.x, self.y, self.width, self.height)
                            Label:
                                color: (0, 0, 0, 1)
                                text: app.active_nation
                                canvas.before:
                                    Color: 
                                        rgba: app.rgba_tuple((248, 212, 128), 1)
                                    Rectangle:
                                        pos: (0, 0)
                                        size: sm.size
                            Button:
                                size_hint: .3, .3
                                pos_hint: {'center_x': .5, 'center_y': .5}
                                on_press: app.change_screen("Civ Card Credits")
                                text: 'Civ Card Credits'
                    Screen:
                        name: "Civ Card Credits"
                        FloatLayout:
                            size: sm.size
                            Image:
                                size_hint: 1,1
                                source: 'civ_credits.png'
                            Button:
                                size_hint: .3, .3
                                pos_hint: {'center_x': .5, 'center_y': .5}
                                on_press: app.change_screen("Stock and Treasury")
                                text: 'Stock and Treasury'
                            
                    
'''

class SnapMap():
    map_locations = {'Great Erg': {'pop_limit': 1, 'nations': None, 'Prime': (680, 965), 'Alt': []},
                     'Western Gaetulia': {'pop_limit': 1, 'nations': None, 'Prime': (1222, 931), 'Alt': []},
                     'Garamantes': {'pop_limit': 1, 'nations': None, 'Prime': (1613, 897), 'Alt': []},
                     'Leptis Magna': {'pop_limit': 1, 'nations': None, 'Prime': (1541, 1114), 'Alt': []},
                     'Libya': {'pop_limit': 1, 'nations': None, 'Prime': (1256, 1137), 'Alt': []},
                     'Numidia': {'pop_limit': 1, 'nations': None, 'Prime': (1018, 1195), 'Alt': []},
                     'Thapsos': {'pop_limit': 1, 'nations': None, 'Prime': (1193, 1340), 'Alt': []},
                     'Carthage': {'pop_limit': 1, 'nations': None, 'Prime': (1174, 1515), 'Alt': []},
                     'Hippo Regius': {'pop_limit': 1, 'nations': None, 'Prime': (1021, 1452), 'Alt': []},
                     'Cirta': {'pop_limit': 1, 'nations': None, 'Prime': (856, 1397), 'Alt': []},
                     'Sitifensis': {'pop_limit': 1, 'nations': None, 'Prime': (645, 1359), 'Alt': []},
                     'Caesariensis': {'pop_limit': 1, 'nations': None, 'Prime': (423, 1288), 'Alt': []},
                     'Mauretania': {'pop_limit': 1, 'nations': None, 'Prime': (146, 1258), 'Alt': []},
                     'Tingitana': {'pop_limit': 1, 'nations': None, 'Prime': (58, 948), 'Alt': []},
                     'Stock': {'pop_limit': 55, 'nations': None, 'Prime': (1768, 535), 'Alt': []},
                     'CityStock': {'pop_limit': 9, 'nations': None, 'Prime': (1768, 435), 'Alt': []},
                     'BoatStock': {'pop_limit': 4, 'nations': None, 'Prime': (1768, 335), 'Alt': []},
                     'Treasury': {'pop_limit': 55, 'nations': None, 'Prime': (1768, 235), 'Alt': []},
                     'HiddenStock': {'pop_limit': 55, 'nations': None, 'Prime': (1768, -535), 'Alt': []},
                     'HiddenCityStock': {'pop_limit': 9, 'nations': None, 'Prime': (1768, -435), 'Alt': []},
                     'HiddenBoatStock': {'pop_limit': 4, 'nations': None, 'Prime': (1768, -335), 'Alt': []},
                     'HiddenTreasury': {'pop_limit': 55, 'nations': None, 'Prime': (1768, -235), 'Alt': []} }

    def get_snap_pos(self, window_pos, type='Token'):
        pos = window_to_map(window_pos)
        territory = min(self.map_locations.keys(), key=lambda t: abs(sqrt((self.map_locations[t]['Prime'][0]-pos[0])**2 + (self.map_locations[t]['Prime'][1]-pos[1])**2)))
        if type=='Token' and territory in ['CityStock','BoatStock']:
            territory = 'Stock'
        if type=='City' and territory in ['Stock', 'BoatStock', 'Treasury']:
            territory = 'CityStock'
        if type=='Boat' and territory in ['Stock', 'Treasury', 'CityStock']:
            territory = 'BoatStock'
        map_pos = self.map_locations[territory]['Prime']
        return territory, map_to_window(map_pos)
   

snap_map = SnapMap()

def pos_to_hint(pos, dims=(4058.0, 2910.0)):
    return {'x':pos[0]/dims[0], 'y':pos[1]/dims[1]}

def size_to_hint(size, dims=(4058.0, 2910.0)):
    return (size[0]/dims[0], size[1]/dims[1])

def map_to_window(map_pos, window_size=None, map_size=(4058.0, 2910.0)):
    if window_size is None:
        window_size = App.get_running_app().root.ids['ms'].size
    hint = pos_to_hint(map_pos, map_size)
    return (hint['x']*window_size[0], hint['y']*window_size[1])

def window_to_map(window_pos):
    return map_to_window(window_pos, (4058.0, 2910.0), App.get_running_app().root.ids['ms'].size)
    

class NationButton(Button):
    def on_press(self):
        app = App.get_running_app()
        old_an = app.active_nation
        app.active_nation = self.text
        for n in app.nations:
            n.show_or_hide_stock()
        print(f"{old_an}->{app.active_nation}")

class MapScatter(Scatter):
    def on_transform_with_touch(self, touch):
        if self.pos[0] > 0:
            self.pos = (0, self.pos[1])
        if self.pos[0] < self.size[0]*(1-self.scale):
            self.pos = (self.size[0]*(1-self.scale), self.pos[1])
        if self.pos[1] > 0:
            self.pos = (self.pos[0], 0)
        if self.pos[1] < self.size[1]*(1-self.scale):
            self.pos = (self.pos[0], self.size[1]*(1-self.scale))

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.scale = 1
            self.pos = (0,0)
        if touch.is_mouse_scrolling:
            old_pos = self.pos
            old_scale = self.scale
            if touch.button == 'scrolldown':
                self.scale = min(self.scale*1.1, 4)
            if touch.button == 'scrollup':
                self.scale = max(self.scale*.9, 1)

            new_pos = tuple(map(lambda i,j: i*(1-(self.scale/old_scale)) + j*(self.scale/old_scale), touch.pos, old_pos))
            self.pos = new_pos
            self.on_transform_with_touch(touch)

        return super(MapScatter, self).on_touch_down(touch)

class Token(DragBehavior, Label):
    nation = ObjectProperty(None)
    active_nation = StringProperty('')
    hidden = False
    territory = StringProperty('')

    def __init__(self, nation=None, hidden=False, territory='', **kwargs):
        super(Token, self).__init__(**kwargs)
        self.nation = nation
        self.hidden = hidden
        self.territory = territory
    
    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos) and self.nation.name==self.active_nation:
            self.pos_hint = {}
            self.territory = 'Moving'
            self.nation.label_tokens()
        return super(Token, self).on_touch_down(touch)

    def goto_territory(self, territory):
        self.territory = territory
        self.pos = map_to_window(snap_map.map_locations[territory]['Prime'])
        self.pos_hint = pos_to_hint(self.pos, self.parent.size)

    def hide(self):
        if self.hidden:
            return
        self.hidden = True
        if self.territory == 'Stock':
            self.goto_territory('HiddenStock')
        if self.territory == 'CityStock':
            self.goto_territory('HiddenCityStock')
        if self.territory == 'BoatStock':
            self.goto_territory('HiddenBoatStock')
        if self.territory == 'Treasury':
            self.goto_territory('HiddenTreasury')

    def show(self):
        if not self.hidden:
            return
        self.hidden = False
        if self.territory == 'HiddenStock':
            self.goto_territory('Stock')
        if self.territory == 'HiddenCityStock':
            self.goto_territory('CityStock')
        if self.territory == 'HiddenBoatStock':
            self.goto_territory('BoatStock')
        if self.territory == 'HiddenTreasury':
            self.goto_territory('Treasury')

class UnitToken(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            snap_ter, snap_pos = snap_map.get_snap_pos(self.pos)
            self.territory = snap_ter
            self.pos = snap_pos
            self.pos_hint = pos_to_hint(self.pos, self.parent.size)
            self.nation.label_tokens()
        return super(UnitToken, self).on_touch_up(touch)

class CityToken(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            snap_ter, snap_pos = snap_map.get_snap_pos(self.pos, 'City')
            self.territory = snap_ter
            self.pos = snap_pos
            self.pos_hint = pos_to_hint(self.pos, self.parent.size)
            self.nation.build_city(snap_ter)
        return super(CityToken, self).on_touch_up(touch)

class AstTokenWidget(Label):
    ast = NumericProperty(0)
    track = NumericProperty(0)
    color = ListProperty([0, 0, 0])
    target_size = 48

    def __init__(self, ast=0, track=0, color=[0,0,0], **kwargs):
        super(AstTokenWidget, self).__init__(**kwargs)
        self.ast = ast
        self.track = track
        self.color = color

    def refresh_pos(self):
        self.pos_hint['x'] = (208 + self.ast*60)/4058.0
        self.pos_hint['y'] = (28 + self.track*60)/2910.0   
        if self.parent:     
            self.parent._trigger_layout()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.ast += 1
            if self.ast > 15:
                self.ast = 1

    def on_track(self, instance, pos):
        self.refresh_pos()

    def on_ast(self, instance, pos):
        self.refresh_pos()

class Nation:
    num_units = 55
    name = 'Unnamed'
    color = [0, 0, 0]
    track = 0
    fl = None
    units_in_location = {}
    unit_icon = 'default_unit_icon.png'

    def __init__(self, name, color, track, fl, unit_icon, num_units=55, **kwargs):
        self.name = name
        self.color = color
        self.track = track
        self.fl = fl
        self.num_units = num_units
        self.unit_icon = unit_icon
        for location in snap_map.map_locations.keys():
            self.units_in_location[location] = 0

        self.ast_token = AstTokenWidget(ast=0,
                                        track=self.track,
                                        color=self.color)
        fl.add_widget(self.ast_token)

        self.nation_button = NationButton(size_hint=(180.0/4058.0, 60.0/2910.0),
                                          pos_hint={'x': 19.0/4058.0, 'y': (22.0+self.track*60.0)/2910.0},
                                          text=self.name,
                                          color=(0,0,0,.01),
                                          background_color=(0,0,0,.01))
        fl.add_widget(self.nation_button)
                           
        self.tokens = []             
        for i in range(num_units):
            token = UnitToken(nation=self, hidden=True, territory='HiddenStock',
                              pos_hint=pos_to_hint(snap_map.map_locations['HiddenStock']['Prime']),
                              size_hint=size_to_hint((60,60)))
            self.fl.add_widget(token)
            self.units_in_location['HiddenStock'] += 1
            self.tokens.append(token)

        for i in range(9):
            city = CityToken(nation=self, hidden=True, territory='HiddenCityStock',
                             size_hint=size_to_hint((60,60)),
                             pos_hint=pos_to_hint(snap_map.map_locations['HiddenCityStock']['Prime']))
            self.fl.add_widget(city)
            self.units_in_location['HiddenCityStock'] += 1
            self.tokens.append(city)
        self.label_tokens()
                             

    def update_locations(self, *args):
        print(f'Should be updating locations for {self.name}')

    def label_tokens(self):
        units_in_location = {}
        for token in self.tokens:
            if token.territory in units_in_location.keys():
                units_in_location[token.territory] += 1
            else:
                units_in_location[token.territory] = 1
        for token in self.tokens:
            if units_in_location[token.territory] > 1:
                token.text = str(units_in_location[token.territory])
            else:
                token.text = ''
        self.units_in_location = units_in_location

    def build_city(self, territory):
        for token in self.tokens:
            if isinstance(token, UnitToken) and token.territory == territory:
                token.goto_territory('Stock')
                
        self.label_tokens()

    def show_or_hide_stock(self):
        active_nation = App.get_running_app().active_nation
        if active_nation == self.name: 
            print(f'Showing tokens in {self.name}, active_nation={active_nation}')           
            for token in self.tokens:
                if token.territory in ['HiddenStock', 'HiddenCityStock', 'HiddenBoatStock', 'HiddenTreasury']:
                    token.show()
        else:
            print(f'Hiding tokens in {self.name}, active_nation={active_nation}')
            for token in self.tokens:
                if token.territory in ['Stock', 'CityStock', 'BoatStock', 'Treasury']:
                    token.hide()


class TestApp(App):
    active_nation = StringProperty("")
    last_active_nation = ""
    nations = ListProperty([])

    def rgba_tuple(self, rgb, a):
        return tuple([x/255 for x in rgb] + [a])

    def change_screen(self, new_screen):
        if self.active_nation:
            self.last_active_nation = self.active_nation
            self.active_nation = ""
            for n in self.nations:
                n.show_or_hide_stock()
        elif new_screen == "Stock and Treasury":
            self.active_nation = self.last_active_nation
            for n in self.nations:
                n.show_or_hide_stock()

        self.root.ids['sm'].current = new_screen

    def build(self):
        root = Builder.load_string(kv)
        fl = root.ids['fl']
        self.nations.append(Nation('Africa', [186, 96, 41], 9, fl, 'africa_token_icon3.png', 5))
        self.nations.append(Nation('Italy', [252, 0, 0], 8, fl, 'africa_token_icon3.png', 5))
        return root

TestApp().run()
