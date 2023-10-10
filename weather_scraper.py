import os as os
import contextlib as contextlib
import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Global variables needed by various functions.
g_two_am = 7200  # Number of seconds of the day corresponding to 2:00AM
g_sec_per_hour = 3600
g_sec_per_day = 86400
g_century = '20'


def get_weather(full_date_str, event_time, station, timezone_conversion=0, is_dst=False, return_string=False):
    """Scrapes weather underground and returns the weather at the approximate time of an event.

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

    """
    if not is_valid_date(full_date_str):
        raise ValueError('ValueError: Not a valid date.')

    full_date_str, event_time = convert_to_local(full_date_str, event_time, timezone_conversion, is_dst)
    weather_table = scrape_weather(full_date_str, station)

    if weather_table is not None:
        # Finds the time in the table that's closest to the time of the event
        index = 0
        best_diff = float('inf')
        best_index = 0
        for clock_hour in weather_table['Time']:
            if type(clock_hour) != float:
                time_sec = convert_clock_hour(clock_hour)
                time_diff = abs(event_time - time_sec)
                if time_diff < best_diff:
                    best_diff = time_diff
                    best_index = index
            else:
                break

            index += 1

        # Gets the weather conditions at the closest hour to the event and the surrounding hour_padding hours
        weather = []
        hour_padding = 3
        for i in range(best_index - hour_padding, best_index + hour_padding + 1):
            if 0 <= i < index:
                weather.append(weather_table['Condition'][i])
            else:
                weather.append(None)

        if return_string:
            weather_string = ''
            hour = -hour_padding
            for condition in weather:
                if condition:
                    if hour < 0:
                        weather_string += f'{condition} ({hour}hr), '
                    elif hour == 0:
                        weather_string += f'{condition} (during)'
                    else:
                        weather_string += f', {condition} ({hour}hr)'

                hour += 1

            return weather_string
        else:
            lightning_variations = ['Thunder', 'T-Storm', 'Storm', 'Lightning', 'Hail']
            heavy_rain = False
            rain = False
            print(weather)
            for condition in weather:
                if condition:
                    for variation in lightning_variations:
                        if variation in condition:
                            return 3

                    if 'Heavy' in condition:
                        heavy_rain = True
                    elif 'Rain' in condition:
                        rain = True

            if heavy_rain:
                return 2
            elif rain:
                return 1

            return 0

    else:
        if return_string:
            return 'Not found'
        else:
            return -1


def scrape_weather(full_date_str, station):
    """Scrapes weather from weather underground and returns the results as a pandas data frame.

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

    """
    try:
        # Note: selenium and lxml modules are required to make this work. Install them
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # Runs the chrome client in headless mode
        with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):  # Prevents selenium from printing status stuff
            driver = webdriver.Chrome(options=chrome_options)

            url = f'https://www.wunderground.com/history/daily/{station}/date/{full_date_str}'

            driver.get(url)
            tables = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table")))

        table = pd.read_html(tables[1].get_attribute('outerHTML'))[0]

        return table  # This is a dataframe containing the table we want

    except:
        return None


def full_date_to_short(full_date_str):
    """Converts a date string of the form yyyy-mm-dd to the form yymmdd."""
    return full_date_str[2:].replace('-', '')


def short_to_full_date(date_str):
    """Converts a date string of the form yymmdd to the form yyyy-mm-dd."""
    return f'{g_century}{date_str[0:2]}-{date_str[2:4]}-{date_str[4:]}'


def days_per_month(month, year):
    """Returns the number of days in the requested month based on the year."""
    month_dict = {'1': 31,  # January
                  '2': 29 if year % 4 == 0 or (year % 100 != 0 and year % 400 == 0) else 28,  # February
                  '3': 31,  # March
                  '4': 30,  # April
                  '5': 31,  # May
                  '6': 30,  # June
                  '7': 31,  # July
                  '8': 31,  # August
                  '9': 30,  # September
                  '10': 31,  # October
                  '11': 30,  # November
                  '12': 31}  # December
    return month_dict[str(month)]


def roll_date_forward(date_str):
    """Returns the calendar date after the one given as an argument."""
    date_int = int(date_str)
    date_int += 1
    date_str = str(date_int)
    # Month rollover
    if int(date_str[4:]) > days_per_month(int(date_str[2:4]), int(g_century + date_str[0:2])):
        date_int = date_int + 100 - (int(date_str[4:]) - 1)
        date_str = str(date_int)

    # Year rollover
    if int(date_str[2:4]) > 12:
        date_int = (date_int // 10000 + 1) * 10000 + 101
        date_str = str(date_int)

    return date_str


def roll_date_backward(date_str):
    """Returns the calendar date before the one given as an argument."""
    date_int = int(date_str)
    date_int -= 1
    date_str = str(date_int)
    # Year rollback
    if int(date_str[2:]) == 100:  # This would be January 0th because int(0100) = 100
        date_int = (date_int // 10000 - 1) * 10000 + 1231  # December 31st of the previous year
        date_str = str(date_int)

    # Month rollback
    if int(date_str[4:]) == 0:
        date_int -= 100
        date_int += days_per_month(int(str(date_int)[2:4]), int(g_century + date_str[0:2]))
        date_str = str(date_int)

    return date_str


def dst_status(date_str):
    """Returns string statuses depending on whether a day falls inside/outside/on the edge of dst."""
    year = int(g_century + date_str[0:2])
    month = int(date_str[2:4])
    day = int(date_str[4:])

    # January, February, and December are never DST
    if month < 3 or month > 11:
        return 'outside'
    # April to October are always DST
    elif 3 < month < 11:
        return 'inside'
    # DST starts on the second Sunday of March (which is always between the 8th and the 14th)
    elif month == 3:
        second_sunday = 8 + (6 - dt.datetime(year, month, 8).weekday())
        if day < second_sunday:
            return 'outside'
        elif day > second_sunday:
            return 'inside'
        else:
            return 'beginning'
    # DST ends on the first Sunday of November (so the previous Sunday must be before the 1st)
    else:
        first_sunday = 1 + (6 - dt.datetime(year, month, 1).weekday())
        if day < first_sunday:
            return 'inside'
        elif day > first_sunday:
            return 'outside'
        else:
            return 'end'


def dst_conversion(date_str, event_time, timezone_conversion):
    """Returns an updated utc to local conversion number depending on the given date and time."""
    temp_time = event_time + (timezone_conversion * g_sec_per_hour)
    if temp_time > g_sec_per_day:
        temp_time -= g_sec_per_day
        temp_date = roll_date_forward(date_str)
    elif temp_time < 0:
        temp_time += g_sec_per_day
        temp_date = roll_date_backward(date_str)
    else:
        temp_date = date_str

    temp_date_status = dst_status(temp_date)
    if temp_date_status == 'inside':  # Squarely inside dst
        return timezone_conversion + 1
    elif temp_date_status == 'outside':  # Squarely outside dst
        return timezone_conversion
    elif temp_date_status == 'beginning':  # Beginning of dst (2nd Sunday of March at 2:00AM)
        if temp_time >= g_two_am:
            return timezone_conversion + 1
        else:
            return timezone_conversion
    else:  # End of dst (1st Sunday of November at 2:00AM)
        if (temp_time + g_sec_per_hour) >= g_two_am:  # + sec_per_hour b/c temp time should be in dst
            return timezone_conversion
        else:
            return timezone_conversion + 1


def convert_to_local(full_date_str, event_time, timezone_conversion, is_dst):
    """Converts the detector date and event time to what they would actually be in local time."""
    date_str = full_date_to_short(full_date_str)

    # Corrects the UTC conversion if we're in daylight savings time
    if is_dst:
        timezone_conversion = dst_conversion(date_str, event_time, timezone_conversion)

    # If the event happened the next day local time
    if (event_time + (g_sec_per_hour * timezone_conversion)) > g_sec_per_day:
        date_str = roll_date_forward(date_str)
        event_time = (event_time + (g_sec_per_hour * timezone_conversion)) - g_sec_per_day
    # If the event happened the previous day local time
    elif (event_time + (g_sec_per_hour * timezone_conversion)) < 0:
        date_str = roll_date_backward(timezone_conversion)
        event_time = (event_time + (g_sec_per_hour * timezone_conversion)) + g_sec_per_day
    else:
        event_time = event_time + (g_sec_per_hour * timezone_conversion)

    return short_to_full_date(date_str), event_time


def convert_clock_hour(clock_hour):
    """Converts a timestamp of the form hh:mm AM/PM into seconds since the beginning of the day."""

    meridiem = clock_hour.split()[1]
    hour = int(clock_hour.split()[0].split(':')[0])
    minute = int(clock_hour.split()[0].split(':')[1])

    # Converting from 12 hour time to 24 hour time
    if meridiem == 'AM' and hour == 12:  # midnight
        hour = 0
    elif meridiem == 'PM' and hour == 12:  # noon
        pass
    elif meridiem == 'PM':  # PM conversion
        hour += 12

    return float((hour * g_sec_per_hour) + (minute * 60))


def is_valid_date(full_date_str):
    if len(full_date_str) != 10:
        return False

    valid = (full_date_str[0:4].isdigit()
             and full_date_str[5:7].isdigit()
             and full_date_str[8:].isdigit()
             and full_date_str[4] == '-'
             and full_date_str[7] == '-')
    return valid
