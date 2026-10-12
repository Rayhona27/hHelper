class hHelperError(Exception):#top level custom error
    def __init__(self, message, error_code=None):
        self.error_code = error_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class WeatherAPIKeyMissingError(hHelperError):
    def __init__(self, message: str = "Weather API Key cannot be found in any environment variable"):
        self.code = "EW001"
        super().__init__(message, self.code)

class WeatherDataFetchFailureError(hHelperError):
    def __init__(self, message: str = "Weather api call resulted in failure"):
        self.code = "EW002"
        super().__init__(message, self.code)

class WeatherDataParameterNotFoundError(hHelperError):
    def __init__(self, message: str = "Certain parameters missing from the fetched weather data"):
        self.code = "EW003"
        super().__init__(message, self.code)

class MisuseOfWeatherAPIError(hHelperError):
    def __init__(self, message: str = "This is not the intended way to use the data"):
        self.code = "EW004"
        super().__init__(message, self.code)

class WeatherDataCacheDatabaseUnaccessibleError(hHelperError):
    def __init__(self, message: str = "Error while connecting to database of weather data cache"):
        self.code = "EWC001"
        super().__init__(message, self.code)

class WeatherDatabaseConnectionClosedPrematurelyError(hHelperError):
    def __init__(self, message: str = "Connection to database has been severed prematurely"):
        self.code = "EWC002"
        super().__init__(message, self.code)