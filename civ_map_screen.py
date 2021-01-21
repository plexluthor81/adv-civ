from kivy.uix.scatter import Scatter
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from tokens import AstToken
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock


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
            self.pos = (0, 0)
        if touch.is_mouse_scrolling:
            old_pos = self.pos
            old_scale = self.scale
            if touch.button == 'scrolldown':
                self.scale = min(self.scale*1.1, 4)
            if touch.button == 'scrollup':
                self.scale = max(self.scale*.9, 1)

            new_pos = tuple(map(lambda i, j: i*(1-(self.scale/old_scale)) + j*(self.scale/old_scale), touch.pos, old_pos))
            self.pos = new_pos
            self.on_transform_with_touch(touch)

        return super(MapScatter, self).on_touch_down(touch)


class CivMapScreen(BoxLayout):
    nations = []
    ms = None
    im = None
    fl = None

    def __init__(self, **kwargs):
        super(CivMapScreen, self).__init__(**kwargs)
        self.pos = (0, 0)
        self.ms = MapScatter(pos_hint={'x': 0, 'y': 0})
        self.add_widget(self.ms)
        self.im = Image(source='civ_board.png', allow_stretch=True, keep_ratio=False, opacity=1.0)
        self.ms.add_widget(self.im)
        self.fl = FloatLayout(size=self.im.size, pos_hint={'x': 0, 'y': 0})
        self.ms.bind(size=self.fl.setter('size'))
        self.im.add_widget(self.fl)
        self.bind(size=self.im.setter('size'))

    def add_spotter(self, spotter):
        print(f'Adding {spotter} to {self.fl}')
        self.fl.add_widget(spotter)


class CivMapApp(App):
    def build(self):
        root = CivMapScreen(pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))
        ast_token = AstToken(ast=0, track=9, color=[186, 96, 41], size_hint=(50 / 4058.0, 50 / 2910.0))
        root.add_spotter(ast_token)
        return root


if __name__ == "__main__":
    CivMapApp().run()
