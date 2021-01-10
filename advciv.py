from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.properties import NumericProperty

class AstTokenWidget(Label):
    ast = NumericProperty(0)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.ast += 1
            if self.ast > 15:
                self.ast = 1


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

        return super(BoxLayout, self).on_touch_down(touch)


class AdvCivApp(App):
    def build(self):
        return AdvCivWidget()

if __name__ == "__main__":
    civmap = AdvCivApp()
    civmap.run()
