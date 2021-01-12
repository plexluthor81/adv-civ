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

class SnapMap():
    map_locations = {'Great Erg': {'pop_limit': 1, 'nations': None, 'Prime': (680, 965), 'Alt': [(744,965),(680,901)]},
                     'Western Gaetulia': {'pop_limit': 1, 'nations': None, 'Prime': (1222, 931), 'Alt': [(1286,931),(1222,867)]},
                     'Garamantes': {'pop_limit': 1, 'nations': None, 'Prime': (1613, 897), 'Alt': [(1677,897),(1549,897)]},
                     'Leptis Magna': {'pop_limit': 1, 'nations': None, 'Prime': (1541, 1114), 'Alt': [(1605,1114),(1541,1050)]},
                     'Libya': {'pop_limit': 1, 'nations': None, 'Prime': (1256, 1137), 'Alt': [(1256,1073),(1320,1073)]},
                     'Numidia': {'pop_limit': 1, 'nations': None, 'Prime': (1018, 1195), 'Alt': [(1082,1195),(1018,1131)]},
                     'Thapsos': {'pop_limit': 1, 'nations': None, 'Prime': (1193, 1340), 'Alt': [(1257, 1340),(1193, 1276)]},
                     'Carthage': {'pop_limit': 1, 'nations': None, 'Prime': (1174, 1515), 'Alt': [(1238, 1515),(1174, 1451)]},
                     'Hippo Regius': {'pop_limit': 1, 'nations': None, 'Prime': (1021, 1452), 'Alt': [(1021, 1516),(1021, 1388)]},
                     'Cirta': {'pop_limit': 1, 'nations': None, 'Prime': (856, 1397), 'Alt': [(920, 1397),(856, 1333)]},
                     'Sitifensis': {'pop_limit': 1, 'nations': None, 'Prime': (645, 1359), 'Alt': [(709, 1359),(645, 1295)]},
                     'Caesariensis': {'pop_limit': 1, 'nations': None, 'Prime': (423, 1288), 'Alt': [(487, 1288),(423, 1224)]},
                     'Mauretania': {'pop_limit': 1, 'nations': None, 'Prime': (146, 1258), 'Alt': [(210, 1258),(146, 1194)]},
                     'Tingitana': {'pop_limit': 1, 'nations': None, 'Prime': (58, 948), 'Alt': [(122, 948),(58, 884)]},
                     'Cirenaica': {'pop_limit': 1, 'nations': None, 'Prime': (1812, 1052), 'Alt': [(1876, 1052),(1812, 988)]},
                     'Cyrene': {'pop_limit': 3, 'nations': None, 'Prime': (2028, 1235), 'Alt': [(2092, 1235),(2028, 1171)]},
                     'Marmarica': {'pop_limit': 2, 'nations': None, 'Prime': (2354, 1265), 'Alt': [(2418, 1265),(2354, 1201)]},
                     'Eastern Gaetulia': {'pop_limit': 1, 'nations': None, 'Prime': (2214, 976), 'Alt': [(2278, 976),(2214, 912)]},
                     'Western Desert': {'pop_limit': 1, 'nations': None, 'Prime': (2538, 982), 'Alt': [(2602, 982),(2538, 918)]},
                     'Siwa Oasis': {'pop_limit': 2, 'nations': None, 'Prime': (2634, 1226), 'Alt': [(2698, 1226),(2634, 1162)]},
                     'Alexandria': {'pop_limit': 4, 'nations': None, 'Prime': (2765, 1366), 'Alt': [(2829, 1366),(2765, 1302)]},
                     'Tanis': {'pop_limit': 3, 'nations': None, 'Prime': (2876, 1408), 'Alt': [(2940, 1408),(2876, 1344)]},
                     'Memphis': {'pop_limit': 3, 'nations': None, 'Prime': (2848, 1267), 'Alt': [(2912, 1267),(2848, 1203)]},
                     'Eastern Desert': {'pop_limit': 1, 'nations': None, 'Prime': (3006, 1221), 'Alt': [(3070, 1221),(3006, 1157)]},
                     'Abydos': {'pop_limit': 5, 'nations': None, 'Prime': (2867, 1118), 'Alt': [(2931, 1118),(2867, 1054)]},
                     'Upper Aegyptus': {'pop_limit': 4, 'nations': None, 'Prime': (2929, 964), 'Alt': [(2993, 964),(2929, 900)]},
                     'Swenett': {'pop_limit': 3, 'nations': None, 'Prime': (3093, 918), 'Alt': [(3157, 918),(3093, 854)]},
                     'Thebes': {'pop_limit': 3, 'nations': None, 'Prime': (3219, 928), 'Alt': [(3283, 928),(3219, 864)]},
                     'Kush': {'pop_limit': 1, 'nations': None, 'Prime': (3406, 920), 'Alt': [(3470, 920),(3406, 856)]},
                     'Nubia': {'pop_limit': 2, 'nations': None, 'Prime': (3149, 1106), 'Alt': [(3213, 1106),(3149, 1042)]},
                     'Nabataei': {'pop_limit': 1, 'nations': None, 'Prime': (3495, 1188), 'Alt': [(3559, 1188),(3495, 1124)]},
                     'Petra': {'pop_limit': 1, 'nations': None, 'Prime': (3248, 1410), 'Alt': [(3312, 1410),(3248, 1346)]},
                     'Sinai': {'pop_limit': 1, 'nations': None, 'Prime': (3075, 1339), 'Alt': [(3139, 1339),(3075, 1275)]},
                     'Pelusium': {'pop_limit': 1, 'nations': None, 'Prime': (2979, 1456), 'Alt': [(3043, 1456),(2979, 1392)]},
                     'Gaza': {'pop_limit': 2, 'nations': None, 'Prime': (3058, 1524), 'Alt': [(3122, 1524),(3058, 1460)]},
                     'Jerusalem': {'pop_limit': 1, 'nations': None, 'Prime': (3228, 1575), 'Alt': [(3292, 1575),(3228, 1511)]},
                     'Tyre': {'pop_limit': 3, 'nations': None, 'Prime': (3073, 1650), 'Alt': [(3137, 1650),(3073, 1586)]},
                     'Arabia': {'pop_limit': 1, 'nations': None, 'Prime': (3680, 1504), 'Alt': [(3744, 1504),(3680, 1440)]},
                     'Mari': {'pop_limit': 3, 'nations': None, 'Prime': (3397, 1725), 'Alt': [(3461, 1725),(3397, 1661)]},
                     'Damascus': {'pop_limit': 2, 'nations': None, 'Prime': (3189, 1745), 'Alt': [(3253, 1745),(3189, 1681)]},
                     'Sidon': {'pop_limit': 1, 'nations': None, 'Prime': (3027, 1730), 'Alt': [(3091, 1730),(3027, 1666)]},
                     'Byblos': {'pop_limit': 3, 'nations': None, 'Prime': (3103, 1845), 'Alt': [(3167, 1845),(3103, 1781)]},
                     'Antioch': {'pop_limit': 2, 'nations': None, 'Prime': (2996, 1932), 'Alt': [(3060, 1932),(2996, 1868)]},
                     'Nisibis': {'pop_limit': 2, 'nations': None, 'Prime': (3472, 1932), 'Alt': [(3536, 1932),(3472, 1868)]},
                     'Akkadia': {'pop_limit': 3, 'nations': None, 'Prime': (3660, 1867), 'Alt': [(3724, 1867),(3660, 1803)]},
                     'Sumeria': {'pop_limit': 2, 'nations': None, 'Prime': (3963, 1745), 'Alt': [(4027, 1745),(3963, 1681)]},
                     'Ur': {'pop_limit': 3, 'nations': None, 'Prime': (3846, 1861), 'Alt': [(3910, 1861),(3846, 1797)]},
                     'Babylon': {'pop_limit': 3, 'nations': None, 'Prime': (3857, 1988), 'Alt': [(3921, 1988),(3857, 1924)]},
                     'Ctesiphon': {'pop_limit': 2, 'nations': None, 'Prime': (3734, 1990), 'Alt': [(3798, 1990),(3734, 1926)]},
                     'Mesopotamia': {'pop_limit': 3, 'nations': None, 'Prime': (3571, 2056), 'Alt': [(3635, 2056),(3571, 1992)]},
                     'Ashur': {'pop_limit': 3, 'nations': None, 'Prime': (3405, 2128), 'Alt': [(3469, 2128),(3405, 2064)]},
                     'Upper Mesopotamia': {'pop_limit': 4, 'nations': None, 'Prime': (3201, 2135), 'Alt': [(3265, 2135),(3201, 2071)]},
                     'Aleppo': {'pop_limit': 2, 'nations': None, 'Prime': (3125, 1979), 'Alt': [(3189, 1979),(3125, 1915)]},
                     'Mitanni': {'pop_limit': 2, 'nations': None, 'Prime': (2998, 2093), 'Alt': [(3062, 2093),(2998, 2029)]},
                     'Kanesh': {'pop_limit': 2, 'nations': None, 'Prime': (2886, 2143), 'Alt': [(2950, 2143),(2886, 2079)]},
                     'Cilicia': {'pop_limit': 2, 'nations': None, 'Prime': (2752, 1955), 'Alt': [(2816, 1955),(2752, 1891)]},
                     'Cyprus': {'pop_limit': 2, 'nations': None, 'Prime': (2808, 1762), 'Alt': [(2872, 1762),(2808, 1698)]},
                     'Salamis': {'pop_limit': 1, 'nations': None, 'Prime': (2904, 1837), 'Alt': [(2968, 1837),(2904, 1773)]},
                     'Parthia': {'pop_limit': 4, 'nations': None, 'Prime': (3751, 2147), 'Alt': [(3815, 2147),(3751, 2083)]},
                     'Susa': {'pop_limit': 3, 'nations': None, 'Prime': (3960, 2118), 'Alt': [(4024, 2118),(3960, 2054)]},
                     'Persia': {'pop_limit': 2, 'nations': None, 'Prime': (3924, 2342), 'Alt': [(3988, 2342),(3924, 2278)]},
                     'Assyria': {'pop_limit': 3, 'nations': None, 'Prime': (3697, 2358), 'Alt': [(3761, 2358),(3697, 2294)]},
                     'Ninevah': {'pop_limit': 3, 'nations': None, 'Prime': (3442, 2328), 'Alt': [(3506, 2328),(3442, 2264)]},
                     'Scythia': {'pop_limit': 2, 'nations': None, 'Prime': (3891, 2564), 'Alt': [(3955, 2564),(3891, 2500)]},
                     'Maedia': {'pop_limit': 1, 'nations': None, 'Prime': (3621, 2592), 'Alt': [(3685, 2592),(3621, 2528)]},
                     'Albania': {'pop_limit': 1, 'nations': None, 'Prime': (3528, 2809), 'Alt': [(3592, 2809),(3528, 2745)]},
                     'Armenia': {'pop_limit': 3, 'nations': None, 'Prime': (3364, 2591), 'Alt': [(3428, 2591),(3364, 2527)]},
                     'Georgia': {'pop_limit': 1, 'nations': None, 'Prime': (3118, 2578), 'Alt': [(3182, 2578),(3118, 2514)]},
                     'Alani': {'pop_limit': 1, 'nations': None, 'Prime': (3200, 2779), 'Alt': [(3264, 2779),(3200, 2715)]},
                     'Caucasus': {'pop_limit': 2, 'nations': None, 'Prime': (2963, 2755), 'Alt': [(3027, 2755),(2963, 2691)]},
                     'Sindica': {'pop_limit': 1, 'nations': None, 'Prime': (2761, 2765), 'Alt': [(2825, 2765),(2761, 2701)]},
                     'Taurica': {'pop_limit': 2, 'nations': None, 'Prime': (2518, 2675), 'Alt': [(2582, 2675),(2518, 2611)]},
                     'Sarmatia': {'pop_limit': 3, 'nations': None, 'Prime': (2214, 2798), 'Alt': [(2278, 2798),(2214, 2734)]},
                     'Dacia Inferior': {'pop_limit': 5, 'nations': None, 'Prime': (2039, 2511), 'Alt': [(2103, 2511),(2039, 2447)]},
                     'Constanta': {'pop_limit': 2, 'nations': None, 'Prime': (2237, 2495), 'Alt': [(2301, 2495),(2237, 2431)]},
                     'Odessos': {'pop_limit': 4, 'nations': None, 'Prime': (2137, 2321), 'Alt': [(2201, 2321),(2137, 2257)]},
                     'Byzantium': {'pop_limit': 3, 'nations': None, 'Prime': (2260, 2183), 'Alt': [(2324, 2183),(2260, 2119)]},
                     'Thracia': {'pop_limit': 2, 'nations': None, 'Prime': (2072, 2171), 'Alt': [(2136, 2171),(2072, 2107)]},
                     'Lemnos': {'pop_limit': 1, 'nations': None, 'Prime': (2136, 2027), 'Alt': [(2200, 2027),(2136, 1963)]},
                     'Troy': {'pop_limit': 2, 'nations': None, 'Prime': (2338, 2105), 'Alt': [(2402, 2105),(2338, 2041)]},
                     'Galatia': {'pop_limit': 2, 'nations': None, 'Prime': (2530, 2242), 'Alt': [(2594, 2242),(2530, 2178)]},
                     'Sardes': {'pop_limit': 2, 'nations': None, 'Prime': (2356, 1995), 'Alt': [(2420, 1995),(2356, 1931)]},
                     'Lesbos': {'pop_limit': 1, 'nations': None, 'Prime': (2225, 1929), 'Alt': [(2289, 1929),(2225, 1865)]},
                     'Ionia': {'pop_limit': 3, 'nations': None, 'Prime': (2487, 1965), 'Alt': [(2551, 1965),(2487, 1901)]},
                     'Miletus': {'pop_limit': 1, 'nations': None, 'Prime': (2430, 1833), 'Alt': [(2494, 1833),(2430, 1769)]},
                     'Rhodes': {'pop_limit': 2, 'nations': None, 'Prime': (2443, 1744), 'Alt': [(2507, 1744),(2443, 1680)]},
                     'Lycia': {'pop_limit': 1, 'nations': None, 'Prime': (2585, 1822), 'Alt': [(2649, 1822),(2585, 1758)]},
                     'Gordium': {'pop_limit': 2, 'nations': None, 'Prime': (2601, 2094), 'Alt': [(2665, 2094),(2601, 2030)]},
                     'Anatolia': {'pop_limit': 1, 'nations': None, 'Prime': (2647, 2364), 'Alt': [(2711, 2364),(2647, 2300)]},
                     'Pontus': {'pop_limit': 2, 'nations': None, 'Prime': (2942, 2435), 'Alt': [(3006, 2435),(2942, 2371)]},
                     'Ancyra': {'pop_limit': 2, 'nations': None, 'Prime': (2781, 2261), 'Alt': [(2845, 2261),(2781, 2197)]},
                     'Cappadocia': {'pop_limit': 3, 'nations': None, 'Prime': (3151, 2349), 'Alt': [(3215, 2349),(3151, 2285)]},
                     'Knossus': {'pop_limit': 3, 'nations': None, 'Prime': (2327, 1613), 'Alt': [(2391, 1613),(2327, 1549)]},
                     'Phastos': {'pop_limit': 2, 'nations': None, 'Prime': (2192, 1592), 'Alt': [(2256, 1592),(2192, 1528)]},
                     'Sparta': {'pop_limit': 1, 'nations': None, 'Prime': (1986, 1677), 'Alt': [(2050, 1677),(1986, 1613)]},
                     'Mycenae': {'pop_limit': 1, 'nations': None, 'Prime': (2066, 1723), 'Alt': [(2130, 1723),(2066, 1659)]},
                     'Athens': {'pop_limit': 2, 'nations': None, 'Prime': (2104, 1787), 'Alt': [(2168, 1787),(2104, 1723)]},
                     'Corinth': {'pop_limit': 2, 'nations': None, 'Prime': (1947, 1767), 'Alt': [(2011, 1767),(1947, 1703)]},
                     'Aetolia': {'pop_limit': 2, 'nations': None, 'Prime': (1933, 1835), 'Alt': [(1997, 1835),(1933, 1771)]},
                     'Delos': {'pop_limit': 2, 'nations': None, 'Prime': (2230, 1712), 'Alt': [(2294, 1712),(2230, 1648)]},
                     'Eretria': {'pop_limit': 1, 'nations': None, 'Prime': (2143, 1838), 'Alt': [(2207, 1838),(2143, 1774)]},
                     'Chalcis': {'pop_limit': 2, 'nations': None, 'Prime': (2070, 1884), 'Alt': [(2134, 1884),(2070, 1820)]},
                     'Thessaly': {'pop_limit': 2, 'nations': None, 'Prime': (1944, 1932), 'Alt': [(2008, 1932),(1944, 1868)]},
                     'Thessalonica': {'pop_limit': 1, 'nations': None, 'Prime': (2022, 2013), 'Alt': [(2086, 2013),(2022, 1949)]},
                     'Macedonia': {'pop_limit': 1, 'nations': None, 'Prime': (1893, 2088), 'Alt': [(1957, 2088),(1893, 2024)]},
                     'Moesia Superior': {'pop_limit': 1, 'nations': None, 'Prime': (1845, 2219), 'Alt': [(1909, 2219),(1845, 2155)]},
                     'Apollonia': {'pop_limit': 1, 'nations': None, 'Prime': (1739, 2042), 'Alt': [(1803, 2042),(1739, 1978)]},
                     'Ithaca': {'pop_limit': 1, 'nations': None, 'Prime': (1759, 1868), 'Alt': [(1823, 1868),(1759, 1804)]},
                     'Dalmatia': {'pop_limit': 2, 'nations': None, 'Prime': (1657, 2240), 'Alt': [(1721, 2240),(1657, 2176)]},
                     'Dacia Superior': {'pop_limit': 3, 'nations': None, 'Prime': (1780, 2554), 'Alt': [(1844, 2554),(1780, 2490)]},
                     'Venedae': {'pop_limit': 1, 'nations': None, 'Prime': (1804, 2787), 'Alt': [(1868, 2787),(1804, 2723)]},
                     'Germania Magna': {'pop_limit': 5, 'nations': None, 'Prime': (1299, 2747), 'Alt': [(1363, 2747),(1299, 2683)]},
                     'Pannonia': {'pop_limit': 4, 'nations': None, 'Prime': (1318, 2478), 'Alt': [(1382, 2478),(1318, 2414)]},
                     'Illyria': {'pop_limit': 2, 'nations': None, 'Prime': (1449, 2233), 'Alt': [(1513, 2233),(1449, 2169)]},
                     'Umbria': {'pop_limit': 3, 'nations': None, 'Prime': (1206, 2186), 'Alt': [(1270, 2186),(1206, 2122)]},
                     'Samnium': {'pop_limit': 2, 'nations': None, 'Prime': (1420, 2030), 'Alt': [(1484, 2030),(1420, 1966)]},
                     'Tarrentum': {'pop_limit': 1, 'nations': None, 'Prime': (1610, 1925), 'Alt': [(1674, 1925),(1610, 1861)]},
                     'Lucani': {'pop_limit': 2, 'nations': None, 'Prime': (1515, 1832), 'Alt': [(1579, 1832),(1515, 1768)]},
                     'Capua': {'pop_limit': 1, 'nations': None, 'Prime': (1345, 1938), 'Alt': [(1409, 1938),(1345, 1874)]},
                     'Rome': {'pop_limit': 2, 'nations': None, 'Prime': (1180, 2036), 'Alt': [(1244, 2036),(1180, 1972)]},
                     'Corsica': {'pop_limit': 1, 'nations': None, 'Prime': (997, 2007), 'Alt': [(1061, 2007),(997, 1943)]},
                     'Oblia': {'pop_limit': 1, 'nations': None, 'Prime': (1001, 1861), 'Alt': [(1065, 1861),(1001, 1797)]},
                     'Sardinia': {'pop_limit': 1, 'nations': None, 'Prime': (1023, 1746), 'Alt': [(1087, 1746),(1023, 1682)]},
                     'Sicilia': {'pop_limit': 2, 'nations': None, 'Prime': (1453, 1675), 'Alt': [(1517, 1675),(1453, 1611)]},
                     'Lilybaeum': {'pop_limit': 2, 'nations': None, 'Prime': (1342, 1611), 'Alt': [(1406, 1611),(1342, 1547)]},
                     'Syracuse': {'pop_limit': 1, 'nations': None, 'Prime': (1487, 1568), 'Alt': [(1551, 1568),(1487, 1504)]},
                     'Genua': {'pop_limit': 2, 'nations': None, 'Prime': (899, 2140), 'Alt': [(963, 2140),(899, 2076)]},
                     'Cisalpine Gaul': {'pop_limit': 2, 'nations': None, 'Prime': (1030, 2241), 'Alt': [(1094, 2241),(1030, 2177)]},
                     'Helvetii': {'pop_limit': 1, 'nations': None, 'Prime': (881, 2356), 'Alt': [(945, 2356),(881, 2292)]},
                     'Noricum': {'pop_limit': 1, 'nations': None, 'Prime': (1031, 2390), 'Alt': [(1095, 2390),(1031, 2326)]},
                     'Germanica Superior': {'pop_limit': 1, 'nations': None, 'Prime': (919, 2543), 'Alt': [(983, 2543),(919, 2479)]},
                     'Sequani': {'pop_limit': 1, 'nations': None, 'Prime': (812, 2531), 'Alt': [(876, 2531),(812, 2467)]},
                     'Transalpine Gaul': {'pop_limit': 1, 'nations': None, 'Prime': (746, 2265), 'Alt': [(810, 2265),(746, 2201)]},
                     'Massilia': {'pop_limit': 3, 'nations': None, 'Prime': (746, 2108), 'Alt': [(810, 2108),(746, 2044)]},
                     'Teutoburg': {'pop_limit': 3, 'nations': None, 'Prime': (822, 2813), 'Alt': [(886, 2813),(822, 2749)]},
                     'Belgica': {'pop_limit': 3, 'nations': None, 'Prime': (637, 2628), 'Alt': [(701, 2628),(637, 2564)]},
                     'Gallia Lugdunensis': {'pop_limit': 3, 'nations': None, 'Prime': (436, 2366), 'Alt': [(500, 2366),(436, 2302)]},
                     'Armorica': {'pop_limit': 1, 'nations': None, 'Prime': (220, 2510), 'Alt': [(284, 2510),(220, 2446)]},
                     'Brittania': {'pop_limit': 2, 'nations': None, 'Prime': (346, 2778), 'Alt': [(410, 2778),(346, 2714)]},
                     'Silures': {'pop_limit': 1, 'nations': None, 'Prime': (145, 2827), 'Alt': [(209, 2827),(145, 2763)]},
                     'Narbonensis': {'pop_limit': 2, 'nations': None, 'Prime': (583, 2005), 'Alt': [(647, 2005),(583, 1941)]},
                     'Edetania': {'pop_limit': 1, 'nations': None, 'Prime': (475, 1842), 'Alt': [(539, 1842),(475, 1778)]},
                     'Aquitania': {'pop_limit': 1, 'nations': None, 'Prime': (332, 2049), 'Alt': [(396, 2049),(332, 1985)]},
                     'Gallaecia': {'pop_limit': 1, 'nations': None, 'Prime': (98, 1992), 'Alt': [(162, 1992),(98, 1928)]},
                     'Lusitania': {'pop_limit': 1, 'nations': None, 'Prime': (94, 1741), 'Alt': [(158, 1741),(94, 1677)]},
                     'Celtiberi': {'pop_limit': 1, 'nations': None, 'Prime': (281, 1824), 'Alt': [(345, 1824),(281, 1760)]},
                     'Valentia': {'pop_limit': 2, 'nations': None, 'Prime': (395, 1679), 'Alt': [(459, 1679),(395, 1615)]},
                     'Gades': {'pop_limit': 2, 'nations': None, 'Prime': (183, 1556), 'Alt': [(247, 1556),(183, 1492)]},
                     'Balearic Islands': {'pop_limit': 1, 'nations': None, 'Prime': (578, 1720), 'Alt': [(642, 1720),(578, 1656)]},
                     'Mahon': {'pop_limit': 1, 'nations': None, 'Prime': (730, 1770), 'Alt': [(794, 1770),(730, 1706)]},
                     'Stock': {'pop_limit': 55, 'nations': None, 'Prime': (1785, 615), 'Alt': []},
                     'CityStock': {'pop_limit': 9, 'nations': None, 'Prime': (1785, 535), 'Alt': []},
                     'BoatStock': {'pop_limit': 4, 'nations': None, 'Prime': (1768, 455), 'Alt': []},
                     'Treasury': {'pop_limit': 55, 'nations': None, 'Prime': (1855, 215), 'Alt': []},
                     'HiddenStock': {'pop_limit': 55, 'nations': None, 'Prime': (1768, -535), 'Alt': []},
                     'HiddenCityStock': {'pop_limit': 9, 'nations': None, 'Prime': (1768, -435), 'Alt': []},
                     'HiddenBoatStock': {'pop_limit': 4, 'nations': None, 'Prime': (1768, -335), 'Alt': []},
                     'HiddenTreasury': {'pop_limit': 55, 'nations': None, 'Prime': (1768, -235), 'Alt': []} }

    def get_snap_pos(self, window_pos, type='Token'):
        pos = window_to_map(window_pos)
        territory = min(self.map_locations.keys(), key=lambda t: abs(sqrt((self.map_locations[t]['Prime'][0]-pos[0])**2 + (self.map_locations[t]['Prime'][1]-pos[1])**2)))
        if type=='Token' and territory in ['CityStock','BoatStock']:
            territory = 'Stock'
        if type=='City' and territory in ['Stock', 'BoatStock', 'Treasury']:
            territory = 'CityStock'
        if type=='Boat' and territory in ['Stock', 'Treasury', 'CityStock']:
            territory = 'BoatStock'
        map_pos = self.map_locations[territory]['Prime']
        print(f'{territory} {map_pos[0]+64,map_pos[1]},{map_pos[0],map_pos[1]-64}')
        return territory, map_to_window(map_pos)
   

snap_map = SnapMap()

def pos_to_hint(pos, dims=(4058.0, 2910.0)):
    return {'x':pos[0]/dims[0], 'y':pos[1]/dims[1]}

def size_to_hint(size, dims=(4058.0, 2910.0)):
    return (size[0]/dims[0], size[1]/dims[1])

def map_to_window(map_pos, window_size=None, map_size=(4058.0, 2910.0)):
    if window_size is None:
        window_size = App.get_running_app().root.ids['ms'].size
    hint = pos_to_hint(map_pos, map_size)
    return (hint['x']*window_size[0], hint['y']*window_size[1])

def window_to_map(window_pos):
    return map_to_window(window_pos, (4058.0, 2910.0), App.get_running_app().root.ids['ms'].size)
    

class NationButton(Button):
    def on_press(self):
        app = App.get_running_app()
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
    territory = StringProperty('')

    def __init__(self, nation=None, hidden=False, territory='', **kwargs):
        super(Token, self).__init__(**kwargs)
        self.nation = nation
        self.hidden = hidden
        self.territory = territory
    
    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos) and self.nation and self.nation.name==self.active_nation:
            self.pos_hint = {}
            self.territory = 'Moving'
            self.nation.label_tokens()
        return super(Token, self).on_touch_down(touch)

    def goto_territory(self, territory):
        self.territory = territory
        self.pos = map_to_window(snap_map.map_locations[territory]['Prime'])
        self.pos_hint = pos_to_hint(self.pos, self.parent.size)

    def hide(self):
        if self.hidden:
            return
        self.hidden = True
        if self.territory == 'Stock':
            self.goto_territory('HiddenStock')
        if self.territory == 'CityStock':
            self.goto_territory('HiddenCityStock')
        if self.territory == 'BoatStock':
            self.goto_territory('HiddenBoatStock')
        if self.territory == 'Treasury':
            self.goto_territory('HiddenTreasury')

    def show(self):
        if not self.hidden:
            return
        self.hidden = False
        if self.territory == 'HiddenStock':
            self.goto_territory('Stock')
        if self.territory == 'HiddenCityStock':
            self.goto_territory('CityStock')
        if self.territory == 'HiddenBoatStock':
            self.goto_territory('BoatStock')
        if self.territory == 'HiddenTreasury':
            self.goto_territory('Treasury')

class UnitToken(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            snap_ter, snap_pos = snap_map.get_snap_pos(self.pos)
            self.territory = snap_ter
            self.pos = snap_pos
            self.pos_hint = pos_to_hint(self.pos, self.parent.size)
            self.nation.label_tokens()
        return super(UnitToken, self).on_touch_up(touch)

class CityToken(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            snap_ter, snap_pos = snap_map.get_snap_pos(self.pos, 'City')
            self.territory = snap_ter
            self.pos = snap_pos
            self.pos_hint = pos_to_hint(self.pos, self.parent.size)
            self.nation.build_city(snap_ter)
        return super(CityToken, self).on_touch_up(touch)

class BoatToken(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            snap_ter, snap_pos = snap_map.get_snap_pos(self.pos, 'Boat')
            self.territory = snap_ter
            self.pos = snap_pos
            self.pos_hint = pos_to_hint(self.pos, self.parent.size)
        return super(BoatToken, self).on_touch_up(touch)

class Spotter(Token):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            wp = window_to_map(self.pos)
            x = round(wp[0])
            y = round(wp[1])
            print(f"'TERRITORY': {{'pop_limit': 1, 'nations': None, 'Prime': {x, y}, 'Alt': [{x+64,y},{x,y-64}]}},")
        super(Spotter,self).on_touch_up(touch)

class AstTokenWidget(Label):
    ast = NumericProperty(0)
    track = NumericProperty(0)
    color = ListProperty([0, 0, 0])
    target_size = 48

    def __init__(self, ast=0, track=0, color=[0,0,0], **kwargs):
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
    unit_icon = 'default_unit_icon.png'

    def __init__(self, name, color, track, fl, unit_icon, num_units=55, **kwargs):
        self.name = name
        self.color = color
        self.track = track
        self.fl = fl
        self.num_units = num_units
        self.unit_icon = unit_icon
        for location in snap_map.map_locations.keys():
            self.units_in_location[location] = 0

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
            token = UnitToken(nation=self, hidden=True, territory='HiddenStock',
                              pos_hint=pos_to_hint(snap_map.map_locations['HiddenStock']['Prime']),
                              size_hint=size_to_hint((60,60)))
            self.fl.add_widget(token)
            self.units_in_location['HiddenStock'] += 1
            self.tokens.append(token)

        for i in range(9):
            city = CityToken(nation=self, hidden=True, territory='HiddenCityStock',
                             size_hint=size_to_hint((60,60)),
                             pos_hint=pos_to_hint(snap_map.map_locations['HiddenCityStock']['Prime']))
            self.fl.add_widget(city)
            self.units_in_location['HiddenCityStock'] += 1
            self.tokens.append(city)
        
        for i in range(4):
            boat = BoatToken(nation=self, hidden=True, territory='HiddenBoatStock',
                             size_hint=size_to_hint((93,60)),
                             pos_hint=pos_to_hint(snap_map.map_locations['HiddenBoatStock']['Prime']))
            self.fl.add_widget(boat)
            self.units_in_location['HiddenBoatStock'] += 1
            self.tokens.append(boat)
        
        self.label_tokens()
                             

    def update_locations(self, *args):
        print(f'Should be updating locations for {self.name}')

    def label_tokens(self):
        units_in_location = {}
        for token in self.tokens:
            if token.territory in units_in_location.keys():
                units_in_location[token.territory] += 1
            else:
                units_in_location[token.territory] = 1
        for token in self.tokens:
            if units_in_location[token.territory] > 1:
                token.text = str(units_in_location[token.territory])
            else:
                token.text = ''
        self.units_in_location = units_in_location

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
                if token.territory in ['HiddenStock', 'HiddenCityStock', 'HiddenBoatStock', 'HiddenTreasury']:
                    token.show()
        else:
            print(f'Hiding tokens in {self.name}, active_nation={active_nation}')
            for token in self.tokens:
                if token.territory in ['Stock', 'CityStock', 'BoatStock', 'Treasury']:
                    token.hide()

colors = {'Africa': [186, 96, 41], 'Italy': [252, 0, 0], 'Illyria': [245,239,7],
          'Thrace': [67,177,30], 'Crete': [102,201,29], 'Asia': [243,146,51],
          'Assyria': [61,185,209], 'Babylon': [145,245,244], 'Egypt': [212,198,137],
          'Phoenecia': [155,10,180]}

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
        self.nations.append(Nation('Africa', [186, 96, 41], 9, fl, 'africa_token_icon3.png', 55))
        self.nations.append(Nation('Italy', [252, 0, 0], 8, fl, 'italy_token_icon.png', 55))
        return root

TestApp().run()
