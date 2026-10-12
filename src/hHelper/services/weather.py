import os, requests, json, sqlite3
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime,timedelta,timezone
from services_exceptions import ( 
    WeatherAPIKeyMissingError, 
    WeatherDataFetchFailureError, 
    WeatherDataParameterNotFoundError, 
    MisuseOfWeatherAPIError,
    WeatherDataCacheDatabaseUnaccessibleError,
    WeatherDatabaseConnectionClosedPrematurelyError
)

BASE_URL = "http://api.weatherapi.com/v1/forecast.json"

class WeatherData:
    def __init__(self, UUID = "0", TIME = None, LOCATION = "Krasnoyarsk", weather_data = None) -> None:
        self.UUID = UUID
        self.LOCATION = LOCATION
        if TIME is None:
            self.TIME = datetime.now(timezone.utc)
        else:
            self.TIME = TIME#its done utc by default so that in case system locale changes it doesnt breaks existing cached data
        self.weather_data = weather_data
    
    
    def __str__(self) -> str:
        return f"\"UUID:\"{self.UUID},\" LOCATION:\"{self.LOCATION},\" TIME:\"{self.TIME.isoformat()},\" WEATHERDATA:\"{self.weather_data}"

    def weather_fetch(self, units) -> None:
        try:
            load_dotenv()
            key = os.environ["WEATHER_API_KEY"]

        except KeyError:
            raise WeatherAPIKeyMissingError("Weather API Key not found in any environment variable")

        params = {
            "key" : key,
            "q" : self.LOCATION,
            "units" : units
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            self.weather_data = response.json()

        except requests.exceptions.HTTPError:
            raise WeatherDataFetchFailureError()

        #if not this error just let it be raised itself main caller's except shall handel it

    def weather_data_parser(self, units : str) -> str | None:#for general total weather data gist
        if self.weather_data is None:
            raise WeatherDataParameterNotFoundError()
        if units not in ("metric", "imperial"):
            raise MisuseOfWeatherAPIError(f"Metric and Imperial are the only valid unit options but recieved a request for {units}")
        try:
            if units=="metric":
                temp = round(self.weather_data["current"]["temp_c"])
                is_day = self.weather_data["current"]["is_day"]
                text = self.weather_data["current"]["condition"]["text"]
                wind_speed = round(self.weather_data["current"]["wind_kph"])
                will_rain = self.weather_data["current"]["will_it_rain"]
                will_snow = self.weather_data["current"]["will_it_snow"]
                feels_like = self.weather_data["current"]["feelslike_c"]
            elif units=="imperial":
                temp = round(self.weather_data["current"]["temp_f"])
                is_day = self.weather_data["current"]["is_day"]
                text = self.weather_data["current"]["condition"]["text"]
                wind_speed = round(self.weather_data["current"]["wind_mph"])
                will_rain = self.weather_data["current"]["will_it_rain"]
                will_snow = self.weather_data["current"]["will_it_snow"]
                feels_like = self.weather_data["current"]["feelslike_f"]
            directions = {
                    "N": "North", "NNE": "North-Northeast", "NE": "Northeast",
                    "ENE": "East-Northeast", "E": "East", "ESE": "East-Southeast",
                    "SE": "Southeast", "SSE": "South-Southeast", "S": "South",
                    "SSW": "South-Southwest", "SW": "Southwest", "WSW": "West-Southwest",
                    "W": "West", "WNW": "West-Northwest", "NW": "Northwest",
                    "NNW": "North-Northwest", "VRB": "Variable", "C": "Calm"
            }
            wind_direction = directions.get(self.weather_data["current"]["wind_dir"])       
        except KeyError:
            raise WeatherDataParameterNotFoundError("The data recieved was mal-formed, failed to parse the data")

        time_of_day = "daytime" if is_day else "nighttime"
        unit = "degree celcius" if units=="metric" else "degree fahrenheit"
        tldr_message = f"It is currently {time_of_day} and the weather condition is {text},with a temperature of around{temp} {unit} and it feels like {feels_like}{unit}"
        if not will_snow and not will_rain:
            extension_tldr = "and you can expect a clear day today! "
        if will_snow or will_rain:
            if will_rain:
                extension_tldr = "and some rainfall is expected so remember to carry an umbrella when you go out"
            else:
                extension_tldr = "and some snowfall is expected so its recommended to not go outside without proper safety gears"
        if will_snow and will_rain:
            extension_tldr = "theirs probablity of both rainfall and snowfall soon so its recommended to stay at home"

        if units == "metric":
            if wind_speed >= 20 and wind_speed <= 28:
                extension_tldr += f" expect some moderate breeze at {wind_speed}kilometer per hour towards {wind_direction}"
            elif wind_speed >= 29 and wind_speed <= 38:
                extension_tldr += f" expect some fresh breeze at {wind_speed}kilometer per hour towards {wind_direction}"
            elif wind_speed >= 39 and wind_speed <= 49:
                extension_tldr += f" expect some strong breeze at {wind_speed}kilometer per hour towards {wind_direction}"
            elif wind_speed >= 50 and wind_speed <= 61:
                extension_tldr += f" expect some high near gale breeze at {wind_speed}kilometer per hour towards {wind_direction} and its highly recommended to stay at home"
            elif wind_speed >= 62: 
                extension_tldr += f" a gale or extremely high winds is expected today at {wind_speed} kilometer per hour towards {wind_direction} and please dont go out in extreme situations like this, you are likely to get blown away"
            elif wind_speed <=19:
                extension_tldr += f" expect some calm moments with light breeze at {wind_speed}kilometer per hour towards {wind_direction}"
        if units == "imperial":
            if wind_speed >= 13 and wind_speed <= 18:
                extension_tldr += f" expect some moderate breeze at {wind_speed}miles per hour towards {wind_direction}"
            elif wind_speed >= 19 and wind_speed <= 24:
                extension_tldr += f" expect some fresh breeze at {wind_speed}miles per hour towards {wind_direction}"
            elif wind_speed >= 25 and wind_speed <= 31:
                extension_tldr += f" expect some strong breeze at {wind_speed}miles per hour towards {wind_direction}"
            elif wind_speed >= 32 and wind_speed <= 38:
                extension_tldr += f" expect some high near gale breeze at {wind_speed}miles per hour towards {wind_direction} and its highly recommended to stay at home"
            elif wind_speed >= 39: 
                extension_tldr += f" a gale or extremely high winds is expected today at {wind_speed} miles per hour towards {wind_direction} and please dont go out in extreme situations like this, you are likely to get blown away"
            elif wind_speed <=12:
                extension_tldr += f" expect some calm moments with light breeze at {wind_speed}miles per hour towards {wind_direction}"
        
        tldr_message += extension_tldr

        return tldr_message

    def is_day(self) -> Optional[bool]:
        if self.weather_data is not None:
            return True if self.weather_data["current"]["is_day"] else False
        else:
            return None

    def time_till_(self, user_localtime, till: str = "sunrise") -> timedelta | None:
        if self.weather_data is not None:
            try:
                astro = self.weather_data["forecast"]["forecastday"][0]["astro"]
            except KeyError:
                raise WeatherDataParameterNotFoundError("Parameter Astro not found in weather data")
            if till not in ("sunrise", "sunset"):
                return None

            t = datetime.strptime(astro[till], "%I:%M %p").time()
            now = user_localtime
            target = now.replace(hour = t.hour, minute = t.minute, second = 0, microsecond = 0)
            if target <= now:#if already passed today then use tomorrow 
                target += timedelta(days=1)
            return target - now
        else:
            return None

    def will_it_(self, what: str="snow") -> bool | None:
        if what not in ("rain", "snow") or self.weather_data is None:
            return None
        
        try:
            if what == "rain":
                will_rain = self.weather_data["current"]["will_it_rain"]
            else:
                will_snow = self.weather_data["current"]["will_it_snow"]
            return bool(will_rain if what == "rain" else will_snow)
        except KeyError:
            raise WeatherDataParameterNotFoundError(f"Parameter {what} not found in weather data")

class WeatherCacheSystem:
    def __init__(self, db_name: str="weather_cache.db") -> None:
        self.db_name = db_name
        try:
            self.conn = sqlite3.connect(self.db_name)
        except sqlite3.OperationalError:
            raise WeatherDataCacheDatabaseUnaccessibleError(f"Error connecting to weather cache database {db_name}")

        self.cursor = self.conn.cursor()
        self.cursor.execute('''Create table if not exists wdata (
                                location text primary key,
                                time text not null,
                                weather_data text not null
            )
            ''')
        self.conn.commit()

    def database_connection_checker(self) -> bool:
        try:
            self.cursor.execute("select 2+2")
            return True
        except sqlite3.ProgrammingError:
            return False

    def new_entry(self, wd: WeatherData) -> bool | None:
        if not self.database_connection_checker():
            raise WeatherDatabaseConnectionClosedPrematurelyError()
        self.database_clearer()
        self.cursor.execute("Select * from wdata where location = ? ",(wd.LOCATION,))
        data = self.cursor.fetchone()
        if data:
            return None
        if wd.weather_data is None:
            return None
        self.cursor.execute("Insert into wdata values(?, ?, ?)",(wd.LOCATION, wd.TIME.isoformat(), json.dumps(wd.weather_data)))
        self.conn.commit()
        return True

    def database_clearer(self) -> bool:
        if not self.database_connection_checker():
            raise WeatherDatabaseConnectionClosedPrematurelyError()
        cutoff_time = (datetime.now(timezone.utc) - timedelta(hours = 2)).isoformat()
        self.cursor.execute("Delete from wdata where time < ?",(cutoff_time,))
        self.conn.commit()
        return True

    def is_in_cache(self, LOCATION : str="Krasnoyarsk") -> bool:
        if not self.database_connection_checker():
            raise WeatherDatabaseConnectionClosedPrematurelyError()
        self.database_clearer()
        self.cursor.execute("Select * from wdata where location = ?",(LOCATION,))
        data = self.cursor.fetchone()
        if data:
            return True
        else:
            return False

    def datablob_to_weatherdata(self, UUID : str, datablob : Tuple[str,str,str]) -> WeatherData | None:
        if len(datablob) != 3:
            return None
        wd_obj = WeatherData(UUID = UUID, TIME = datetime.fromisoformat(datablob[1]), LOCATION = datablob[0],weather_data = json.loads(datablob[2]))
        return wd_obj

    def fetch_from_cache(self, UUID : str, LOCATION : str="Krasnoyarsk") -> WeatherData | None:
        if not self.database_connection_checker():
            raise WeatherDatabaseConnectionClosedPrematurelyError()
        self.database_clearer()
        self.cursor.execute("Select * from wdata where location = ?",(LOCATION,))
        data = self.cursor.fetchone()
        if data:
            return self.datablob_to_weatherdata(UUID, tuple(data))
