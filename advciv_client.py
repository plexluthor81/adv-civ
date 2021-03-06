from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from flask import json

from contextlib import suppress

from nation_selector import NationSelectionScreen
from login_screen import LoginScreen
from civ_map_screen import CivMapScreen
from nation import Nation
from snap_map import SnapMap
from tokens import Spotter, AstToken


class AdvCivClientApp(App):
    player = ''
    screen_manager = ObjectProperty(None)
    login_page = None
    nation_selection_page = None
    civ_map_page = None
    active_nation = StringProperty('')

    def update_buttons(self):
        pass

    def show_stuff(self, root=None):
        if not root:
            root = self.root

    def build(self):
        self.title = "Advanced Civilization"
        self.screen_manager = ScreenManager(pos=(0, 0), pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

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
        self.nation_selection_page.player_name = self.login_page.name
        self.nation_selection_page.server_url = self.login_page.url
        self.login_page.bind(name=self.nation_selection_page.setter('player_name'))
        self.login_page.bind(url=self.nation_selection_page.setter('server_url'))
        self.nation_selection_page.bind(nation=self.setter('active_nation'))

        self.civ_map_page = CivMapScreen(pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))
        screen = Screen(name="CivMap", pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))
        screen.add_widget(self.civ_map_page)
        self.screen_manager.add_widget(screen)
        self.bind(active_nation=self.civ_map_page.st.setter('nation'))

        return self.screen_manager

    def handle_connect(self, instance, connected):
        if connected:
            print('Login screen connected successfully')
            print(self.nation_selection_page.player_name)
            print(self.nation_selection_page.server_url)
            self.nation_selection_page.request_update()
            self.screen_manager.current = "NationSelection"

    def handle_finish(self, instance, finished):
        if finished:
            self.active_nation = self.nation_selection_page.nation
            print(f"Nation Selection finished successfully (I'm {self.active_nation})")
            self.screen_manager.current = "CivMap"
            snap_map = SnapMap(self.civ_map_page.ms)

            fl = self.civ_map_page.fl
            for n in self.nation_selection_page.get_selected_nations():
                self.civ_map_page.nations.append(Nation(n, fl, snap_map))

            for n in self.civ_map_page.nations:
                n.show_or_hide_stock(self.active_nation)

            self.update_board(0)
            Clock.schedule_interval(self.update_board, 1)

    def update_board(self, dt):
        n = [n for n in self.civ_map_page.nations if n.name == self.active_nation][0]
        url = self.login_page.url
        if dt == 0:
            body = None
        else:
            body = json.dumps(n.get_dict())
        req = UrlRequest(url=f"{url}/civ_board", on_success=self.handle_update,
                         on_failure=self.show_error_msg, on_error=self.show_error_msg,
                         req_body=body,
                         req_headers={'Content-Type': 'application/json'},
                         timeout=None, decode=True, debug=False, file_path=None, ca_file=None,
                         verify=False)

    def handle_update(self, req, res):
        res_list = json.loads(res)
        for n in self.civ_map_page.nations:
            if n.name not in res_list:
                print(f"{n.name} not listed on server: {res_list.keys()}")
                return
            if n.name == self.active_nation:
                if res_list[n.name] == n.get_dict():
                    pass
                else:
                    print(f"Client {n.name} doesn't match server!")
            if res_list[n.name] == {}:
                continue
            else:
                for i in range(len(res_list[n.name]['tokens'])):
                    if n.name == self.active_nation:
                        if res_list[n.name]['tokens'][i] == 'HiddenUnitStock':
                            res_list[n.name]['tokens'][i] = 'UnitStock'
                        if res_list[n.name]['tokens'][i] == 'HiddenCityStock':
                            res_list[n.name]['tokens'][i] = 'CityStock'
                        if res_list[n.name]['tokens'][i] == 'HiddenBoatStock':
                            res_list[n.name]['tokens'][i] = 'BoatStock'
                    else:
                        if res_list[n.name]['tokens'][i] == 'UnitStock':
                            res_list[n.name]['tokens'][i] = 'HiddenUnitStock'
                        if res_list[n.name]['tokens'][i] == 'CityStock':
                            res_list[n.name]['tokens'][i] = 'HiddenCityStock'
                        if res_list[n.name]['tokens'][i] == 'BoatStock':
                            res_list[n.name]['tokens'][i] = 'HiddenBoatStock'
            n.update(res_list[n.name])

    @staticmethod
    def show_error_msg(request, error):
        print('Error')
        print(error)


if __name__ == "__main__":
    client = AdvCivClientApp()
    client.run()

        
