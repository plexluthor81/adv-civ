from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.behaviors import DragBehavior
from kivy.lang import Builder
from kivy.uix.scatter import Scatter
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.clock import Clock

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

<UnitToken>:
    # Define the properties for the DragLabel
    drag_rectangle: self.x, self.y, self.width, self.height
    drag_timeout: 10000000
    drag_distance: 0
    canvas.before:
        Color:
            rgba: tuple([x/255 for x in root.nation_color] + [.8])
        Rectangle:
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
                # Define the root widget
                UnitToken:
                    size_hint: 0.25, 0.2
                    text: 'Drag me'
                UnitToken:
                    id: smaller
                    size_hint: 60/4058, 60/2910
                    text: 'Smaller'
                    pos: (300,300)
'''

map_locations = {'Great Erg': (680, 965),
                 'Western Gaetulia': (1222, 931),
                 'Garamantes': (1613, 897),
                 'Leptis Magna': (1541, 1114),
                 'Libya': (1256, 1137),
                 'Numidia': (1018, 1195),
                 'Thapsos': (1193, 1340),
                 'Carthage': (1174, 1515),
                 'Hippo Regius': (1021, 1452),
                 'Cirta': (856, 1397),
                 'Sitifensis': (645, 1359),
                 'Caesariensis': (423, 1288),
                 'Mauretania': (146, 1258),
                 'Tingitana': (58, 948),
                 'Stock': (1768, 535)}

def pos_to_hint(pos, dims=(4058.0, 2910.0)):
    return {'x':pos[0]/dims[0], 'y':pos[1]/dims[1]}

def size_to_hint(size, dims=(4058.0, 2910.0)):
    return (size[0]/dims[0], size[1]/dims[1])

def map_to_window(map_pos, window_size):
    hint = pos_to_hint(map_pos)
    return (hint['x']*window_size[0], hint['y']*window_size[1])

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

class UnitToken(DragBehavior, Label):
    stock = ListProperty(pos_to_hint(map_locations['Stock']))
    nation_color = ListProperty([0,0,0])

    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.pos_hint = {}
        return super(UnitToken, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.pos_hint = pos_to_hint(self.pos, self.parent.size)
        return super(UnitToken, self).on_touch_up(touch)

class AstTokenWidget(Label):
    ast = NumericProperty(0)
    track = NumericProperty(0)
    color = ListProperty([0, 0, 0, 1])
    target_size = 48

    def refresh_pos(self):
        self.pos_hint['x'] = (208 + self.ast*60)/4058.0
        self.pos_hint['y'] = (28 + self.track*60)/2910.0   
        if self.parent:     
            self.parent._trigger_layout()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print("AST")
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
    tokens = []

    def __init__(self, name, color, track, fl, num_units=55, **kwargs):
        self.name = name
        self.color = color
        self.track = track
        self.fl = fl
        self.num_units = num_units
        for location in map_locations.keys():
            self.units_in_location[location] = 0

        self.ast_token = AstTokenWidget(text=self.name[0].upper(),
                                        ast=0,
                                        track=self.track,
                                        color=self.color)
        fl.add_widget(self.ast_token)
                                        
        for i in range(num_units):
            token = UnitToken(nation_color=self.color, 
                              pos_hint=pos_to_hint(map_locations['Stock']),
                              size_hint=size_to_hint((60,60)))
            self.fl.add_widget(token)
            self.units_in_location['Stock'] += 1
            self.tokens.append(token)

    def update_locations(self, *args):
        print(f'Should be updating locations for {self.name}')


class TestApp(App):
    def build(self):
        root = Builder.load_string(kv)
        fl = root.ids['fl']
        fl._trigger_layout()
        ms = root.ids['ms']
        fl.add_widget(UnitToken(size_hint=size_to_hint((80,80)),
                                pos_hint=pos_to_hint(map_locations['Stock']),
                                text="Some big long phrase"))
        africa = Nation('Africa', [186, 96, 41], 9, fl, 1)
        return root

TestApp().run()
