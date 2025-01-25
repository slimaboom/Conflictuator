from model.sector import Sector
from model.point import Point
from model.balise import Balise, DatabaseBalise
from model.route import Airway

#------------------------------------------------------------------------------
#--------- Definition  des secteurs: principal et secondaires -----------------
#------------------------------------------------------------------------------
MAIN_SECTOR = Sector(
name='MAIN_SECTOR', 
points=[
    Point(0.739454094292804, 1-0.5239968528717546),
    Point(0.6060794044665012, 1-0.7269866247049567),
    Point(0.5893300248138957, 1-0.7765538945712038),
    Point(0.5074441687344913, 1-0.7254130605822188),
    Point(0.2704714640198511, 1-0.7246262785208497),
    Point(0.25806451612903225, 1-0.44531864673485444),
    Point(0.5272952853598015, 1-0.1880409126671912),
    Point(0.5403225806451613, 1-0.2077104642014162),
    Point(0.5359801488833746, 1-0.21321793863099922),
    Point(0.532258064516129, 1-0.21951219512195122),
    Point(0.5285359801488834, 1-0.23210070810385522),
    Point(0.5310173697270472, 1-0.24547600314712825),
    Point(0.5359801488833746, 1-0.2549173878835563),
    Point(0.5421836228287841, 1-0.26435877261998425),
    Point(0.5825062034739454, 1-0.25413060582218727),
    Point(0.6464019851116626, 1-0.34775767112509837),
    Point(0.6941687344913151, 1-0.45790715971675844),
])

SECONDARY_SECTOR = Sector()
SECONDARY_SECTOR.add(
    key='N3N2', 
    value=[Point(0.0006203473945409429, 1-0.34067663257277736), 
            Point(0, 1-0.2840283241542093), 
            Point(0.23883374689826303, 1-0.12273800157356413), 
            Point(0.5248138957816377, 1-0.0007867820613690008), 
            Point(0.5465260545905707, 1-0.0007867820613690008), 
            Point (0.5248138957816377, 1-0.12667191188040913), 
            Point(0.5285359801488834, 1-0.1872541306058222), 
            Point(0.25806451612903225, 1-0.44531864673485444)]
)

SECONDARY_SECTOR.add(
    key='OSOM',
    value=[Point(0.0006203473945409429, 1-0.33988985051140835), 
            Point(0.25806451612903225, 1-0.44453186467348543), 
            Point(0.2704714640198511, 1-0.7261998426435877), 
            Point(0.25682382133995035, 1-0.999213217938631), 
            Point(0, 1-0.999213217938631)]
)

SECONDARY_SECTOR.add(
    key='S3S2',
    value=[Point(0.2704714640198511, 1-0.7254130605822188), 
            Point(0.5080645161290323, 1-0.7254130605822188), 
            Point(0.5409429280397022, 1-0.923682140047207), 
            Point(0.5887096774193549, 1-0.999213217938631), 
            Point(0.25744416873449133, 1-0.999213217938631)]
)

SECONDARY_SECTOR.add(
    key='I3I2',
    value=[Point(0.5893300248138957, 1-0.999213217938631), 
            Point(0.5409429280397022, 1-0.9221085759244689), 
            Point(0.5074441687344913, 1-0.7254130605822188), 
            Point(0.5893300248138957, 1-0.7765538945712038), 
            Point(0.6060794044665012, 1-0.7277734067663257), 
            Point(0.7400744416873449, 1-0.5247836349331235), 
            Point(0.7574441687344913, 1-0.5428796223446105), 
            Point(0.7946650124069479, 1-0.6939417781274587), 
            Point(0.8449131513647643, 1-0.6955153422501967), 
            Point(0.8504962779156328, 1-0.7317073170731707), 
            Point(0.9435483870967742, 1-0.8198269079464988), 
            Point(0.7872208436724566, 1-0.999213217938631)]
)

SECONDARY_SECTOR.add(
    key='APRES_I3I3_SE',
    value=[Point(0.7884615384615384, 1-0.998426435877262), 
            Point(0.9429280397022333, 1-0.8198269079464988), 
            Point(0.999379652605459, 1-0.8418568056648308), 
            Point(0.9987593052109182, 1-0.998426435877262)]
)

SECONDARY_SECTOR.add(
    key='M2',
    value=[Point(0.9981389578163772, 1-0.8402832415420929), 
            Point(0.9416873449131513, 1-0.8182533438237608), 
            Point(0.8492555831265509, 1-0.7309205350118018), 
            Point(0.8442928039702233, 1-0.6963021243115657), 
            Point(0.794044665012407, 1-0.6923682140047207), 
            Point(0.7568238213399504, 1-0.5428796223446105), 
            Point(0.739454094292804, 1-0.5239968528717546), 
            Point(0.6947890818858561, 1-0.45712037765538943), 
            Point(0.6854838709677419, 1-0.4358772619984264), 
            Point(0.9094292803970223, 1-0.17938630999213218), 
            Point(0.9987593052109182, 1-0.4107002360346184)]
)

SECONDARY_SECTOR.add(
    key='G2',
    value=[Point(0.9088089330024814, 1-0.17859952793076317), 
            Point(0.6854838709677419, 1-0.43430369787568845), 
            Point(0.6464019851116626, 1-0.3493312352478363), 
            Point(0.5831265508684863, 1-0.2549173878835563), 
            Point(0.542803970223325, 1-0.26671911880409127), 
            Point(0.5366004962779156, 1-0.25727773406766324), 
            Point(0.5310173697270472, 1-0.24783634933123525), 
            Point(0.5291563275434243, 1-0.23288749016522423), 
            Point(0.532258064516129, 1-0.22108575924468923), 
            Point(0.5366004962779156, 1-0.21243115656963021), 
            Point(0.5409429280397022, 1-0.2077104642014162), 
            Point(0.5272952853598015, 1-0.1872541306058222), 
            Point(0.5248138957816377, 1-0.12667191188040913), 
            Point(0.5459057071960298, 1-0), 
            Point(0.705955334987593, 1-0)]
)

#------------------------------------------------------------------------------
#--------- Definition  des balises  -------------------------------------------
#------------------------------------------------------------------------------
BALISES = DatabaseBalise([
    Balise(0.04714640198511166, 1-0.01730920535011802, name="DIRMO"),
    Balise(0.03287841191066997, 1-0.3060582218725413, name="GWENA"),
    Balise(0.01054590570719603, 1-0.8182533438237608, name="GAI"),
    Balise(0.07258064516129033, 1-0.07317073170731707, name="ETAMO"),
    Balise(0.09553349875930521, 1-0.7411487018095987, name="LOBOS"),
    Balise(0.10669975186104218, 1-0.7781274586939417, name="ONGHI"),
    Balise(0.18176178660049627, 1-0.23839496459480725, name="VULCA"),
    Balise(0.19540942928039703, 1-0.33831628638867034, name="CFA"),
    Balise(0.19975186104218362, 1-0.6451612903225806, name="MEN"),
    Balise(0.19540942928039703, 1-0.7435090479937058, name="ETORI"),
    Balise(0.2630272952853598, 1-0.5696302124311565, name="LANZA"),
    Balise(0.2698511166253102, 1-0.7112509834775768, name="SPIDY"),
    Balise(0.3238213399503722, 1-0.5011801730920535, name="MINDI"),
    Balise(0.34863523573200994, 1-0.07710464201416208, name="ATN"),
    Balise(0.3815136476426799, 1-0.14712824547600314, name="BURGO"),
    Balise(0.4230769230769231, 1-0.23918174665617625, name="BOJOL"),
    Balise(0.43548387096774194, 1-0.6451612903225806, name="MTL"),
    Balise(0.4441687344913151, 1-0.8269079464988198, name="MAJOR"),
    Balise(0.4646401985111663, 1-0.3304484657749803, name="LSE"),
    Balise(0.5167493796526055, 1-0.3981117230527144, name="LTP"),
    Balise(0.5347394540942928, 1-0.2549173878835563, name="LIMAN"),
    Balise(0.5831265508684863, 1-0.2069236821400472, name="PAS"),
    Balise(0.6271712158808933, 1-0.03147128245476003, name="VEYRI"),
    Balise(0.6116625310173698, 1-0.2966168371361133, name="MOZAO"),
    Balise(0.6004962779156328, 1-0.5712037765538945, name="GRENA"),
    Balise(0.6687344913151365, 1-0.11644374508261211, name="MELKA"),
    Balise(0.6662531017369727, 1-0.7065302911093627, name="SANTO"),
    Balise(0.7468982630272953, 1-0.03619197482297404, name="FRI"),
    Balise(0.7096774193548387, 1-0.1966955153422502, name="SEVET"),
    Balise(0.7363523573200993, 1-0.5177025963808025, name="BOSUA"),
    Balise(0.739454094292804, 1-0.8583792289535799, name="JAMBI"),
    Balise(0.8120347394540943, 1-0.09284028324154209, name="RAPID"),
    Balise(0.848014888337469, 1-0.4704956726986625, name="JUVEN"),
    Balise(0.8815136476426799, 1-0.8174665617623919, name="SAMOS"),
    Balise(0.9032258064516129, 1-0.975609756097561, name="SICIL"),
    Balise(0.966501240694789, 1-0.42014162077104644, name="BIELA"),
    Balise(0.9844913151364765, 1-0.982690794649882, name="SODRI")]
)



#------------------------------------------------------------------------------
#--------- Definition  des routes aeriennes:  ---------------------------------
#------------------------------------------------------------------------------
ROUTES = Airway()

#----------------nord sud ---------------------
#DIRMO

ROUTES.add(
    key="NORTHSOUTH1",
    value=["DIRMO", "ETAMO", "CFA", "MEN", "LOBOS", "GAI"]
)

ROUTES.add(
    key="NORTHSOUTH2",
    value=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI"]
)

"""ROUTES.add(
    key="NORTHSOUTH3",
    value=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI", "SPIDY", "MTL", "GRENA", "SANTO", "JAMBI"]
)"""

"""ROUTES.add(
    key="NORTHSOUTH4",
    value=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI", "SPIDY", "MTL", "GRENA", "SANTO", "SAMOS"]
)"""

"""ROUTES.add(
    key="NORTHSOUTH5",
    value=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI", "SPIDY", "MTL", "GRENA", "BOSUA", "JUVEN"]
)"""

"""ROUTES.add(
    key="NORTHSOUTH6",
    value=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI", "SPIDY", "MTL", "GRENA", "BOSUA", "JUVEN", "BIELA"]
)"""

#ATN

ROUTES.add(
    key="NORTHSOUTH7",
    value=["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "LOBOS", "GAI"]
)

ROUTES.add(
    key="NORTHSOUTH8",
    value=["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "ETORI"]
)

"""ROUTES.add(
    key="NORTHSOUTH11",
    value=["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "ETORI", "ONGHI", "GAI"]
)"""

ROUTES.add(
    key="NORTHSOUTH9",
    value=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "JAMBI"]
)

ROUTES.add(
    key="NORTHSOUTH10",
    value=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "SAMOS"]
)

"""ROUTES.add(
    key="NORTHSOUTH11",
    value=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "BOSUA", "JUVEN"]
)"""

"""ROUTES.add(
    key="NORTHSOUTH12",
    value=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "BOSUA", "JUVEN", "BIELA"]
)"""

ROUTES.add(
    key="NORTHSOUTH13",
    value=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI"]
)

#VEYRI
ROUTES.add(
    key="NORTHSOUTH14",
    value=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "LOBOS", "GAI"]
)

ROUTES.add(
    key="NORTHSOUTH15",
    value=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "ETORI"]
)

"""ROUTES.add(
    key="NORTHSOUTH15bis",
    value=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "ETORI", "ONGHI", "GAI"]
)"""

ROUTES.add(
    key="NORTHSOUTH16",
    value=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "SANTO", "JAMBI"]
)

ROUTES.add(
    key="NORTHSOUTH17",
    value=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "SANTO", "SAMOS"]
)

ROUTES.add(
    key="NORTHSOUTH18",
    value=["VEYRI", "MELKA", "SEVET", "JUVEN"]
)

"""ROUTES.add(
    key="NORTHSOUTH19",
    value=["VEYRI", "MELKA", "SEVET", "JUVEN", "BIELA"]
)"""

ROUTES.add(
    key="NORTHSOUTH20",
    value=["VEYRI", "MELKA", "SEVET", "JUVEN", "BOSUA", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI" ] 
)

"""ROUTES.add(
    key="NORTHSOUTH20bis",
    value=["VEYRI", "MELKA", "SEVET", "JUVEN", "BOSUA", "GRENA", "SANTO", "JAMBI" ] 
)"""

"""ROUTES.add(
    key="NORTHSOUTH20tri",
    value=["VEYRI", "MELKA", "SEVET", "JUVEN", "BOSUA", "GRENA", "SANTO", "SAMOS" ] 
)"""

#FRI

ROUTES.add(
    key="NORTHSOUTH21",
    value=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "LOBOS", "GAI"]
)

ROUTES.add(
    key="NORTHSOUTH22",
    value=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "ETORI"]
)

ROUTES.add(
    key="NORTHSOUTH23",
    value=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "SANTO", "JAMBI"]
)

ROUTES.add(
    key="NORTHSOUTH24",
    value=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "SANTO", "SAMOS"]
)

ROUTES.add(
    key="NORTHSOUTH25",
    value=["FRI", "MELKA", "SEVET", "JUVEN"]
)

"""ROUTES.add(
    key="NORTHSOUTH26",
    value=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI"]
)"""

ROUTES.add(
    key="NORTHSOUTH26",
    value=["FRI", "MELKA", "SEVET", "JUVEN", "BOSUA", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI"]
)

#BIELA

ROUTES.add(
    key="NORTHSOUTH34",
    value=["BIELA", "JUVEN", "BOSUA", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI"]
)


"""ROUTES.add(
    key="NORTHSOUTH36",
    value=["BIELA", "JUVEN", "BOSUA", "GRENA", "SANTO", "JAMBI"]
)"""

"""ROUTES.add(
    key="NORTHSOUTH37",
    value=["BIELA", "JUVEN", "BOSUA", "GRENA", "SANTO", "SAMOS"]
)"""


#--------------------sud nord ------------------------------
#MAJOR

ROUTES.add(
    key="SOUTHNORTH41",
    value=["MAJOR", "MTL", "MINDI", "CFA", "VULCA"]
)

ROUTES.add(
    key="SOUTHNORTH42",
    value=["MAJOR", "MTL", "MINDI", "CFA", "VULCA", "BURGO", "VEYRI"]
)

ROUTES.add(
    key="SOUTHNORTH43",
    value=["MAJOR", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"]
)

ROUTES.add(
    key="SOUTHNORTH44",
    value=["MAJOR", "MTL", "GRENA", "BOSUA", "JUVEN", "BIELA"]
)

#SODRI

ROUTES.add(
    key="SOUTHNORTH46",
    value=["SODRI", "SICIL", "JAMBI", "MTL", "MINDI", "CFA", "VULCA"]
)

ROUTES.add(
    key="SOUTHNORTH47",
    value=["SODRI", "SICIL", "JAMBI", "MTL", "MINDI", "CFA", "VULCA", "BURGO", "VEYRI"]
)

ROUTES.add(
    key="SOUTHNORTH48",
    value=["SODRI", "SICIL", "JAMBI", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"]
)

#GAI

ROUTES.add(
    key="SOUTHNORTH50",
    value=["GAI", "GWENA", "DIRMO"]
)

ROUTES.add(
    key="SOUTHNORTH51",
    value=["GAI", "GWENA", "VULCA"]
)

ROUTES.add(
    key="SOUTHNORTH52",
    value=["GAI", "GWENA", "VULCA", "BURGO", "VEYRI"]
)

ROUTES.add(
    key="SOUTHNORTH53",
    value=["GAI", "ONGHI", "ETORI", "SPIDY", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"]
)

ROUTES.add(
    key="SOUTHNORTH54",
    value=["GAI", "ONGHI", "ETORI", "SPIDY", "MTL", "GRENA", "BOSUA", "JUVEN", "BIELA"]
)


#------------------------------------------------------------------------------
#--------- Definition  des balise de departs et d'arrivées: -------------------
#------------------------------------------------------------------------------


START_BALISE = {
    "NORTH-SOUTH": ["DIRMO", "ATN", "VEYRI", "FRI", "BIELA"],
    "SOUTH-NORTH": ["MAJOR", "SODRI", "GAI"]
}

END_BALISE = {
    "NORTH-SOUTH": ["GAI", "ETORI", "JAMBI", "SAMOS", "JUVEN", "BIELA"],
    "SOUTH-NORTH": ["DIRMO", "VULCA", "VEYRI", "RAPID", "BIELA"]
}


#------------------------------------------------------------------------------
#--------- Definition  des segment: -------------------------------------------
#------------------------------------------------------------------------------

DIRECTED_SEGMENT = {
    "NORTH-SOUTH": [
        ["DIRMO", "ETAMO"], ["ETAMO", "CFA"], ["CFA", "MEN"], ["MEN", "ETORI"],
        ["LANZA", "MEN"], ["LANZA", "MINDI"], ["LSE", "MINDI"], ["LSE", "LTP"],
        ["LSE", "BOJOL"], ["BOJOL", "BURGO"], ["BURGO", "ATN"], ["LSE", "LIMAN"],
        ["LIMAN", "PAS"], ["PAS", "MELKA"], ["MELKA", "VEYRI"], ["MELKA", "FRI"],
        ["MELKA", "SEVET"], ["SEVET", "JUVEN"], ["LTP", "GRENA"], ["GRENA", "SANTO"],
        ["SANTO", "JAMBI"], ["SANTO", "SAMOS"]
    ],
    "SOUTH-NORTH": [
        ["GAI", "GWENA"], ["GWENA", "DIRMO"], ["GWENA", "VULCA"], ["VULCA", "BURGO"],
        ["BURGO", "VEYRI"], ["CFA", "VULCA"], ["CFA", "MINDI"], ["MINDI", "MTL"],
        ["MTL", "LTP"], ["MTL", "JAMBI"], ["JAMBI", "SICIL"], ["SICIL", "SODRI"],
        ["LTP", "MOZAO"], ["MOZAO", "SEVET"], ["SEVET", "RAPID"]
    ],
    "BOTH": [
        ["GAI", "LOBOS"], ["LOBOS", "MEN"], ["GAI", "ONGHI"], ["ONGHI", "ETORI"],
        ["ETORI", "SPIDY"], ["SPIDY", "MTL"], ["MTL", "MAJOR"], ["MTL", "GRENA"],
        ["GRENA", "BOSUA"], ["BOSUA", "JUVEN"], ["JUVEN", "BIELA"]
    ]
}






#------------------------------------------------------------------------------
#--------- Definition  des avions:  -------------------------------------------
#------------------------------------------------------------------------------
"""AIRCRAFTS = AircraftCollector() # Gestion d'un dictionnaire car recherche en O(1)
AIRCRAFTS.add_aircraft(Aircraft(speed=0.003, # Conflit 5:48 #0.003
                                flight_plan=Airway.transform(ROUTES.get_from_key("NO-SE1"), BALISES))
                    )
AIRCRAFTS.add_aircraft(Aircraft(speed=0.002, 
                                flight_plan=Airway.transform(ROUTES.get_from_key("NO-SO1"), BALISES, reverse=True),
                                take_off_time=20)
)
AIRCRAFTS.add_aircraft(Aircraft(speed=0.001, 
                                flight_plan=Airway.transform(ROUTES.get_from_key("SE-NE1"), BALISES))
)
AIRCRAFTS.add_aircraft(Aircraft(speed=0.0012, 
                                flight_plan=Airway.transform(["MAJOR", "MTL", "MINDI", "CFA", "ETAMO"], BALISES))
)"""
#0.001, 0.002, 0.002, 0.001 conflit LSE (1-2) + MTL (3-4)
#0.003, 0.002 0.001, 0.0012 pas de conflit
#Solution propose par recuit:
#[DataStorage(speed=0.002, id=1), DataStorage(speed=0.003, id=2), DataStorage(speed=0.003, id=3), DataStorage(speed=0.003, id=4)]


