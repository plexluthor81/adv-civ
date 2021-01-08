from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class MapWidget(BoxLayout):
    pass

class MapApp(App):
    def build(self):
        return MapWidget()

if __name__ == "__main__":
    civmap = MapApp()
    civmap.run()
