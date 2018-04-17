def distance(latitude1, longitude1, latitude2, longitude2):
    return sqrt(((float(latitude2) - float(latitude1)) ** 2) +
                ((float(longitude2) - float(longitude1)) ** 2))
