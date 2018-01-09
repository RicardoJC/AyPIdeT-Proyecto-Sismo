import pickle
from itertools import combinations
from math import radians, cos, sin, asin, sqrt
import gmplot
import geohash2
import json

gmap = gmplot.GoogleMapPlotter(19.379162, -99.137760, 12)

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371* c
    return km

def group(locations, threshold = 2,precision=8):
    hashes = []
    for location in locations:
        hashes.append(geohash2.encode(location['lat'],location['lng'],precision=precision))
    already = {}
    for hash in hashes:
        prefix = hash[:-threshold:]
        if prefix not in already:
            already.update({prefix:hash})
    new_locations = []
    for hash in already.values():
        coord = geohash2.decode(hash)
        new_locations.append({'lat':float(coord[0]),'lng':float(coord[1])})
    return new_locations

def plot_loc(locations,name):
    latitudes = []
    longitudes = []
    for location in locations:
        if not location['lat'] == 0:
            latitudes.append(location['lat'])
            longitudes.append(location['lng'])
    gmap.scatter(latitudes, longitudes, '#3B0B39', size=250, marker=False)
    gmap.draw(name)

def remove_zeros(locations):
    clean_locations = []
    for coord in locations:
        if coord["lng"] != 0:
            clean_locations.append(coord)
    return clean_locations

def generate_json(locations):
    #coor =  json.dumps(locations)
    for loc in locations:
        loc['title']='Ayuda terremoto'
        loc['description'] = 'Help!'
    with open('locations.json','w+') as f:
        f.write(json.dumps(locations))






old_locations = pickle.load( open( "locations.pickle", "rb" ) )
addresses = pickle.load(open('addresses.pickle','rb'))
print(len(old_locations))
clean_locations = remove_zeros(old_locations)
print(len(clean_locations))
new_locations = group(clean_locations)
print(len(new_locations))
plot_loc(new_locations,'nuevas.html')
plot_loc(old_locations,'viejas.html')
generate_json(new_locations)
