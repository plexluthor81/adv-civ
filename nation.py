from tokens import AstToken, UnitToken, CityToken, BoatToken


default_colors = {'Africa': [186, 96, 41], 'Italy': [252, 0, 0], 'Illyria': [245, 239, 7],
                  'Thrace': [67, 177, 30], 'Crete': [102, 201, 29], 'Asia': [243, 146, 51],
                  'Assyria': [61, 185, 209], 'Babylon': [145, 245, 244], 'Egypt': [212, 198, 137],
                  'Phoenecia': [155, 10, 180]}
default_icons = {'Africa': ['africa_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png'],
                 'Italy': ['italy_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png'],
                 'Illyria': ['africa_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png'],
                 'Thrace': ['africa_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png'],
                 'Crete': ['africa_token_icon.png', 'crete_city_icon.png', 'africa_ship_icon.png'],
                 'Asia': ['africa_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png'],
                 'Assyria': ['africa_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png'],
                 'Babylon': ['africa_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png'],
                 'Egypt': ['africa_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png'],
                 'Phoenecia': ['africa_token_icon.png', 'africa_city_icon.png', 'africa_ship_icon.png'],
                 }
default_tracks = {'Africa': 9, 'Italy': 8, 'Illyria': 7, 'Thrace': 6, 'Crete': 5, 'Asia': 4,
                  'Assyria': 3, 'Babylon': 2, 'Egypt': 1, 'Phoenecia': 0}


class Nation:
    num_units = 55
    name = 'Unnamed'
    color = [0, 0, 0]
    track = 0
    fl = None
    snap_map = None
    units_in_location = {}
    boats_in_location = {}
    cities_in_location = {}
    unit_icon = 'default_unit_icon.png'
    boat_icon = 'default_boat_icon.png'

    def __init__(self, name, fl, snap_map, num_units=55, track=-1, color=[0, 0, 0], icons=[], **kwargs):
        print(name)
        print(fl)
        print(snap_map)
        self.name = name
        if color == [0, 0, 0] and name in default_colors.keys():
            self.color = default_colors[name]
        else:
            self.color = color
        if track == -1 and name in default_tracks.keys():
            self.track = default_tracks[name]
        else:
            self.track = track
        self.fl = fl
        self.snap_map = snap_map
        self.num_units = num_units
        if icons == [] and name in default_icons.keys():
            self.unit_icon = default_icons[name][0]
            self.city_icon = default_icons[name][1]
            self.boat_icon = default_icons[name][2]
        else:
            self.unit_icon = icons[0]
            self.city_icon = icons[1]
            self.boat_icon = icons[2]

        for location in [t.name for t in snap_map.territories]:
            self.units_in_location[location] = 0
            self.boats_in_location[location] = 0
            self.cities_in_location[location] = 0

        self.ast_token = AstToken(ast=0, track=self.track, token_color=self.color, size_hint=(50 / 4058.0, 50 / 2910.0))
        fl.add_widget(self.ast_token)

        self.tokens = []

        for i in range(num_units):
            token = UnitToken(nation=self, hidden=True, territory='HiddenUnitStock',
                              size_hint=snap_map.size_to_hint((60, 60)),
                              icon=default_icons[self.name][0])
            self.fl.add_widget(token)
            self.units_in_location['HiddenUnitStock'] = self.units_in_location['HiddenUnitStock'] + 1
            self.tokens.append(token)

        print('Done with Units, starting Cities')
        for i in range(9):
            city = CityToken(nation=self, hidden=True, territory='HiddenCityStock',
                             size_hint=snap_map.size_to_hint((60, 60)),
                             icon=default_icons[self.name][1])
            self.fl.add_widget(city)
            self.units_in_location['HiddenCityStock'] += 1
            self.tokens.append(city)

        for i in range(4):
            boat = BoatToken(nation=self, hidden=True, territory='HiddenBoatStock',
                             size_hint=snap_map.size_to_hint((93, 60)),
                             icon=default_icons[self.name][2])
            self.fl.add_widget(boat)
            self.units_in_location['HiddenBoatStock'] += 1
            self.tokens.append(boat)

        self.label_tokens()
        print(f'Done with {self.name}')

    def update_locations(self, *args):
        print(f'Should be updating locations for {self.name}')

    def label_tokens(self):
        units_in_location = {}
        boats_in_location = {}
        cities_in_location = {}
        for token in self.tokens:
            if isinstance(token, UnitToken):
                d = units_in_location
            if isinstance(token, BoatToken):
                d = boats_in_location
            if isinstance(token, CityToken):
                d = cities_in_location
            if token.territory in d.keys():
                d[token.territory] += 1
            else:
                d[token.territory] = 1
        for token in self.tokens:
            if isinstance(token, UnitToken):
                d = units_in_location
            if isinstance(token, BoatToken):
                d = boats_in_location
            if isinstance(token, CityToken):
                d = cities_in_location
            if d[token.territory] > 1:
                token.text = str(d[token.territory])
            else:
                token.text = ''
        self.units_in_location = units_in_location
        self.boats_in_location = boats_in_location
        self.cities_in_location = cities_in_location

    def build_city(self, territory):
        for token in self.tokens:
            if isinstance(token, UnitToken) and token.territory == territory:
                token.goto_territory('Stock')
        self.label_tokens()

    def show_or_hide_stock(self, active_nation):
        print(f"{self.name} showing or hiding based on {active_nation}")
        if active_nation == self.name:
            for token in self.tokens:
                if token.territory.name in ['HiddenUnitStock', 'HiddenCityStock', 'HiddenBoatStock', 'HiddenTreasury']:
                    token.show()
        else:
            for token in self.tokens:
                if token.territory.name in ['UnitStock', 'CityStock', 'BoatStock', 'Treasury']:
                    token.hide()
