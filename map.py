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

class MapWidget(BoxLayout):
    pass

class MapApp(App):
    def build(self):
        return MapWidget()

if __name__ == "__main__":
    civmap = MapApp()
    civmap.run()
