from kivy.uix.scatter import Scatter
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout

civ_map_kv = '''
<CivMapScreen>:
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
'''


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


class CivMapScreen(FloatLayout):
    def __init__(self, **kwargs):
        Builder.load_string(civ_map_kv)
        super(CivMapScreen, self).__init__(**kwargs)


class CivMapApp(App):
    def build(self):
        root = CivMapScreen()
        return root


if __name__ == "__main__":
    CivMapApp().run()
