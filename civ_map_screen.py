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
from kivy.properties import StringProperty
from kivy.uix.button import Button


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
        if 'text' in kwargs:
            print(kwargs['text'])
        super(StockBox, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        self.bind(size=self.setter('text_size'))
        self.font_size = 12
        self.halign = 'center'
        self.markup = True
        self.valign = 'top'
        self.color = (0, 0, 0, 1)
        self.bind(size=self.draw_rect)
        self.bind(pos=self.draw_rect)
        print(self.text)
        print(self.font_size)
        print(self.color)
        print(self.pos, self.size)

    def draw_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(.1, .1, .1, 1)
            Line(width=1.5, rectangle=[self.x, self.y, self.width, self.height])


class StockLabel(Label):
    def __init__(self, **kwargs):
        super(StockLabel, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        self.font_size = 10
        self.halign = 'left'
        self.markup = True
        self.valign = 'center'
        self.color = (0, 0, 0, 1)
        self.size_hint = (.1, .1)


class StockPanel(FloatLayout):
    nation = StringProperty('Nation')

    def __init__(self, **kwargs):
        super(StockPanel, self).__init__(**kwargs)
        self.lab = Label(color=(0, 0, 0, 1), text=self.nation)
        self.lrect = None
        self.nation = 'Nation'
        self.bind(nation=self.lab.setter('text'))
        self.add_widget(self.lab)
        self.lab.bind(size=self.draw_lrect)
        self.ccc_btn = Button(text='Civ Card Credits', font_size=10, size_hint=(.19, .14), pos_hint={'x': 0.04, 'top': 0.18})
        self.add_widget(self.ccc_btn)
        print('Adding Stock StockBox')
        self.add_widget(StockBox(text="Stock", size_hint=(0.17, 0.44), pos_hint={'x': 0.05, 'top': 0.95}))
        print('Done Adding Stock StockBox')
        self.add_widget(StockLabel(text="Units", pos_hint={'x': 0.12, 'y': 0.75}))
        self.add_widget(StockLabel(text="Cities", pos_hint={'x': 0.12, 'y': 0.65}))
        self.add_widget(StockLabel(text="Ships", pos_hint={'x': 0.12, 'y': 0.55}))
        self.add_widget(StockBox(text="Treasury", size_hint=(0.17, 0.24), pos_hint={'x': 0.05, 'top': 0.45}))

    def draw_lrect(self, *args):
        self.lab.canvas.before.clear()
        with self.lab.canvas.before:
            Color(248/255, 212/255, 128/255, 1)
            self.lrect = Rectangle(pos=(0, 0), size=self.lab.size)


class CivCardCreditsPanel(FloatLayout):
    def __init__(self, **kwargs):
        super(CivCardCreditsPanel, self).__init__(**kwargs)
        self.add_widget(Image(source='civ_credits.png', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1)))
        self.st_btn = Button(size_hint=(0.3, 0.3), pos_hint={'center_x': .5, 'center_y': .5}, text="Stock and Treasury")
        self.add_widget(self.st_btn)


class CivMapScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(CivMapScreen, self).__init__(**kwargs)
        self.pos = (0, 0)
        self.nations = []
        self.ms = MapScatter(pos_hint={'x': 0, 'y': 0})
        self.add_widget(self.ms)
        self.im = Image(source='civ_board.png', allow_stretch=True, keep_ratio=False, opacity=1.0)
        self.ms.add_widget(self.im)
        self.fl = FloatLayout(size=self.im.size, pos_hint={'x': 0, 'y': 0})
        self.ms.bind(size=self.fl.setter('size'))
        self.im.add_widget(self.fl)
        self.bind(size=self.im.setter('size'))

        self.sm = ScreenManager(pos_hint={'x': 1660/4058.0, 'y': 3/2910.0}, size_hint=((3367-1660)/4058.0, (2907-2105)/2910.0))
        self.fl.add_widget(self.sm)

        self.st = StockPanel(pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))
        self.st.ccc_btn.bind(on_press=self.change_screen)
        self.sm.bind(size=self.st.lab.setter('size'))
        screen = Screen(name="Stock and Treasury", pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))
        screen.add_widget(self.st)
        self.sm.add_widget(screen)

        self.ccc = CivCardCreditsPanel(pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))
        self.ccc.st_btn.bind(on_press=self.change_screen)
        screen = Screen(name='Civ Card Credits', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))
        screen.add_widget(self.ccc)
        self.sm.add_widget(screen)

    def change_screen(self, instance, *args):
        if instance == self.st.ccc_btn:
            self.sm.current = 'Civ Card Credits'
        elif instance == self.ccc.st_btn:
            self.sm.current = 'Stock and Treasury'
        for obj in [self, self.sm, self.st, self.st.lab]:
            print(obj, obj.pos, obj.pos_hint, obj.size, obj.size_hint)

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
