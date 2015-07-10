import logging
from math import sin, cos, atan2, sqrt, radians

import requests
from spacebot.util.utils import field

log = logging.getLogger(__name__)


# Gets the position of the ISS from https://api.wheretheiss.at/v1/satellites/25544
def get_iss_data():
    r = requests.get("https://api.wheretheiss.at/v1/satellites/25544", verify=False)
    assert r.status_code == 200
    response = r.json()
    log.debug("ISS location response: %s", response)
    return response


def get_iss_text_and_attachments():
    data = get_iss_data()
    fields = [
        field("Altitude", data["altitude"]),
        field("Linear Velocity", "{0} km/hr".format(data["velocity"])),
        field("Solar Latitude:", "{0} degrees".format(data["solar_lat"])),
        field("Solar Longitude", "{0} degrees".format(data["solar_lon"])),
        field("Latitude", "{0} degrees".format(data["latitude"])),
        field("Longitude", "{0} degrees".format(data["longitude"])),
        field("Footprint Diameter", "{0} km".format(data["footprint"])),
        field("Visibility", data["visibility"]),
    ]
    lat = data["latitude"]
    lon = data["longitude"]
    image_url = "https://maps.googleapis.com/maps/api/staticmap?markers={lat},{lon}&zoom=6&size=500x400" \
        .format(lat=lat, lon=lon)
    attachments = {"fields": fields, "image_url": image_url}
    return ":star: *Current Position of the ISS* :star:", attachments


# Determines if the ISS is overhead by computing the great circle distance
# between its latitude and longitude and a given latitude and longitude.
# TODO: verify this calculation -ccampo 2015-07-10
def is_iss_overhead(lat, lon):
    iss_data = get_iss_data()
    lat1 = radians(lat)
    lon1 = radians(lon)
    lat2 = radians(iss_data["latitude"])
    lon2 = radians(iss_data["longitude"])
    delta_lon = lon2 - lon1
    d = atan2(
        sqrt((cos(lat2) * sin(delta_lon)) ** 2 + (cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(delta_lon)) ** 2),
        sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(delta_lon))
    # 6372.795 is the average great-circle radius of the Earth in km, from Wikipedia
    iss_dist = 6372.795 * d
    return iss_dist <= iss_data["footprint"] / 2
