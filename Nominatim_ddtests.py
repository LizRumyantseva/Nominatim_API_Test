import requests
import pytest
import xlrd

url_forward_search = "https://nominatim.openstreetmap.org/search"
url_reverse_search = "https://nominatim.openstreetmap.org/reverse"


def read_file(name):
    filename = name
    xls = xlrd.open_workbook(filename)
    sheet = xls.sheet_by_index(0)
    vals = [tuple(sheet.row_values(rownum)) for rownum in range(sheet.nrows)]
    vals.pop(0)
    return vals


# for free-form search
@pytest.mark.parametrize('request_text, lat, lon', read_file('test_data_forward_f2.xlsx'))
def test_forward_search_format2(request_text, lat, lon):
    response = requests.get(url_forward_search, {'q': request_text, 'format': 'json'}).json()
    response_lat = float(response[0]['lat'])
    response_lon = float(response[0]['lon'])
    assert (float(lat) == response_lat) & (float(lon) == response_lon)


# for structured search
@pytest.mark.parametrize('street, city, county, state, country, postalcode, lat, lon',
                         read_file('test_data_forward_f1.xlsx'))
def test_forward_search_format1(street, city, county, state, country, postalcode, lat, lon):
    if postalcode != '':
        postalcode = str(int(postalcode))
    response = requests.get(url_forward_search,
                            {'street': street, 'city': city, 'county': county, 'state': state, 'country': country,
                             'postalcode': postalcode, 'format': 'json'})
    response = response.json()
    if response != []:
        response_lat = float(response[0]['lat'])
        response_lon = float(response[0]['lon'])
    else:
        response_lat = 0
        response_lon = 0
    assert (float(lat) == response_lat) & (float(lon) == response_lon)


# reverse with lat & lon
@pytest.mark.parametrize('lat, lon, expected_name', read_file('test_data_reverse_lat_lon.xlsx'))
def test_reverse_search_lat_lon(lat, lon, expected_name):
    response = requests.get(url_reverse_search,
                            {'lat': lat, 'lon': lon, 'format': 'json', 'accept-language': 'en'}).json()
    if response == {'error': 'Unable to geocode'}:
        address = 'None'
    else:
        address = response['display_name']
    assert (address == expected_name)


# reverse with osm_type & osm_id
@pytest.mark.parametrize('osm_type, osm_id, expected_name', read_file('test_data_reverse_osm_type_id.xlsx'))
def test_reverse_search_osm(osm_type, osm_id, expected_name):
    response = requests.get(url_reverse_search, {'osm_type': osm_type, 'osm_id': int(osm_id), 'format': 'json',
                                                 'accept-language': 'en'}).json()
    if response == {'error': 'Unable to geocode'}:
        address = 'None'
    else:
        address = response['display_name']
    assert (address == expected_name)
