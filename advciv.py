from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.graphics.vertex_instructions import (Rectangle,
                                               Ellipse,
                                               Line)
from kivy.graphics.context_instructions import Color
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.behaviors import DragBehavior

from math import sqrt

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

class UnitWidget(DragBehavior, Label):
    nation_color = ListProperty([0,0,0])

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            print(f'I moved to {self.pos}')
        return super(DragBehavior, self).on_touch_up(touch)


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

        for i in range(num_units):
            token = UnitWidget(nation_color=self.color, 
                               pos=(map_locations['Stock'][0]/4058.0,
                                    map_locations['Stock'][1]/2910.0),
                               size_hint=(60/4058.0, 60/2910.0))
            self.fl.add_widget(token)
            self.units_in_location['Stock'] += 1
            self.tokens.append(token)
            #token.bind(pos=self.update_locations)

    def update_locations(self, *args):
        print(f'Should be updating locations for {self.name}')

        

def map_to_window(map_pos):
    app = App.get_running_app()
    if not app.root:
        return (0,0)
    map_widget = app.root.ids['map']
    window_pos = (map_widget.size[0]/4058.0*map_pos[0], map_widget.size[1]/2910.0*map_pos[1])
    return window_pos

def window_to_map(window_pos):
    app = App.get_running_app()
    map_widget = app.root.ids['map']
    map_pos = (4058.0/map_widget.size[0]*window_pos[0], 2910.0/map_widget.size[1]*window_pos[1])
    return map_pos

def get_snap_pos(window_pos):
    pos = window_to_map(window_pos)
    territory, map_pos = min(map_locations.items(), key=lambda t: abs(sqrt((t[1][0]-pos[0])**2 + (t[1][1]-pos[1])**2)))
    return territory, map_to_window(map_pos)

class Spotter(Label):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            map_pos = window_to_map(self.parent.pos)
            print(f"{map_pos[0]:.1f},{map_pos[1]:.1f}")
            if touch.is_double_tap:
                territory, snap_pos = get_snap_pos(self.parent.pos)
                self.parent.pos = snap_pos
                print(f"Snapping to {territory}")
                return True
        return super(Spotter, self).on_touch_up(touch) 

class AstTokenWidget(Label):
    ast = NumericProperty(0)
    track = NumericProperty(0)
    color = ListProperty([0, 0, 0, 1])
    target_size = 48

    def refresh_pos(self):
        self.pos_hint['x'] = (208 + self.ast*60)/4058.0
        self.pos_hint['y'] = (28 + self.track*60)/2910.0        
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

    
class NationButton(Button):
    def on_press(self):
        app = App.get_running_app()
        old_an = app.active_nation
        app.active_nation = self.text
        print(f"{old_an}->{app.active_nation}")

class TurnOrderScreen(Screen):
    def __init__(self, **kwargs):
        super(TurnOrderScreen, self).__init__(**kwargs)
        self.name = 'Turn Order'
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, *args):
        gl = GridLayout(cols=3)
        print(gl.size)
        self.stock_label = Label(width=self.parent.size[0]/3,height=self.parent.size[1],valign='top',halign='center',text="Stock")
        self.stock_label.text_size = self.stock_label.size
        phase_label = Label(font_size=8, markup=True,text="""[b][size=10]Phase Descriptions[/size][/b]
1. Collect Taxes
2. Population Expanstion
3. Census
4. Build Ships
5. Movement
6. Conflict
7. Build Cities
8. Remove Surplus Population
9. Acquire Trade Cards
10. Trade
11. Resolve Calamities
12. Acquire Civ Cards
13. Alter AST""")
        treas_label = Label(text="Treasury")
        gl.add_widget(self.stock_label)
        gl.add_widget(phase_label)
        gl.add_widget(treas_label)
        print(gl.size)
        print(self.size)
        with gl.canvas.before:
            Color(.7, .7, .7, 1)
            Rectangle(pos=(0,0), size=self.parent.size)
        with self.stock_label.canvas.before:
            Color(.3, .3, .3, 1)
            Rectangle(pos=self.stock_label.pos, size=self.stock_label.size)
        self.add_widget(gl)

    def on_touch_down(self, touch):
        if self.stock_label.collide_point(*touch.pos):
            print("You poked stock")

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


class AdvCivWidget(BoxLayout):
    def on_touch_down(self, touch):        
        map_scatter = self.ids['map_scatter']
        if touch.is_double_tap:
            map_scatter.scale = 1
            map_scatter.pos = (0,0)
        if touch.is_mouse_scrolling:
            old_pos = map_scatter.pos
            old_scale = map_scatter.scale
            if touch.button == 'scrolldown':
                map_scatter.scale = min(map_scatter.scale*1.1, 4)
            if touch.button == 'scrollup':
                map_scatter.scale = max(map_scatter.scale*.9, 1)

            new_pos = tuple(map(lambda i,j: i*(1-(map_scatter.scale/old_scale)) + j*(map_scatter.scale/old_scale), touch.pos, old_pos))
            map_scatter.pos = new_pos
            map_scatter.on_transform_with_touch(touch)

        return super(AdvCivWidget, self).on_touch_down(touch)


class AdvCivApp(App):
    active_nation = StringProperty("Not Set")

    def rgba_tuple(self, rgb, a):
        return tuple([x/255 for x in rgb] + [a])

    def build(self):
        acw = AdvCivWidget()
        fl = acw.ids['fl']
        africa = Nation('Africa', [186, 96, 41], 9, fl, 1)
        return acw

if __name__ == "__main__":
    civmap = AdvCivApp()
    civmap.run()
