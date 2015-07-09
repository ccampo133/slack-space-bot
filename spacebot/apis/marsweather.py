import logging

import requests

log = logging.getLogger(__name__)


# Grabs the latest weather report on Mars, from http://marsweather.ingenology.com/
# The above API is actually a wrapper around http://cab.inta-csic.es/rems/rems_weather.xml,
# which provides data from the REMS instrument on the Curiosity rover. See:
# http://cab.inta-csic.es/rems/rems-an-instrument-for-mars-environmental-monitoring/
def get_mars_weather():
    r = requests.get("http://marsweather.ingenology.com/v1/latest")
    assert r.status_code == 200
    response = r.json()
    log.debug("Mars Weather response: %s", response)
    return response["report"]  # We only care about the inner report object


def weather_emoji(opacity):
    return {
        "Cloudy": ":cloud:",
        "Dust_devils_and_strong_winds": ":dash:",
        "Fog": ":foggy:",
        "Frost": ":snowflake:",
        "Ice_and_fog": ":snowflake:",
        "Snow": ":snowflake:",
        "Storm": ":umbrella:",
        "Sunny_and_cloudy": ":party_sunny",
        "Sunny": ":sunny:",
        "Windy": ":dash:"
    }.get(opacity, ":question:")


def get_weather_text_and_attachments():
    data = get_mars_weather()
    fields = [
        field("Terrestrial Date", data["terrestrial_date"]),
        field("Sol", data["sol"]),
        field("Solar Longitude", "{0} degrees".format(data["ls"])),
        field("Season", data["season"]),
        field("Atmospheric Conditions", "{0} {1}".format(data["atmo_opacity"], weather_emoji(data["atmo_opacity"]))),
        field("Minimum Temperature", "{0} F ({1} C)".format(data["min_temp_fahrenheit"], data["min_temp"])),
        field("Maximum Temperature", "{0} F ({1} C)".format(data["max_temp_fahrenheit"], data["max_temp"])),
        field("Atmospheric Pressure", "{0} Pa ({1})".format(data["pressure"],
                                                            pressure_string(data["pressure_string"]))),
        field("Relative Humidity", "{0} %".format(data["abs_humidity"])),
        field("Wind Speed", "{0} m/s".format(data["wind_speed"])),
        field("Wind Direction", data["wind_direction"]),
        field("Sunrise :sunrise:", data["sunrise"]),
        field("Sunset :sunrise_over_mountains:", data["sunset"])
    ]
    attachments = {"fields": fields}
    return ":star: *Latest Martian Weather Report From Curiosity* :star:", attachments


def pressure_string(p_string):
    return "above average" if p_string == "Higher" else "below average"


def field(name, value, short=True):
    return {"title": name, "value": value, "short": short}
