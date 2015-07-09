import logging

import requests
from spacebot.util.utils import field

log = logging.getLogger(__name__)


# Gets the position of the ISS from https://api.wheretheiss.at/v1/satellites/25544
def get_iss_data():
    r = requests.get("https://api.wheretheiss.at/v1/satellites/25544")
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
