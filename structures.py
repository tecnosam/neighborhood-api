from math import sin, cos, atan2, sqrt, pi

def haversine(pos1, pos2):
    lat1 = float(pos1['x'])
    long1 = float(pos1['y'])
    lat2 = float(pos2['x'])
    long2 = float(pos2['y'])

    degree_to_rad = float(pi / 180.0)

    d_lat = (lat2 - lat1) * degree_to_rad
    d_long = (long2 - long1) * degree_to_rad

    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    km = 6367 * c
    mi = 3956 * c
    return km

def search( target, values, key = lambda x: x ):
    high = len(values)
    low = 0
    while low <= high:
        mid = ( low + high ) // 2
        if ( key(target) == key( values[mid] ) ):
            return mid
        elif ( key(target) < key( values[mid] ) ):
            high = mid - 1
        elif ( key( target ) > key( values[mid] ) ):
            low = mid + 1
    
    return None