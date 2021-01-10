from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics.vertex_instructions import (Rectangle,
                                               Ellipse,
                                               Line)
from kivy.graphics.context_instructions import Color
from kivy.clock import Clock

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
                 'Sitifensis': (645, 1359)}

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
        res = super(Spotter, self).on_touch_up(touch)
        if self.collide_point(*touch.pos):
            map_pos = window_to_map(self.parent.pos)
            print(f"{map_pos[0]:.1f},{map_pos[1]:.1f}")
            if touch.is_double_tap:
                territory, snap_pos = get_snap_pos(self.parent.pos)
                self.parent.pos = snap_pos
                print(f"Snapping to {territory}")
        return res 

class AstTokenWidget(Label):
    ast = NumericProperty(0)
    track = NumericProperty(0)
    color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super(AstTokenWidget, self).__init__(**kwargs)
        Clock.schedule_once(self.init_bindings, 0)

    def init_bindings(self, *args):
        self.parent.parent.bind(size=self.update_size)        

    def get_window_pos(self):
        print('get window pos')
        map_pos = (202 + self.ast*60, 22 + self.track*60)
        return map_to_window(map_pos)

    def get_window_size(self):
        app = App.get_running_app()
        if not app.root:
            return (58,58)
        map_widget = app.root.ids['map']
        return (58/4058.0*map_widget.size[0], 58/2910.0*map_widget.size[1])
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.ast += 1
            if self.ast > 15:
                self.ast = 1

    def on_track(self, instance, pos):
        self.pos = self.get_window_pos()

    def on_ast(self, instance, pos):
        self.pos = self.get_window_pos()    

    def update_size(self, instance, size):
        app = App.get_running_app()
        map_widget = app.root.ids['map']
        self.size = (60/4058.0*map_widget.size[0], 60/2910.0*map_widget.size[1])
        self.pos = self.get_window_pos()
    


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
    def build(self):
        return AdvCivWidget()

if __name__ == "__main__":
    civmap = AdvCivApp()
    civmap.run()
