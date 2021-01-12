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

from math import sqrt

class Territory:
    def __init__(self, name, pop_limit, unit_spots, city_site=False,
                 flood_plain='', flood_city=False, starting_nation='',
                 boat_spots=[]):
        self.name = name
        self.pop_limit = pop_limit
        self.unit_spots = unit_spots
        self.city_site = city_site
        self.flood_plain = flood_plain
        self.flood_city = flood_city
        self.starting_nation = starting_nation
        self.boat_spots = boat_spots

        self.tokens = []
        self.has_city_token = False
        self.unit_nations = []
        self.boat_nations = []

    def __repr__(self):
        return f"Territory Object {{name: {self.name}, len(tokens): {len(self.tokens)}, tokens: {self.tokens}, unit_spots: {self.unit_spots}}}"

    def add_token(self, token):
        if token not in self.tokens:
            self.tokens.append(token)

    def remove_token(self, token):
        if token not in self.tokens:
            raise Exception(f"Tried removing {token} from {self.name}, but it wasn't there")
        self.tokens.remove(token)
        if isinstance(token, UnitToken):
            nation_list = self.unit_nations
            spot_list = self.unit_spots
            token_class = UnitToken
        elif isinstance(token, BoatToken):
            nation_list = self.boat_nations
            spot_list = self.boat_spots
            token_class = BoatToken
        elif isinstance(token, CityToken):
            self.has_city_token = False
            return # TODO: place tokens in that prime spot if this is conflict
        if nation_list and (len([n for n in nation_list if n==token.nation]) == 0):
            # If that was the last one for that nation, we have more to do
            nation_index = nation_list.index(token.nation)
            if not (nation_index == len(nation_list)-1):
                # Trade places
                swap_nation = nation_list[-1]
                nation_list[nation_index] = nation_list[-1]
                for t in self.tokens:
                    if isinstance(t, token_class) and t.nation==swap_nation:
                        t.goto_territory(self.name)
            nation_list.remove(token.nation)

    def try_adding_token(self, token):
        # Returns a boolean indicating whether token is allowed, and also a tuple with coords for where to place it.
        # If token is not allowed, coords are (0, 0)
        if isinstance(token, CityToken):
            if self.has_city_token and not self.name in ['CityStock', 'HiddenCityStock']:
                # Reject the city token, we've already got one
                return False, (0, 0)
            if (not self.unit_nations) or (self.unit_nations == [token.nation]):
                # Accept the city token, and send units back to stock
                print("\n\n\n\nSending units back home to place City")
                print(len(self.tokens))
                tokens_to_send_home = [t for t in self.tokens if isinstance(t, UnitToken) and t.nation==token.nation]
                for t in tokens_to_send_home:
                    t.goto_territory('UnitStock')
                if len([t for t in self.tokens if isinstance(t, UnitToken)]) > 0:
                    raise Exception(f"Unexpected unit token from {self.tokens[0].nation} in {self.name}")
                print(self)
                self.unit_nations = []
                self.add_token(token)
                self.has_city_token = True
                print(self)
                return True, self.unit_spots[0]
        if isinstance(token, UnitToken):
            if self.has_city_token:
                if token.nation not in self.unit_nations:
                    if len(self.unit_nations) == len(self.unit_spots)-1:
                        raise Exception(f"Trying to add too many nations' units in {self.name}. Max={len(self.unit_spots)} (city using 1)")
                    self.unit_nations.append(token.nation)
                self.add_token(token)
                print(self)
                print(token)
                return True, self.unit_spots[self.unit_nations.index(token.nation)+1]
            else:
                if token.nation not in self.unit_nations:
                    if len(self.unit_nations) == len(self.unit_spots):
                        raise Exception(f"Trying to add too many nations' units in {self.name}. Max={len(self.unit_spots)}")
                    self.unit_nations.append(token.nation)
                self.add_token(token)
                print(self)
                return True, self.unit_spots[self.unit_nations.index(token.nation)]
        if isinstance(token, BoatToken):
            if len(self.boat_spots)==0:
                return True, snap_map.window_to_map(token.pos)
            if token.nation not in self.boat_nations:
                if len(self.boat_nations) == len(self.boat_spots):
                    raise Exception(f"Trying to add too many nations' boats in {self.name}. Max={len(self.boat_spots)}")
                self.boat_nations.append(token.nation)
            self.add_token(token)
            return True, self.boat_spots[self.boat_nations.index(token.nation)]
        raise Exception(f"Trying to add non-City, non-Unit, non-Ship token {token} to {self.name}")


advciv_territory_list = [
    {'name': 'Abydos', 'pop_limit': 5, 'unit_spots': [(2867, 1118), (2931, 1118), (2867, 1054)], 'city_site': True},
    {'name': 'Aetolia', 'pop_limit': 2, 'unit_spots': [(1933, 1835), (1997, 1835), (1933, 1771)]},
    {'name': 'Akkadia', 'pop_limit': 3, 'unit_spots': [(3660, 1867), (3724, 1867), (3660, 1803)]},
    {'name': 'Alani', 'pop_limit': 1, 'unit_spots': [(3200, 2779), (3264, 2779), (3200, 2715)], 'starting_nation': 'Assyria'},
    {'name': 'Albania', 'pop_limit': 1, 'unit_spots': [(3528, 2809), (3592, 2809), (3528, 2745)], 'starting_nation': 'Assyria'},
    {'name': 'Aleppo', 'pop_limit': 2, 'unit_spots': [(3125, 1979), (3189, 1979), (3125, 1915)], 'city_site': True},
    {'name': 'Alexandria', 'pop_limit': 4, 'unit_spots': [(2765, 1366), (2829, 1366), (2765, 1302)], 'city_site': True},
    {'name': 'Anatolia', 'pop_limit': 1, 'unit_spots': [(2647, 2364), (2711, 2364), (2647, 2300)]},
    {'name': 'Ancyra', 'pop_limit': 2, 'unit_spots': [(2781, 2261), (2845, 2261), (2781, 2197)], 'city_site': True},
    {'name': 'Antioch', 'pop_limit': 2, 'unit_spots': [(2996, 1932), (3060, 1932), (2996, 1868)], 'city_site': True},
    {'name': 'Apollonia', 'pop_limit': 1, 'unit_spots': [(1739, 2042), (1803, 2042), (1739, 1978)], 'city_site': True},
    {'name': 'Aquitania', 'pop_limit': 1, 'unit_spots': [(332, 2049), (396, 2049), (332, 1985)]},
    {'name': 'Arabia', 'pop_limit': 1, 'unit_spots': [(3680, 1504), (3744, 1504), (3680, 1440)]},
    {'name': 'Armenia', 'pop_limit': 3, 'unit_spots': [(3364, 2591), (3428, 2591), (3364, 2527)]},
    {'name': 'Armorica', 'pop_limit': 1, 'unit_spots': [(220, 2510), (284, 2510), (220, 2446)]},
    {'name': 'Ashur', 'pop_limit': 3, 'unit_spots': [(3405, 2128), (3469, 2128), (3405, 2064)], 'city_site': True},
    {'name': 'Assyria', 'pop_limit': 3, 'unit_spots': [(3697, 2358), (3761, 2358), (3697, 2294)]},
    {'name': 'Athens', 'pop_limit': 2, 'unit_spots': [(2104, 1787), (2168, 1787), (2104, 1723)], 'city_site': True},
    {'name': 'Babylon', 'pop_limit': 3, 'unit_spots': [(3857, 1988), (3921, 1988), (3857, 1924)], 'city_site': True},
    {'name': 'Balearic Islands', 'pop_limit': 1, 'unit_spots': [(578, 1720), (642, 1720), (578, 1656)]},
    {'name': 'Belgica', 'pop_limit': 3, 'unit_spots': [(637, 2628), (701, 2628), (637, 2564)]},
    {'name': 'Brittania', 'pop_limit': 2, 'unit_spots': [(346, 2778), (410, 2778), (346, 2714)]},
    {'name': 'Byblos', 'pop_limit': 3, 'unit_spots': [(3103, 1845), (3167, 1845), (3103, 1781)]},
    {'name': 'Byzantium', 'pop_limit': 3, 'unit_spots': [(2260, 2183), (2324, 2183), (2260, 2119)], 'city_site': True},
    {'name': 'Caesariensis', 'pop_limit': 1, 'unit_spots': [(423, 1288), (487, 1288), (423, 1224)]},
    {'name': 'Cappadocia', 'pop_limit': 3, 'unit_spots': [(3151, 2349), (3215, 2349), (3151, 2285)]},
    {'name': 'Capua', 'pop_limit': 1, 'unit_spots': [(1345, 1938), (1409, 1938), (1345, 1874)], 'city_site': True},
    {'name': 'Carthage', 'pop_limit': 3, 'unit_spots': [(1174, 1515), (1238, 1515), (1174, 1451)], 'city_site': True},
    {'name': 'Caucasus', 'pop_limit': 2, 'unit_spots': [(2963, 2755), (3027, 2755), (2963, 2691)], 'starting_nation': 'Asia'},
    {'name': 'Celtiberi', 'pop_limit': 1, 'unit_spots': [(281, 1824), (345, 1824), (281, 1760)]},
    {'name': 'Chalcis', 'pop_limit': 2, 'unit_spots': [(2070, 1884), (2134, 1884), (2070, 1820)], 'city_site': True},
    {'name': 'Cilicia', 'pop_limit': 2, 'unit_spots': [(2752, 1955), (2816, 1955), (2752, 1891)]},
    {'name': 'Cirenaica', 'pop_limit': 1, 'unit_spots': [(1812, 1052), (1876, 1052), (1812, 988)]},
    {'name': 'Cirta', 'pop_limit': 2, 'unit_spots': [(856, 1397), (920, 1397), (856, 1333)], 'city_site': True},
    {'name': 'Cisalpine Gaul', 'pop_limit': 2, 'unit_spots': [(1030, 2241), (1094, 2241), (1030, 2177)]},
    {'name': 'Constanta', 'pop_limit': 2, 'unit_spots': [(2237, 2495), (2301, 2495), (2237, 2431)], 'city_site': True},
    {'name': 'Corinth', 'pop_limit': 2, 'unit_spots': [(1947, 1767), (2011, 1767), (1947, 1703)], 'city_site': True},
    {'name': 'Corsica', 'pop_limit': 1, 'unit_spots': [(997, 2007), (1061, 2007), (997, 1943)]},
    {'name': 'Ctesiphon', 'pop_limit': 2, 'unit_spots': [(3734, 1990), (3798, 1990), (3734, 1926)], 'city_site': True},
    {'name': 'Cyprus', 'pop_limit': 2, 'unit_spots': [(2808, 1762), (2872, 1762), (2808, 1698)]},
    {'name': 'Cyrene', 'pop_limit': 3, 'unit_spots': [(2028, 1235), (2092, 1235), (2028, 1171)], 'city_site': True},
    {'name': 'Dacia Inferior', 'pop_limit': 5, 'unit_spots': [(2039, 2511), (2103, 2511), (2039, 2447)]},
    {'name': 'Dacia Superior', 'pop_limit': 3, 'unit_spots': [(1780, 2554), (1844, 2554), (1780, 2490)]},
    {'name': 'Dalmatia', 'pop_limit': 2, 'unit_spots': [(1657, 2240), (1721, 2240), (1657, 2176)]},
    {'name': 'Damascus', 'pop_limit': 2, 'unit_spots': [(3189, 1745), (3253, 1745), (3189, 1681)], 'city_site': True},
    {'name': 'Delos', 'pop_limit': 2, 'unit_spots': [(2230, 1712), (2294, 1712), (2230, 1648)], 'city_site': True},
    {'name': 'Eastern Desert', 'pop_limit': 1, 'unit_spots': [(3006, 1221), (3070, 1221), (3006, 1157)]},
    {'name': 'Eastern Gaetulia', 'pop_limit': 1, 'unit_spots': [(2214, 976), (2278, 976), (2214, 912)], 'starting_nation': 'Egypt'},
    {'name': 'Edetania', 'pop_limit': 1, 'unit_spots': [(475, 1842), (539, 1842), (475, 1778)]},
    {'name': 'Epirus', 'pop_limit': 1, 'unit_spots': [(1821, 1925),(1885, 1925),(1821, 1861)]},
    {'name': 'Eretria', 'pop_limit': 1, 'unit_spots': [(2143, 1838), (2207, 1838), (2143, 1774)], 'city_site': True},
    {'name': 'Gades', 'pop_limit': 2, 'unit_spots': [(183, 1556), (247, 1556), (183, 1492)], 'city_site': True, 'starting_nation': 'Italy'},
    {'name': 'Galatia', 'pop_limit': 2, 'unit_spots': [(2530, 2242), (2594, 2242), (2530, 2178)]},
    {'name': 'Gallaecia', 'pop_limit': 1, 'unit_spots': [(98, 1992), (162, 1992), (98, 1928)], 'starting_nation': 'Italy'},
    {'name': 'Gallia Lugdunensis', 'pop_limit': 3, 'unit_spots': [(436, 2366), (500, 2366), (436, 2302)]},
    {'name': 'Garamantes', 'pop_limit': 1, 'unit_spots': [(1613, 897), (1677, 897), (1549, 897)], 'starting_nation': 'Africa'},
    {'name': 'Gaza', 'pop_limit': 2, 'unit_spots': [(3058, 1524), (3122, 1524), (3058, 1460)], 'city_site': True},
    {'name': 'Genua', 'pop_limit': 2, 'unit_spots': [(899, 2140), (963, 2140), (899, 2076)], 'city_site': True},
    {'name': 'Georgia', 'pop_limit': 1, 'unit_spots': [(3118, 2578), (3182, 2578), (3118, 2514)]},
    {'name': 'Germania Magna', 'pop_limit': 5, 'unit_spots': [(1299, 2747), (1363, 2747), (1299, 2683)], 'starting_nation': 'Illyria'},
    {'name': 'Germanica Superior', 'pop_limit': 1, 'unit_spots': [(919, 2543), (983, 2543), (919, 2479)]},
    {'name': 'Gordium', 'pop_limit': 2, 'unit_spots': [(2601, 2094), (2665, 2094), (2601, 2030)], 'city_site': True},
    {'name': 'Great Erg', 'pop_limit': 1, 'unit_spots': [(680, 965), (744, 965), (680, 901)], 'starting_nation': 'Africa'},
    {'name': 'Helvetii', 'pop_limit': 1, 'unit_spots': [(881, 2356), (945, 2356), (881, 2292)]},
    {'name': 'Hippo Regius', 'pop_limit': 2, 'unit_spots': [(1021, 1452), (1021, 1516), (1021, 1388)]},
    {'name': 'Illyria', 'pop_limit': 2, 'unit_spots': [(1449, 2233), (1513, 2233), (1449, 2169)]},
    {'name': 'Ionia', 'pop_limit': 3, 'unit_spots': [(2487, 1965), (2551, 1965), (2487, 1901)]},
    {'name': 'Ithaca', 'pop_limit': 1, 'unit_spots': [(1759, 1868), (1823, 1868), (1759, 1804)], 'city_site': True},
    {'name': 'Jerusalem', 'pop_limit': 1, 'unit_spots': [(3228, 1575), (3292, 1575), (3228, 1511)], 'city_site': True},
    {'name': 'Kanesh', 'pop_limit': 2, 'unit_spots': [(2886, 2143), (2950, 2143), (2886, 2079)], 'city_site': True},
    {'name': 'Knossus', 'pop_limit': 3, 'unit_spots': [(2327, 1613), (2391, 1613), (2327, 1549)], 'city_site': True, 'starting_nation': 'Crete'},
    {'name': 'Kush', 'pop_limit': 1, 'unit_spots': [(3406, 920), (3470, 920), (3406, 856)], 'starting_nation': 'Egypt'},
    {'name': 'Lemnos', 'pop_limit': 1, 'unit_spots': [(2136, 2027), (2200, 2027), (2136, 1963)]},
    {'name': 'Leptis Magna', 'pop_limit': 1, 'unit_spots': [(1541, 1114), (1605, 1114), (1541, 1050)], 'city_site': True},
    {'name': 'Lesbos', 'pop_limit': 1, 'unit_spots': [(2225, 1929), (2289, 1929), (2225, 1865)]},
    {'name': 'Libya', 'pop_limit': 2, 'unit_spots': [(1256, 1137), (1256, 1073), (1320, 1073)]},
    {'name': 'Lilybaeum', 'pop_limit': 2, 'unit_spots': [(1342, 1611), (1406, 1611), (1342, 1547)], 'city_site': True},
    {'name': 'Lucani', 'pop_limit': 2, 'unit_spots': [(1515, 1832), (1579, 1832), (1515, 1768)]},
    {'name': 'Lusitania', 'pop_limit': 1, 'unit_spots': [(94, 1741), (158, 1741), (94, 1677)], 'starting_nation': 'Italy'},
    {'name': 'Lycia', 'pop_limit': 1, 'unit_spots': [(2585, 1822), (2649, 1822), (2585, 1758)]},
    {'name': 'Macedonia', 'pop_limit': 1, 'unit_spots': [(1893, 2088), (1957, 2088), (1893, 2024)]},
    {'name': 'Maedia', 'pop_limit': 1, 'unit_spots': [(3621, 2592), (3685, 2592), (3621, 2528)]},
    {'name': 'Mahon', 'pop_limit': 1, 'unit_spots': [(730, 1770), (794, 1770), (730, 1706)], 'city_site': True},
    {'name': 'Mari', 'pop_limit': 3, 'unit_spots': [(3397, 1725), (3461, 1725), (3397, 1661)]},
    {'name': 'Marmarica', 'pop_limit': 2, 'unit_spots': [(2354, 1265), (2418, 1265), (2354, 1201)]},
    {'name': 'Massilia', 'pop_limit': 3, 'unit_spots': [(746, 2108), (810, 2108), (746, 2044)], 'city_site': True},
    {'name': 'Mauretania', 'pop_limit': 2, 'unit_spots': [(146, 1258), (210, 1258), (146, 1194)]},
    {'name': 'Memphis', 'pop_limit': 3, 'unit_spots': [(2848, 1267), (2912, 1267), (2848, 1203)], 'city_site': True},
    {'name': 'Mesopotamia', 'pop_limit': 3, 'unit_spots': [(3571, 2056), (3635, 2056), (3571, 1992)]},
    {'name': 'Miletus', 'pop_limit': 1, 'unit_spots': [(2430, 1833), (2494, 1833), (2430, 1769)], 'city_site': True},
    {'name': 'Mitanni', 'pop_limit': 2, 'unit_spots': [(2998, 2093), (3062, 2093), (2998, 2029)]},
    {'name': 'Moesia Superior', 'pop_limit': 1, 'unit_spots': [(1845, 2219), (1909, 2219), (1845, 2155)]},
    {'name': 'Mycenae', 'pop_limit': 1, 'unit_spots': [(2066, 1723), (2130, 1723), (2066, 1659)], 'city_site': True},
    {'name': 'Nabataei', 'pop_limit': 1, 'unit_spots': [(3495, 1188), (3559, 1188), (3495, 1124)]},
    {'name': 'Narbonensis', 'pop_limit': 2, 'unit_spots': [(583, 2005), (647, 2005), (583, 1941)]},
    {'name': 'Ninevah', 'pop_limit': 3, 'unit_spots': [(3442, 2328), (3506, 2328), (3442, 2264)], 'city_site': True},
    {'name': 'Nisibis', 'pop_limit': 2, 'unit_spots': [(3472, 1932), (3536, 1932), (3472, 1868)], 'city_site': True},
    {'name': 'Noricum', 'pop_limit': 1, 'unit_spots': [(1031, 2390), (1095, 2390), (1031, 2326)]},
    {'name': 'Nubia', 'pop_limit': 2, 'unit_spots': [(3149, 1106), (3213, 1106), (3149, 1042)]},
    {'name': 'Numidia', 'pop_limit': 2, 'unit_spots': [(1018, 1195), (1082, 1195), (1018, 1131)]},
    {'name': 'Oblia', 'pop_limit': 1, 'unit_spots': [(1001, 1861), (1065, 1861), (1001, 1797)], 'city_site': True},
    {'name': 'Odessos', 'pop_limit': 4, 'unit_spots': [(2137, 2321), (2201, 2321), (2137, 2257)], 'city_site': True},
    {'name': 'Pannonia', 'pop_limit': 4, 'unit_spots': [(1318, 2478), (1382, 2478), (1318, 2414)]},
    {'name': 'Parthia', 'pop_limit': 4, 'unit_spots': [(3751, 2147), (3815, 2147), (3751, 2083)]},
    {'name': 'Pelusium', 'pop_limit': 1, 'unit_spots': [(2979, 1456), (3043, 1456), (2979, 1392)]},
    {'name': 'Persia', 'pop_limit': 2, 'unit_spots': [(3924, 2342), (3988, 2342), (3924, 2278)], 'starting_nation': 'Babylon'},
    {'name': 'Petra', 'pop_limit': 1, 'unit_spots': [(3248, 1410), (3312, 1410), (3248, 1346)], 'city_site': True},
    {'name': 'Phastos', 'pop_limit': 2, 'unit_spots': [(2192, 1592), (2256, 1592), (2192, 1528)], 'starting_nation': 'Crete'},
    {'name': 'Pontus', 'pop_limit': 2, 'unit_spots': [(2942, 2435), (3006, 2435), (2942, 2371)], 'city_site': True},
    {'name': 'Rhodes', 'pop_limit': 2, 'unit_spots': [(2443, 1744), (2507, 1744), (2443, 1680)], 'city_site': True},
    {'name': 'Rome', 'pop_limit': 2, 'unit_spots': [(1180, 2036), (1244, 2036), (1180, 1972)], 'city_site': True},
    {'name': 'Salamis', 'pop_limit': 1, 'unit_spots': [(2904, 1837), (2968, 1837), (2904, 1773)], 'city_site': True},
    {'name': 'Samnium', 'pop_limit': 2, 'unit_spots': [(1420, 2030), (1484, 2030), (1420, 1966)]},
    {'name': 'Sardes', 'pop_limit': 2, 'unit_spots': [(2356, 1995), (2420, 1995), (2356, 1931)], 'city_site': True},
    {'name': 'Sardinia', 'pop_limit': 1, 'unit_spots': [(1023, 1746), (1087, 1746), (1023, 1682)]},
    {'name': 'Sarmatia', 'pop_limit': 3, 'unit_spots': [(2214, 2798), (2278, 2798), (2214, 2734)], 'starting_nation': 'Thrace'},
    {'name': 'Scythia', 'pop_limit': 2, 'unit_spots': [(3891, 2564), (3955, 2564), (3891, 2500)], 'starting_nation': 'Babylon'},
    {'name': 'Sequani', 'pop_limit': 1, 'unit_spots': [(812, 2531), (876, 2531), (812, 2467)]},
    {'name': 'Sicilia', 'pop_limit': 2, 'unit_spots': [(1453, 1675), (1517, 1675), (1453, 1611)]},
    {'name': 'Sidon', 'pop_limit': 1, 'unit_spots': [(3027, 1730), (3091, 1730), (3027, 1666)], 'city_site': True},
    {'name': 'Silures', 'pop_limit': 1, 'unit_spots': [(145, 2827), (209, 2827), (145, 2763)]},
    {'name': 'Sinai', 'pop_limit': 1, 'unit_spots': [(3075, 1339), (3139, 1339), (3075, 1275)]},
    {'name': 'Sindica', 'pop_limit': 1, 'unit_spots': [(2761, 2765), (2825, 2765), (2761, 2701)], 'starting_nation': 'Asia'},
    {'name': 'Sitifensis', 'pop_limit': 1, 'unit_spots': [(645, 1359), (709, 1359), (645, 1295)]},
    {'name': 'Siwa Oasis', 'pop_limit': 2, 'unit_spots': [(2634, 1226), (2698, 1226), (2634, 1162)]},
    {'name': 'Sparta', 'pop_limit': 1, 'unit_spots': [(1986, 1677), (2050, 1677), (1986, 1613)], 'city_site': True},
    {'name': 'Sumeria', 'pop_limit': 2, 'unit_spots': [(3963, 1745), (4027, 1745), (3963, 1681)]},
    {'name': 'Susa', 'pop_limit': 3, 'unit_spots': [(3960, 2118), (4024, 2118), (3960, 2054)], 'city_site': True, 'starting_nation': 'Babylon'},
    {'name': 'Swenett', 'pop_limit': 3, 'unit_spots': [(3093, 918), (3157, 918), (3093, 854)], 'city_site': True, 'starting_nation': 'Egypt'},
    {'name': 'Syracuse', 'pop_limit': 1, 'unit_spots': [(1487, 1568), (1551, 1568), (1487, 1504)], 'city_site': True},
    {'name': 'Tanis', 'pop_limit': 3, 'unit_spots': [(2876, 1408), (2940, 1408), (2876, 1344)], 'city_site': True},
    {'name': 'Tarrentum', 'pop_limit': 1, 'unit_spots': [(1610, 1925), (1674, 1925), (1610, 1861)], 'city_site': True},
    {'name': 'Taurica', 'pop_limit': 2, 'unit_spots': [(2518, 2675), (2582, 2675), (2518, 2611)]},
    {'name': 'Teutoburg', 'pop_limit': 3, 'unit_spots': [(822, 2813), (886, 2813), (822, 2749)]},
    {'name': 'Thapsos', 'pop_limit': 3, 'unit_spots': [(1193, 1340), (1257, 1340), (1193, 1276)], 'city_site': True},
    {'name': 'Thebes', 'pop_limit': 3, 'unit_spots': [(3219, 928), (3283, 928), (3219, 864)], 'city_site': True, 'starting_nation': 'Egypt'},
    {'name': 'Thessalonica', 'pop_limit': 1, 'unit_spots': [(2022, 2013), (2086, 2013), (2022, 1949)], 'city_site': True},
    {'name': 'Thessaly', 'pop_limit': 2, 'unit_spots': [(1944, 1932), (2008, 1932), (1944, 1868)]},
    {'name': 'Thracia', 'pop_limit': 2, 'unit_spots': [(2072, 2171), (2136, 2171), (2072, 2107)]},
    {'name': 'Tingitana', 'pop_limit': 1, 'unit_spots': [(58, 948), (122, 948), (58, 884)]},
    {'name': 'Transalpine Gaul', 'pop_limit': 1, 'unit_spots': [(746, 2265), (810, 2265), (746, 2201)]},
    {'name': 'Troy', 'pop_limit': 2, 'unit_spots': [(2338, 2105), (2402, 2105), (2338, 2041)], 'city_site': True},
    {'name': 'Tyre', 'pop_limit': 3, 'unit_spots': [(3073, 1650), (3137, 1650), (3073, 1586)], 'city_site': True},
    {'name': 'Umbria', 'pop_limit': 3, 'unit_spots': [(1206, 2186), (1270, 2186), (1206, 2122)]},
    {'name': 'Upper Aegyptus', 'pop_limit': 4, 'unit_spots': [(2929, 964), (2993, 964), (2929, 900)], 'starting_nation': 'Egypt'},
    {'name': 'Upper Mesopotamia', 'pop_limit': 4, 'unit_spots': [(3201, 2135), (3265, 2135), (3201, 2071)]},
    {'name': 'Ur', 'pop_limit': 3, 'unit_spots': [(3846, 1861), (3910, 1861), (3846, 1797)], 'city_site': True},
    {'name': 'Valentia', 'pop_limit': 2, 'unit_spots': [(395, 1679), (459, 1679), (395, 1615)], 'city_site': True},
    {'name': 'Venedae', 'pop_limit': 1, 'unit_spots': [(1804, 2787), (1868, 2787), (1804, 2723)], 'starting_nation': 'Illyria'},
    {'name': 'Western Desert', 'pop_limit': 1, 'unit_spots': [(2538, 982), (2602, 982), (2538, 918)], 'starting_nation': 'Egypt'},
    {'name': 'Western Gaetulia', 'pop_limit': 1, 'unit_spots': [(1222, 931), (1286, 931), (1222, 867)], 'starting_nation': 'Africa'},
]

advciv_utility_list = [
    {'name': 'UnitStock', 'pop_limit': 55, 'unit_spots': [(1785, 615)]*10},
    {'name': 'CityStock', 'pop_limit': 9, 'unit_spots': [(1785, 535)] * 10},
    {'name': 'BoatStock', 'pop_limit': 4, 'unit_spots': [(1768, 455)] * 10, 'boat_spots': [(1768, 455)] * 10},
    {'name': 'Treasury', 'pop_limit': 55, 'unit_spots': [(1855, 215)] * 10},
    {'name': 'HiddenUnitStock', 'pop_limit': 55, 'unit_spots': [(1785, -615)]*10},
    {'name': 'HiddenCityStock', 'pop_limit': 9, 'unit_spots': [(1785, -535)] * 10},
    {'name': 'HiddenBoatStock', 'pop_limit': 4, 'unit_spots': [(1768, -455)] * 10, 'boat_spots': [(1768, -455)] * 10},
    {'name': 'HiddenTreasury', 'pop_limit': 55, 'unit_spots': [(1855, -215)] * 10}
]


class SnapMap:
    def __init__(self, ms, map_type='advciv'):
        self.territories = []
        self.ms = ms
        self.dims = (100.0, 100.0)
        if map_type == 'advciv':
            self.dims = (4058.0, 2910.0)
            for t in advciv_territory_list:
                self.territories.append(Territory(**t))
            for t in advciv_utility_list:
                self.territories.append(Territory(**t))

    def pos_to_hint(self, pos, dims=None):
        if not dims:
            dims = self.dims
        return {'x': pos[0]/dims[0], 'y': pos[1]/dims[1]}

    def size_to_hint(self, size, dims=None):
        if not dims:
            dims = self.dims
        return size[0] / dims[0], size[1] / dims[1]

    def map_to_window(self, map_pos, window_size=None, map_size=None):
        if window_size is None:
            window_size = self.ms.size
        if map_size is None:
            map_size = self.dims
        hint = self.pos_to_hint(map_pos, map_size)
        return hint['x'] * window_size[0], hint['y'] * window_size[1]

    def window_to_map(self, window_pos):
        return self.map_to_window(window_pos, self.dims, self.ms.size)

    def place_token_at_pos(self, token, window_pos):
        if isinstance(token, (UnitToken, CityToken, BoatToken)):
            map_pos = self.window_to_map(window_pos)

            def euclid_dist(ter):
                return abs(sqrt((ter.unit_spots[0][0]-map_pos[0])**2 + (ter.unit_spots[0][1]-map_pos[1])**2))
            territory = min(self.territories, key=euclid_dist)
            if isinstance(token, UnitToken) and territory.name in ['CityStock', 'BoatStock']:
                territory = [t for t in self.territories if t.name == 'UnitStock'][0]
            if isinstance(token, CityToken) and territory.name in ['UnitStock', 'BoatStock']:
                territory = [t for t in self.territories if t.name == 'CityStock'][0]
            if isinstance(token, BoatToken) and territory.name in ['CityStock', 'UnitStock']:
                territory = [t for t in self.territories if t.name == 'BoatStock'][0]
            self.place_token_in_territory(token, territory)

    def place_token_in_territory(self, token, territory):
        if isinstance(territory, str):
            territory = [t for t in self.territories if t.name == territory][0]
        if not isinstance(territory, Territory):
            raise Exception(f"territory must be a Territory object, the a Territory object's name. {territory}")
        if isinstance(token, (UnitToken, CityToken, BoatToken)):
            b, map_pos = territory.try_adding_token(token)
            if not b:
                if not token.territory:
                    raise Exception(f"Can't add token to its first territory! {token} of {token.nation} to {territory}")
                b, map_pos = token.territory.try_adding_token(token)
                if not b:
                    raise Exception(f"Can't add token to its current territory! {token} of {token.nation} to {token.territory.name}")
                territory = token.territory
            else:
                if token.territory:
                    token.territory.remove_token(token)
            # At this point, territory and map_pos are both definitely valid
            token.territory = territory
            token.pos_hint = self.pos_to_hint(map_pos)


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
        Color:
            rgba: tuple([x/255 for x in root.nation.color] + [.8]) if root.nation else (.5,.5,.5,.8)
        Ellipse:
            pos: self.pos
            size: self.size

<BoatToken>:
    canvas.before:
        Color:
            rgba: tuple([x/255 for x in root.nation.color] + [.8]) if root.nation else (.5,.5,.5,.8)
        Rectangle:
            pos: self.pos
            size: self.size

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

BoxLayout:
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
        # Here's a useful snippet for checking the map data:
        if True and (app.active_nation == self.text):
            print(len(app.nations[0].tokens))
            u = app.nations[0].tokens[0]
            for t in snap_map.territories:
                if t.pop_limit==1: # This is the relevant test condition
                    u = next(unit for unit in app.nations[0].tokens if
                         isinstance(unit, UnitToken) and unit.territory.name == 'UnitStock')
                    u.goto_territory(t)
            app.nations[0].label_tokens()
        # It will stick a unit token in whatever property you test for.
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


class Token(DragBehavior, Label):
    nation = ObjectProperty(None)
    active_nation = StringProperty('')
    hidden = False
    moving = False
    territory = ObjectProperty(None, allownone=True)

    def __init__(self, nation=None, hidden=False, territory=None, moving=False, **kwargs):
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
        snap_map.place_token_in_territory(self, territory)

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
            snap_map.place_token_at_pos(self, touch.pos)
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
            snap_map.place_token_at_pos(self, touch.pos)
            self.nation.label_tokens()
        return super(CityToken, self).on_touch_up(touch)


class BoatToken(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.moving:
            self.moving = False
            print(f'Released {self} at {touch.pos}')
            snap_map.place_token_at_pos(self, touch.pos)
            self.nation.label_tokens()
        return super(BoatToken, self).on_touch_up(touch)


class Spotter(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.moving:
            self.moving = False
            wp = snap_map.window_to_map(self.pos)
            x = round(wp[0])
            y = round(wp[1])
            print(f"'TERRITORY': {{'pop_limit': 1, 'nations': None, 'Prime': {x, y}, 'Alt': [{x+64,y},{x,y-64}]}},")
        super(Spotter, self).on_touch_up(touch)


class AstTokenWidget(Label):
    ast = NumericProperty(0)
    track = NumericProperty(0)
    color = ListProperty([0, 0, 0])
    target_size = 48

    def __init__(self, ast=0, track=0, color=[0, 0, 0], **kwargs):
        super(AstTokenWidget, self).__init__(**kwargs)
        self.ast = ast
        self.track = track
        self.color = color

    def refresh_pos(self):
        self.pos_hint['x'] = (208 + self.ast*60)/4058.0
        self.pos_hint['y'] = (28 + self.track*60)/2910.0   
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


class Nation:
    num_units = 55
    name = 'Unnamed'
    color = [0, 0, 0]
    track = 0
    fl = None
    units_in_location = {}
    boats_in_location = {}
    cities_in_location = {}
    unit_icon = 'default_unit_icon.png'

    def __init__(self, name, color, track, fl, unit_icon, num_units=55, **kwargs):
        self.name = name
        self.color = color
        self.track = track
        self.fl = fl
        self.num_units = num_units
        self.unit_icon = unit_icon
        for location in [t.name for t in snap_map.territories]:
            self.units_in_location[location] = 0
            self.boats_in_location[location] = 0
            self.cities_in_location[location] = 0

        self.ast_token = AstTokenWidget(ast=0,
                                        track=self.track,
                                        color=self.color)
        fl.add_widget(self.ast_token)

        self.nation_button = NationButton(size_hint=(180.0/4058.0, 60.0/2910.0),
                                          pos_hint={'x': 19.0/4058.0, 'y': (22.0+self.track*60.0)/2910.0},
                                          text=self.name,
                                          color=(0,0,0,.01),
                                          background_color=(0,0,0,.01))
        fl.add_widget(self.nation_button)
                           
        self.tokens = []

        for i in range(num_units):
            token = UnitToken(nation=self, hidden=True, territory='HiddenUnitStock',
                              size_hint=snap_map.size_to_hint((60, 60)))
            self.fl.add_widget(token)
            self.units_in_location['HiddenUnitStock'] = self.units_in_location['HiddenUnitStock'] + 1
            self.tokens.append(token)

        for i in range(9):
            city = CityToken(nation=self, hidden=True, territory='HiddenCityStock',
                             size_hint=snap_map.size_to_hint((60, 60)))
            self.fl.add_widget(city)
            self.units_in_location['HiddenCityStock'] += 1
            self.tokens.append(city)
        
        for i in range(4):
            boat = BoatToken(nation=self, hidden=True, territory='HiddenBoatStock',
                             size_hint=snap_map.size_to_hint((93, 60)))
            self.fl.add_widget(boat)
            self.units_in_location['HiddenBoatStock'] += 1
            self.tokens.append(boat)
        
        self.label_tokens()

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

    def show_or_hide_stock(self):
        active_nation = App.get_running_app().active_nation
        if active_nation == self.name: 
            print(f'Showing tokens in {self.name}, active_nation={active_nation}')           
            for token in self.tokens:
                if token.territory.name in ['HiddenUnitStock', 'HiddenCityStock', 'HiddenBoatStock', 'HiddenTreasury']:
                    token.show()
        else:
            print(f'Hiding tokens in {self.name}, active_nation={active_nation}')
            for token in self.tokens:
                if token.territory.name in ['UnitStock', 'CityStock', 'BoatStock', 'Treasury']:
                    token.hide()

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
        self.nations.append(Nation('Africa', [186, 96, 41], 9, fl, 'africa_token_icon3.png', 75))
        #self.nations.append(Nation('Italy', [252, 0, 0], 8, fl, 'italy_token_icon.png', 55))
        return root

TestApp().run()
