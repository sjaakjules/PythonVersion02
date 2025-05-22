"""
Purpose: Interface with the Curiosa API for online deck retrieval.
Responsibilities:
	•	Downloads user-supplied deck by ID.
	•	Parses it into Atlas and Spellbook format.
	•	Handles conversion into the internal Deck structure.
"""

# Preconstructed Decks
PRECON_ALPHA = {
    'avatar_air': "https://curiosa.io/precons/clso3l1mg001q2w08qv1nexky",
    'avatar_water': "https://curiosa.io/precons/clso3lffd006jhb60hiwpltyc",
    'avatar_fire': "https://curiosa.io/precons/clso3l8ph005ihb60cxkus6mh",
    'avatar_earth': "https://curiosa.io/precons/clso3lngx007lhb600v843gd7"
}

PRECON_BETA = {
    'sparkmage': "https://curiosa.io/precons/clczbmbxb008av5ugml35rdwt",
    'waveshaper': "https://curiosa.io/precons/clczbmbxb008ev5ugiovmxcw1",
    'flamecaller': "https://curiosa.io/precons/clczbmbxb0085v5ug7eyxn2dk",
    'geomancer': "https://curiosa.io/precons/clczbmbxb008hv5uggpws66fe"
}

# Single Element Decks
SINGLE_ELEMENT = {
    'avatar_air': {"https://curiosa.io/decks/clur4vvfi007393mb1jeks49q",
                   "https://curiosa.io/decks/cm7h1bo280003jy03d6h9vjdk"},
    'avatar_earth': "https://curiosa.io/decks/clf3gywls001xjs0fq0oymxrw",
    'avatar_fire': "https://curiosa.io/decks/clllgewcb000al70f1trl23nj",
    'avatar_water': "https://curiosa.io/decks/clkta1lm80016ml0fx7j5g85z",
    'flamecaller': "https://curiosa.io/decks/clp4lhy3k000ml40f7tz4kzt9",
    'geomancer': "https://curiosa.io/decks/clq0g9545005v18uw6wys5j7s",
    'sparkmage': "https://curiosa.io/decks/cloneejb7003al80fj99t5zse",
    'spellslinger': "https://curiosa.io/decks/clzyaqvk200f69z9318843mvj",
    'waveshaper': "https://curiosa.io/decks/cm778jggb0004la031y4lihll"
}

# Double Element Decks
DOUBLE_ELEMENT = {
    'archimago': "https://curiosa.io/decks/cm5gwcht600cajv03o66g813t",
    'battlemage': {"https://curiosa.io/decks/clczbmbxk00l5v5ug8fszmefg",
                   "https://curiosa.io/decks/clvotbl1x000hdr85httnltx9"},
    'deathspeaker': "https://curiosa.io/decks/clczbmbxm00osv5ug2r4pyidz",
    'druid': "https://curiosa.io/decks/cm6idlshk003jl803y6gvrshg",
    'enchantress': "https://curiosa.io/decks/clsmmlhou001z11pizfcx1ika",
    'pathfinder': "https://curiosa.io/decks/clfu91ick0000mo0f2o0ydeo2",
    'seer': "https://curiosa.io/decks/cltwmj6vp0040ydfaz3qodjgd",
    'sorcerer': "https://curiosa.io/decks/clrno48s50029nptuqqoxyioa",
    'spellslinger': "https://curiosa.io/decks/cm1zd8c0h006ezuaazqvybyiu",
    'witch': "https://curiosa.io/decks/cm2biop6z00006htx57qzp8fm"
}

# Triple Element Decks
TRIPLE_ELEMENT = {
    'archimago': "https://curiosa.io/decks/cm36h7lls005ltupl99xqsoj0",
    'deathspeaker': "https://curiosa.io/decks/cm6ksu9us00m0lb03jr9ft22q",
    'enchantress': {"https://curiosa.io/decks/clf7hjfxc002lmk0gy6nyzgl9",
                    "https://curiosa.io/decks/cm7e9p2x80002jr03v9v2d7pg"},
    'seer': "https://curiosa.io/decks/cm8m6vbdu002tie03di2cqd8g"
}

# Quadruple Element Decks
QUADRUPLE_ELEMENT = {
    'elementalist': {"https://curiosa.io/decks/clp2hendb007ol70ffaln2e5x",
                     "https://curiosa.io/decks/cmamc8l5r008jih047su6gbtf"},
    'templar': "https://curiosa.io/decks/cm29j1szy0030j0oagg8ujs0t"
}


def get_all_precon_alpha():
    return list(PRECON_ALPHA.values())


def get_all_precon_beta():
    return list(PRECON_BETA.values())


def get_all_single_element():
    urls = []
    for value in SINGLE_ELEMENT.values():
        if isinstance(value, dict):
            urls.extend(value)
        else:
            urls.append(value)
    return urls


def get_all_double_element():
    urls = []
    for value in DOUBLE_ELEMENT.values():
        if isinstance(value, dict):
            urls.extend(value)
        else:
            urls.append(value)
    return urls


def get_all_triple_element():
    urls = []
    for value in TRIPLE_ELEMENT.values():
        if isinstance(value, dict):
            urls.extend(value)
        else:
            urls.append(value)
    return urls


def get_all_quadruple_element():
    urls = []
    for value in QUADRUPLE_ELEMENT.values():
        if isinstance(value, dict):
            urls.extend(value)
        else:
            urls.append(value)
    return urls


def get_all_decks():
    """Returns a list of all deck URLs."""
    return (
        get_all_precon_alpha() +
        get_all_precon_beta() +
        get_all_single_element() +
        get_all_double_element() +
        get_all_triple_element() +
        get_all_quadruple_element()
    )


def get_avatar_decks(avatar_name):
    """
    Returns all decks for a specific avatar/archetype.
    
    Args:
        avatar_name (str): The name of the avatar/archetype (e.g., 'avatar', 'archimago', 'enchantress')
        
    Returns:
        list: A list of deck URLs for the specified avatar/archetype
        
    Example:
        >>> get_avatar_decks('avatar')
        ['https://curiosa.io/decks/clur4vvfi007393mb1jeks49q', ...]
    """
    decks = []
    
    # Check in single element decks
    if avatar_name in SINGLE_ELEMENT:
        value = SINGLE_ELEMENT[avatar_name]
        if isinstance(value, dict):
            decks.extend(value)
        else:
            decks.append(value)
    
    # Check in double element decks
    if avatar_name in DOUBLE_ELEMENT:
        value = DOUBLE_ELEMENT[avatar_name]
        if isinstance(value, dict):
            decks.extend(value)
        else:
            decks.append(value)
    
    # Check in triple element decks
    if avatar_name in TRIPLE_ELEMENT:
        value = TRIPLE_ELEMENT[avatar_name]
        if isinstance(value, dict):
            decks.extend(value)
        else:
            decks.append(value)
    
    # Check in quadruple element decks
    if avatar_name in QUADRUPLE_ELEMENT:
        value = QUADRUPLE_ELEMENT[avatar_name]
        if isinstance(value, dict):
            decks.extend(value)
        else:
            decks.append(value)
    
    return decks


def get_available_avatars():
    """
    Returns a list of all available avatar/archetype names.
    
    Returns:
        list: A list of all avatar/archetype names that have decks
        
    Example:
        >>> get_available_avatars()
        ['avatar', 'archimago', 'enchantress', ...]
    """
    avatars = set()
    avatars.update(SINGLE_ELEMENT.keys())
    avatars.update(DOUBLE_ELEMENT.keys())
    avatars.update(TRIPLE_ELEMENT.keys())
    avatars.update(QUADRUPLE_ELEMENT.keys())
    return sorted(list(avatars))
