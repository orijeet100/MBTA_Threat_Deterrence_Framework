import pygal

# Create a Supranational World Map
worldmap = pygal.maps.world.SupranationalWorld()

# Set the title of the map
worldmap.title = 'Network Locations by Continent'

# Adding the continents
worldmap.add('Africa', [('africa')])
worldmap.add('North America', [('north_america')])
worldmap.add('Oceania', [('oceania')])
worldmap.add('South America', [('south_america')])
worldmap.add('Asia', [('asia')])
worldmap.add('Europe', [('europe')])
worldmap.add('Antarctica', [('antartica')])

# Network Locations
network_locations = {
    "Athens": (37.9838, 23.7275),
    "Budapest": (47.4979, 19.0402),
    "Cairo": (30.0444, 31.2357),
    "Montreal": (45.5017, -73.5673),
    "New York": (40.7128, -74.0060),
    "Boston": (42.3601, -71.0589),
    "Delhi": (28.6139, 77.2090),
    "Tokyo": (35.6895, 139.6917),
    "Paris": (48.8566, 2.3522),
    "Shanghai": (31.2304, 121.4737),
    "London": (51.5074, -0.1278),
    "Toronto": (43.651070, -79.347015),
    "Rome": (41.9028, 12.4964),
    "Lisbon": (38.7223, -9.1393),
    "Amsterdam": (52.3676, 4.9041),
    "BuenosAires": (-34.6037, -58.3816),
    "Naples": (40.8518, 14.2681),
    "Dubai": (25.276987, 55.296249),
    "Vienna": (48.2082, 16.3738),
    "SanFrancisco": (37.7749, -122.4194),
    "Stockholm": (59.3293, 18.0686),
    "Vancouver": (49.2827, -123.1207),
    "Rotterdam": (51.9225, 4.4792),
    "Marseille": (43.2965, 5.3698),
    "Toulouse": (43.6047, 1.4442),
    "Oslo": (59.9139, 10.7522),
    "Warsaw": (52.2297, 21.0122),
    "Kobe": (34.6901, 135.1955),
    "Philadelphia": (39.9526, -75.1652),
    "Bilbao": (43.2630, -2.9350),
    "Lyon": (45.7640, 4.8357),
    "Valencia": (39.4699, -0.3763),
    "Washington DC": (38.9072, -77.0369),
    "Chicago": (41.8781, -87.6298),
}

# Plot network locations as points
for city, coords in network_locations.items():
    worldmap.add(city, {city.lower().replace(" ", "_"): 1})

# Save into a high-quality PNG file
worldmap.render_to_png('network_locations_pygal.png')

print("Success! Map with points saved to 'visuals_for_paper/network_locations_pygal.png'")
