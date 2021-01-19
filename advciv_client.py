from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager

from contextlib import suppress

from nation_selector import NationSelectionScreen, nation_selector_kv
from login_screen import LoginScreen
from civ_map_screen import CivMapScreen


class AdvCivClientApp(App):
    player = ''
    screen_manager = ObjectProperty(None)
    login_page = None
    nation_selection_page = None
    civ_map_page = None

    def update_buttons(self):
        pass

    def show_stuff(self, root=None):
        if not root:
            root = self.root

    def build(self):
        self.title = "Advanced Civilization"
        self.screen_manager = ScreenManager()

        self.login_page = LoginScreen()
        screen = Screen(name="Login")
        screen.add_widget(self.login_page)
        self.screen_manager.add_widget(screen)
        self.login_page.bind(connected=self.handle_connect)

        self.nation_selection_page = NationSelectionScreen()
        screen = Screen(name="NationSelection")
        screen.add_widget(self.nation_selection_page)
        self.screen_manager.add_widget(screen)
        self.nation_selection_page.bind(finished=self.handle_finish)

        self.civ_map_page = CivMapScreen()
        screen = Screen(name="CivMap")
        screen.add_widget(self.civ_map_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def handle_connect(self, instance, connected):
        if connected:
            print('Login screen connected successfully')
            self.nation_selection_page.player_name = self.login_page.ids['name'].text
            self.nation_selection_page.server_url = self.login_page.ids['url'].text
            self.nation_selection_page.request_update()
            self.screen_manager.current = "NationSelection"

    def handle_finish(self, instance, finished):
        if finished:
            print('Nation Selection finished successfully')
            self.screen_manager.current = "CivMap"
            print(self.nation_selection_page.get_selected_nations())


if __name__ == "__main__":
    client = AdvCivClientApp()
    client.run()

        
