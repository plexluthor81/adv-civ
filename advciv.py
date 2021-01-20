from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.behaviors import DragBehavior
from kivy.lang import Builder
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.graphics.vertex_instructions import Rectangle, Ellipse
from kivy.graphics.context_instructions import Color



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
        Ellipse:
            pos: self.pos
            size: self.size
            source: root.nation.city_icon if root.nation else 'default_city.png'

<BoatToken>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: root.nation.boat_icon if root.nation else 'default_boat.png'

<Spotter>:
    canvas.before:
        Color:
            rgba: (.1,.1,.1,.9)
        Rectangle:
            pos: self.pos
            size: self.size

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

FloatLayout:
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
                Spotter:
                    size_hint: 60/4058.0,60/2910.0
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


class NationButton(Button):
    def on_press(self):
        app = App.get_running_app()
        # Here's a useful snippet for checking the map data by double-clicking a nation button:
        if False and (app.active_nation == self.text):
            print(len(app.nations[0].tokens))
            u = app.nations[0].tokens[0]
            for t in snap_map.territories:
                # if t.city_site:
                # if (whatever you want to check):
                if t.pop_limit == 1: # This is the relevant test condition
                    u = next(unit for unit in app.nations[0].tokens if
                         isinstance(unit, UnitToken) and unit.territory.name == 'UnitStock')
                    u.goto_territory(t)
            app.nations[0].label_tokens()
        # It will stick a unit token in whatever property you test for.

        # This is the real behavior for the button:
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


global snap_map
colors = {'Africa': [186, 96, 41], 'Italy': [252, 0, 0], 'Illyria': [245, 239, 7],
          'Thrace': [67, 177, 30], 'Crete': [102, 201, 29], 'Asia': [243, 146, 51],
          'Assyria': [61, 185, 209], 'Babylon': [145, 245, 244], 'Egypt': [212, 198, 137],
          'Phoenecia': [155, 10, 180]}


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
        global snap_map
        snap_map = SnapMap(root.ids['ms'], map_type='advciv')
        self.nations.append(Nation('Africa', [186, 96, 41], 9, fl, 'africa_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png', 55))
        self.nations.append(Nation('Italy', [252, 0, 0], 8, fl, 'italy_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png', 55))
        self.nations.append(Nation('Crete', [102, 201, 29], 5, fl, 'italy_token_icon.png', 'crete_city_icon.png', 'africa_ship_icon.png', 55))
        return root

TestApp().run()
