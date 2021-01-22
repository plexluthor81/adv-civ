from kivy.uix.behaviors import DragBehavior
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle, Ellipse


class Token(DragBehavior, Label):
    nation = ObjectProperty(None, allownone=True)
    active_nation = StringProperty('')
    color = ListProperty([0, 0, 0, 1])
    territory = ObjectProperty(None, allownone=True)

    def __init__(self, nation=None, hidden=False, territory=None, moving=False, token_color=[255, 255, 255], icon='', **kwargs):
        super(Token, self).__init__(**kwargs)
        self.nation = nation
        self.active_nation = ''
        self.hidden = hidden
        self.moving = moving
        self.color = [0, 0, 0, 1]
        self.rect = None
        self.drag_height = self.height
        self.bind(height=self.setter('drag_rect_height'))
        self.drag_width = self.width
        self.bind(width=self.setter('drag_rect_width'))
        self.drag_x = self.x
        self.bind(x=self.setter('drag_rect_x'))
        self.drag_y = self.y
        self.bind(y=self.setter('drag_rect_y'))
        self.drag_timeout = 10000000
        self.drag_distance = 0
        self.draw_rect(token_color, icon)

        self.territory = None
        if territory:
            self.goto_territory(territory)

    def draw_rect(self, token_color, icon):
        canvas_color = [x / 255 for x in token_color] + [.99]
        if not icon:
            with self.canvas.before:
                Color(*canvas_color)
                # rgba: tuple([x / 255 for x in self.color] + [.99])
                self.rect = Rectangle(pos=self.pos, size=self.size)
        else:
            with self.canvas.before:
                Color(*canvas_color)
                # rgba: tuple([x / 255 for x in self.color] + [.99])
                self.rect = Rectangle(pos=self.pos, size=self.size, source=icon)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        if self.rect:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pos_hint = {}
            self.moving = True
            if self.nation and (self.nation.name == self.active_nation):
                self.nation.label_tokens()
        return super(Token, self).on_touch_down(touch)

    def goto_territory(self, territory):
        self.nation.snap_map.place_token_in_territory(self, territory)

    def hide(self):
        if self.hidden:
            return
        self.hidden = True
        if self.territory.name == 'UnitStock':
            self.goto_territory('HiddenUnitStock')
        if self.territory.name == 'CityStock':
            self.goto_territory('HiddenCityStock')
        if self.territory.name == 'BoatStock':
            self.goto_territory('HiddenBoatStock')
        if self.territory.name == 'Treasury':
            self.goto_territory('HiddenTreasury')

    def show(self):
        if not self.hidden:
            return
        self.hidden = False
        if self.territory.name == 'HiddenUnitStock':
            self.goto_territory('UnitStock')
        if self.territory.name == 'HiddenCityStock':
            self.goto_territory('CityStock')
        if self.territory.name == 'HiddenBoatStock':
            self.goto_territory('BoatStock')
        if self.territory.name == 'HiddenTreasury':
            self.goto_territory('Treasury')


class UnitToken(Token):
    def __str__(self):
        if self.nation and self.territory:
            return f"UnitToken of {self.nation.name} in {self.territory.name} Moving: {self.moving}"
        else:
            return f"Unassigned UnitToken"

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.moving:
            self.moving = False
            self.nation.snap_map.place_token_at_pos(self, touch.pos)
            self.nation.label_tokens()
        super(UnitToken, self).on_touch_up(touch)
        return True


class CityToken(Token):
    def __str__(self):
        if self.nation and self.territory:
            return f"CityToken of {self.nation.name} in {self.territory.name} Moving: {self.moving}"
        else:
            return f"Unassigned UnitToken"

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.moving:
            self.moving = False
            self.nation.snap_map.place_token_at_pos(self, touch.pos)
            self.nation.label_tokens()
        return super(CityToken, self).on_touch_up(touch)

    def draw_rect(self, token_color, icon):
        canvas_color = [x / 255 for x in token_color] + [.99]
        if not icon:
            icon = 'default_icon.png'
        with self.canvas.before:
            Color(*canvas_color)
            # rgba: tuple([x / 255 for x in self.color] + [.99])
            self.rect = Ellipse(pos=self.pos, size=self.size, source=icon)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)


class BoatToken(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.moving:
            self.moving = False
            print(f'Released {self} at {touch.pos}')
            self.nation.snap_map.place_token_at_pos(self, touch.pos)
            self.nation.label_tokens()
        return super(BoatToken, self).on_touch_up(touch)


class Spotter(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.moving:
            self.moving = False
            wp = self.nation.snap_map.window_to_map(self.pos)
            x = round(wp[0])
            y = round(wp[1])
            print(
                f"'TERRITORY': {{'pop_limit': 1, 'nations': None, 'Prime': {x, y}, 'Alt': [{x + 64, y},{x, y - 64}]}},")
        super(Spotter, self).on_touch_up(touch)


class AstToken(Token):
    ast = NumericProperty(0)
    track = NumericProperty(0)

    def __init__(self, ast=0, track=0, **kwargs):
        super(AstToken, self).__init__(**kwargs)
        self.ast = ast
        self.track = track
        self.pos_hint = {'x': (208 + self.ast * 60) / 4058.0, 'y': (27 + self.track * 60) / 2910.0}

    def refresh_pos(self):
        self.pos_hint = {'x': (208 + self.ast * 60) / 4058.0, 'y': (27 + self.track * 60) / 2910.0}
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
