from kivy.uix.behaviors import DragBehavior
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle

Token_kv = '''
<AstTokenWidget>:
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

<Spotter>:
    canvas.before:
        Color:
            rgba: (.1,.1,.1,.9)
        Rectangle:
            pos: self.pos
            size: self.size
'''


class Token(DragBehavior, Label):
    nation = ObjectProperty(None)
    active_nation = StringProperty('')
    hidden = False
    moving = False
    territory = ObjectProperty(None, allownone=True)

    def __init__(self, nation=None, hidden=False, territory=None, moving=False, **kwargs):
        Builder.load_string(Token_kv)
        super(Token, self).__init__(**kwargs)
        self.nation = nation
        self.hidden = hidden
        self.moving = moving
        self.territory = None
        if territory:
            self.goto_territory(territory)

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


class AstToken(Label):
    ast = NumericProperty(0)
    track = NumericProperty(0)
    color = ListProperty([0, 0, 0])
    target_size = 48
    rect = None

    def __init__(self, ast=0, track=0, color=[.5, .5, .5], **kwargs):
        self.text = 'A'
        super(AstToken, self).__init__(**kwargs)
        self.ast = ast
        self.track = track
        self.color = color
        # Builder.load_string(Token_kv)
        canvas_color = [x / 255 for x in self.color] + [.99]
        with self.canvas.before:
            Color(*canvas_color)
            # rgba: tuple([x / 255 for x in self.color] + [.99])
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        if self.rect:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def refresh_pos(self):
        print(f'AST refresh_pos {self.color} {tuple([x / 255.0 for x in self.color] + [.99])}')
        self.pos_hint['x'] = (207 + self.ast * 60) / 4058.0
        self.pos_hint['y'] = (26 + self.track * 60) / 2910.0
        print(self.pos_hint)
        print(self.parent)

        if self.parent:
            self.parent._trigger_layout()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print(f'touch_down on AstToken: {self.ast} {self.track} {self.color} {self.pos}, {self.pos_hint}')
            # AstToken.show_parentage(self, 6)
            self.ast += 1
            if self.ast > 15:
                self.ast = 1
            # AstToken.show_parentage(self, 6)

    @staticmethod
    def show_parentage(obj, i):
        if i > 0:
            AstToken.show_parentage(obj.parent, i-1)
        print(obj)
        print(obj.pos, obj.pos_hint)
        print(obj.size, obj.size_hint)

    def on_track(self, instance, pos):
        self.refresh_pos()

    def on_ast(self, instance, pos):
        self.refresh_pos()


