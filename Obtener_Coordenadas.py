#!/usr/bin/env python
""" Parse the addresses to obtain the coordinates and display the results on a map """
from googlemaps import Client
import os
import pickle
import gmplot
import json
from sys import stdout
__author__ = "Augusto Meza"
# Updates by Ricardo JC

gmaps = Client(key='AIzaSyAycEuXVjtrwQc1B53iKUGpH-tLl_zB-Ys')
gmap = gmplot.GoogleMapPlotter(19.379162, -99.137760, 12)
data_root = ''
mexicocity_bounds = {
        "northeast": {
            "lat": 19.545890,
            "lng": -99.014140
        },
        "southwest": {
            "lat": 19.207550,
            "lng": -99.275016
        }
    }


def geocode_google(query, progress=0.0):
    """
    From the phrase look up the address and default the untraceable
    :param query: Phrase to look for
    :param progress: current address being queried
    :return: dictionary containing lat and lng
    """

    stdout.write('\rPercentage Completed {:2.2f}%'.format(progress * 100))
    full_address = gmaps.geocode(query, region="mx", bounds=mexicocity_bounds)
    if len(full_address) != 1:
        print(query)
        return {'lat': 0, 'lng': 0}
    elif len(full_address) > 1:
        print(full_address)
    location = full_address[0]['geometry']['location']
    return location


def parse_ne(filename):
    """
    From the output file obtain the address
    :param filename: file containing clustering output
    :return: list of addresses
    """
    with open(filename, 'r') as f:
        street_i = -1
        colonia_i = -1
        addresses = []
        for i, line in enumerate(f.readlines()):
            if line == 'Calle: \n':
                street_i = i + 1
            if line == 'Complemento: \n':
                colonia_i = i + 1
            if i == street_i:
                addresses.append(line.replace('\n', '').replace('https', '').replace('#', '').replace('esquina', ''))
            if i == colonia_i:
                addresses[-1] = addresses[-1] + ' , ' + line.replace('\n', '').split('#')[0]
    return addresses


def parse_json(filename):
    '''
    From JSON file obtain address
    :param filename: file containing clustering output
    :return: list of addresses
    '''
    j_file = json.load(open(filename))
    addresses = []
    for tweet in j_file:
        addresses.append(j_file.get(tweet).get('Calle'))
    return addresses




def retrieve_addrs(filename, force=False):
    """
    From the given filename obtain the addresses and pickled them, if pickle with addresses exists load it
    :param filename: filename that contains the addresses
    :param force: force parsing the file even if it has already been procesed
    :return: the addresses either parsed or from pickle file
    """
    dest_filename = os.path.join(data_root, 'addresses.pickle')
    if force or not os.path.exists(dest_filename):
        print('Parsing named entities...')
        #data = parse_ne(filename)
        data = parse_json(filename)
        with open(dest_filename, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    else:
        with open(dest_filename,'rb') as f:
            data = pickle.load(f)
    print(len(data), 'addresses total, limit is 2500 per day')
    return data

def retrieve_locs(filename, force=False):
    """
    From the given filename check wheater locations have been obtained and retrieve them, otherwise parse the file
    :param filename: filename that contains the addresses
    :param force: force parsing the file even if it has already been procesed
    :return: the coordinates as a list of dictionaries with entries lng and lat
    """
    dest_filename = os.path.join(data_root, 'locations.pickle')
    if force or not os.path.exists(dest_filename):
        print('Geocoding addresses')
        addrs = retrieve_addrs(filename, force=force)
        locations = {}
        for i, query in enumerate(addrs):
            locations[addrs[i]]=[geocode_google(query, i/len(addrs))]
        #locations = [geocode_google(query, i/len(addrs)) for i, query in enumerate(addrs)]
        with open(dest_filename, 'wb') as f:
            pickle.dump(locations, f, pickle.HIGHEST_PROTOCOL)
        print('Completed and pickled')
    else:
        with open(dest_filename, 'rb') as f:
            locations = pickle.load(f)
    return locations



def plot_loc(locations):
    """
    TESTING, plot the coordinates given MEXICO CITY center
    :param locations: list of coordinates
    :return: The compiled map
    """
    latitudes = []
    longitudes = []
    for location in locations:
        if not location['lat'] == 0:
            latitudes.append(location['lat'])
            longitudes.append(location['lng'])
    #gmap.scatter(latitudes, longitudes, '#3B0B39', size=250, marker=False)
    #gmap.draw("mymap.html")

retrieve_locs('ner.json')
#plot_loc(retrieve_locs('ner.json'))
#parse_json('ner.json')
