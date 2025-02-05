from model.sector import Sector
from model.point import Point
from model.balise import Balise
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
BALISES = [
    Balise(0.04714640198511166, 1-0.01730920535011802, name="DIRMO", is_external=True),
    Balise(0.03287841191066997, 1-0.3060582218725413, name="GWENA"),
    Balise(0.01054590570719603, 1-0.8182533438237608, name="GAI", is_external=True),
    Balise(0.07258064516129033, 1-0.07317073170731707, name="ETAMO", is_external=True),
    Balise(0.09553349875930521, 1-0.7411487018095987, name="LOBOS", is_external=True),
    Balise(0.10669975186104218, 1-0.7781274586939417, name="ONGHI", is_external=True),
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
    Balise(0.4441687344913151, 1-0.8269079464988198, name="MAJOR", is_external=True),
    Balise(0.4646401985111663, 1-0.3304484657749803, name="LSE"),
    Balise(0.5167493796526055, 1-0.3981117230527144, name="LTP"),
    Balise(0.5347394540942928, 1-0.2549173878835563, name="LIMAN"),
    Balise(0.5831265508684863, 1-0.2069236821400472, name="PAS"),
    Balise(0.6271712158808933, 1-0.03147128245476003, name="VEYRI", is_external=True),
    Balise(0.6116625310173698, 1-0.2966168371361133, name="MOZAO"),
    Balise(0.6004962779156328, 1-0.5712037765538945, name="GRENA"),
    Balise(0.6687344913151365, 1-0.11644374508261211, name="MELKA"),
    Balise(0.6662531017369727, 1-0.7065302911093627, name="SANTO"),
    Balise(0.7468982630272953, 1-0.03619197482297404, name="FRI", is_external=True),
    Balise(0.7096774193548387, 1-0.1966955153422502, name="SEVET"),
    Balise(0.7363523573200993, 1-0.5177025963808025, name="BOSUA"),
    Balise(0.739454094292804, 1-0.8583792289535799, name="JAMBI"),
    Balise(0.8120347394540943, 1-0.09284028324154209, name="RAPID", is_external=True),
    Balise(0.848014888337469, 1-0.4704956726986625, name="JUVEN"),
    Balise(0.8815136476426799, 1-0.8174665617623919, name="SAMOS", is_external=True),
    Balise(0.9032258064516129, 1-0.975609756097561, name="SICIL", is_external=True),
    Balise(0.966501240694789, 1-0.42014162077104644, name="BIELA", is_external=True),
    Balise(0.9844913151364765, 1-0.982690794649882, name="SODRI", is_external=True)
]



#------------------------------------------------------------------------------
#--------- Definition  des routes aeriennes:  ---------------------------------
#------------------------------------------------------------------------------

#--------------------Nord --> Sud  ------------------------------

ROUTES_NORTH_SOUTH = [
    # DIRMO

Airway(name='NORTHSOUTH1', points=["DIRMO", "ETAMO", "CFA", "MEN", "LOBOS", "GAI"]),
Airway(name='NORTHSOUTH2', points=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI"]),
#Airway(name='NORTHSOUTH3', points=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI", "SPIDY", "MTL", "GRENA", "SANTO", "JAMBI"]),
#Airway(name="NORTHSOUTH4", points=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI", "SPIDY", "MTL", "GRENA", "SANTO", "SAMOS"]),
#Airway(name="NORTHSOUTH5", points=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI", "SPIDY", "MTL", "GRENA", "BOSUA", "JUVEN"]),
#Airway(name="NORTHSOUTH6", points=["DIRMO", "ETAMO", "CFA", "MEN", "ETORI", "SPIDY", "MTL", "GRENA", "BOSUA", "JUVEN", "BIELA"]),


    # ATN

Airway(name="NORTHSOUTH7", points=["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "LOBOS", "GAI"]),
Airway(name="NORTHSOUTH8", points=["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "ETORI"]),
#Airway(name="NORTHSOUTH11", points=["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "ETORI", "ONGHI", "GAI"]),
Airway(name="NORTHSOUTH9", points=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "JAMBI"]),
Airway(name="NORTHSOUTH10", points=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "SAMOS"]),
#Airway(name="NORTHSOUTH11", points=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "BOSUA", "JUVEN"]),
#Airway(name="NORTHSOUTH12", points=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "BOSUA", "JUVEN", "BIELA"]),
Airway(name="NORTHSOUTH13", points=["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI"]),

    # VEYRI
Airway(name="NORTHSOUTH14", points=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "LOBOS", "GAI"]),
Airway(name="NORTHSOUTH15", points=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "ETORI"]),
#Airway(name="NORTHSOUTH15bis", points=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "ETORI", "ONGHI", "GAI"]),
Airway(name="NORTHSOUTH16", points=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "SANTO", "JAMBI"]),
Airway(name="NORTHSOUTH17", points=["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "SANTO", "SAMOS"]),
Airway(name="NORTHSOUTH18", points=["VEYRI", "MELKA", "SEVET", "JUVEN"]),
#Airway(name="NORTHSOUTH19", points=["VEYRI", "MELKA", "SEVET", "JUVEN", "BIELA"]),
Airway(name="NORTHSOUTH20", points=["VEYRI", "MELKA", "SEVET", "JUVEN", "BOSUA", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI" ]),
#Airway(name="NORTHSOUTH20bis", points=["VEYRI", "MELKA", "SEVET", "JUVEN", "BOSUA", "GRENA", "SANTO", "JAMBI" ]),
#Airway(name="NORTHSOUTH20tri", points=["VEYRI", "MELKA", "SEVET", "JUVEN", "BOSUA", "GRENA", "SANTO", "SAMOS" ]),


    # FRI

Airway(name="NORTHSOUTH21",points=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "LOBOS", "GAI"]),
Airway(name="NORTHSOUTH22", points=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "ETORI"]),
Airway(name="NORTHSOUTH23", points=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "SANTO", "JAMBI"]),
Airway(name="NORTHSOUTH24", points=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "SANTO", "SAMOS"]),
Airway(name="NORTHSOUTH25", points=["FRI", "MELKA", "SEVET", "JUVEN"]),
#Airway(name="NORTHSOUTH26", points=["FRI", "MELKA", "PAS", "LIMAN", "LSE", "LTP", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI"]),
Airway(name="NORTHSOUTH26", points=["FRI", "MELKA", "SEVET", "JUVEN", "BOSUA", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI"]),

    # BIELA

Airway(name="NORTHSOUTH34", points=["BIELA", "JUVEN", "BOSUA", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI"]),
#Airway(name="NORTHSOUTH36", points=["BIELA", "JUVEN", "BOSUA", "GRENA", "SANTO", "JAMBI"]),
#Airway(name="NORTHSOUTH37", points=["BIELA", "JUVEN", "BOSUA", "GRENA", "SANTO", "SAMOS"]),
]

#-------------------- South --> North  ------------------------------
ROUTES_SOUTH_NORTH = [
    # MAJOR

Airway(name="SOUTHNORTH41", points=["MAJOR", "MTL", "MINDI", "CFA", "VULCA"]),
Airway(name="SOUTHNORTH42", points=["MAJOR", "MTL", "MINDI", "CFA", "VULCA", "BURGO", "VEYRI"]),
Airway(name="SOUTHNORTH43", points=["MAJOR", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"]),
Airway(name="SOUTHNORTH44", points=["MAJOR", "MTL", "GRENA", "BOSUA", "JUVEN", "BIELA"]),

    # SODRI

Airway(name="SOUTHNORTH46", points=["SODRI", "SICIL", "JAMBI", "MTL", "MINDI", "CFA", "VULCA"]),
Airway(name="SOUTHNORTH47", points=["SODRI", "SICIL", "JAMBI", "MTL", "MINDI", "CFA", "VULCA", "BURGO", "VEYRI"]),
Airway(name="SOUTHNORTH48", points=["SODRI", "SICIL", "JAMBI", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"]),
    
    # GAI

Airway(name="SOUTHNORTH50", points=["GAI", "GWENA", "DIRMO"]),
Airway(name="SOUTHNORTH51", points=["GAI", "GWENA", "VULCA"]),
Airway(name="SOUTHNORTH52", points=["GAI", "GWENA", "VULCA", "BURGO", "VEYRI"]),
Airway(name="SOUTHNORTH53", points=["GAI", "ONGHI", "ETORI", "SPIDY", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"]),
Airway(name="SOUTHNORTH54", points=["GAI", "ONGHI", "ETORI", "SPIDY", "MTL", "GRENA", "BOSUA", "JUVEN", "BIELA"])
]


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


