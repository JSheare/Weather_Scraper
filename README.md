# Weather_Scraper
Python module with functions that get weather info from the web and look for conditions that indicate TGFs.

Note - the following python packages are required for the module to function properly:
- Pandas
- lxml
- Selenium

There are two main functions in the module: get_weather and scrape_weather.

get_weather: <br />
Scrapes weather underground and returns the weather at the approximate time of an event.

    Parameters
    ----------
    full_date_str : str
        The date to scrape weather for in the format yyyy-mm-dd.
    event_time : float
        The time that the event occurred at in seconds since the beginning of the day.
    station : str
        The closest weather station to the event.
    timezone_conversion : int
        A number representing the timezone conversion to the event's local timezone.
    is_dst : bool
        Optional. Whether the event occurred in a place where daylight savings time is observed.
    return_string : bool
        Optional. Instead of returning a status code, the function will return the weather conditions as a string.

    Returns
    -------
    int / string
        An integer status code by default. Returns a string if return_string is True.

        Status code meanings:

        3 - Confirmed lightning / Hail

        2 - Heavy Rain

        1 - Rain/Light Rain

        0 - Clear

        -1 - Weather data retrieval failure

<br />
scrape_weather: <br />
Scrapes weather from weather underground and returns the results as a pandas data frame.

    Parameters
    ----------
    full_date_str : str
        The date to scrape weather for in the format yyyy-mm-dd.
    station : str
        The weather station to scrape weather info from.

    Returns
    -------
    pd.DataFrame
        A pandas data frame containing the weather info for the requested date.
