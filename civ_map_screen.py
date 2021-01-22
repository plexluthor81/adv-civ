from kivy.uix.scatter import Scatter
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from tokens import AstToken
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager

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


class StockBox(Label):
    def __init__(self, **kwargs):
        super(StockBox, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        self.font_size = 12
        self.halign = 'center'
        self.markup = True
        self.valign = 'top'
        self.color = (0,0,0,1)
        self.bind(size=self.draw_rect)

    def draw_rect(self, *args):
        with self.canvas:
            Color(.1, .1, .1, 1)
            Line(width=1.5, rectangle=[self.x, self,y, self.width, self.height])

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

        self.sm = ScreenManager()
        self.fl.add_widget(self.sm)

        self.fl.add_widget(StockBox())

'''
<StockBox@Label>:
    text_size: self.size
    font_size: 12
    halign: 'center'
    markup: True
    valign: 'top'
    color: (0,0,0)
    canvas:
        Color:
            rgba: .1, .1, .1, 1
        Line:
            width: 1.5
            rectangle: (self.x, self.y, self.width, self.height)

<StockLabel@Label>:
    text_size: self.size
    font_size: 10
    halign: 'left'
    markup: True
    valign: 'center'
    color: (0,0,0)
    size_hint: .1, .1

ScreenManager:
                    id: sm
                    pos_hint: {'x': 1660/4058.0, 'y': 3/2910.0}
                    size_hint: (3367-1660)/4058.0,(2907-2105)/2910.0
                    Screen:
                        name: 'Stock and Treasury'
                        FloatLayout:
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
                                size_hint: .19, .14
                                pos_hint: {'x': .04, 'top': .18}
                                on_press: app.change_screen("Civ Card Credits")
                                text: 'Civ Card Credits'
                                font_size: 10
                            StockBox:
                                text: "Stock"
                                size_hint: .17, .44
                                pos_hint: {'x':.05,'top':.95}
                            StockLabel:
                                text: "Units"
                                pos_hint: {'x': .12, 'y': .75}
                            StockLabel:
                                text: "Cities"
                                pos_hint: {'x': .12, 'y': .65}
                            StockLabel:
                                text: "Ships"
                                pos_hint: {'x': .12, 'y': .55}
                            StockBox:
                                text: "Treasury"
                                size_hint: .17, .24
                                pos_hint: {'x':.05,'top':.45}
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
