import json as json
import glob as glob
import os as os
import psutil as psutil

import weather_scraper as ws


def make_file(unit, checked_dates, weather_path, deployment_file_path):
    # Getting a list of all deployment files for this unit
    files = glob.glob(f'{deployment_file_path}/{unit}_*_*.json')
    for file in files:
        with open(file, 'r') as deployment:
            location = json.load(deployment)

        station = location['Nearest weather station']
        if station not in checked_dates:  # Making an entry for a new station/deployment
            checked_dates[station] = []

        dates = ws.make_date_list(location['Start date'], location['End date'])
        for date in dates:
            if date not in checked_dates[station]:
                max_retries = 10
                retries = 0
                weather_data = None
                # Get weather dataframe. In case it doesn't work the first time, we retry a few more times
                while retries < max_retries:
                    weather_data = ws.scrape_weather(ws.short_to_full_date(date), station)
                    if weather_data is not None:
                        break

                    retries += 1

                # Writes the weather data to a file if we managed to get it and adds it to the list of checked dates
                if weather_data is not None:
                    weather_data.to_json(f'{weather_path}/{station}_{date}.json')
                    checked_dates[station].append(date)
                    with open(f'{weather_path}/checked_dates.json', 'w') as date_file:
                        json.dump(checked_dates, date_file)

    return checked_dates


def main():
    # Where all the weather files will go
    weather_path = 'home/jacob/search/Weather'
    if not os.path.exists(weather_path):
        os.makedirs(weather_path)

    # Checks to see if the program is already running
    try:
        with open(f'{weather_path}/pid.txt', 'r') as existing_pid_file:
            pid = int(existing_pid_file.readline())
            if psutil.pid_exists(pid):
                exit()
            else:
                raise FileNotFoundError

    # Runs the program normally if it isn't
    except FileNotFoundError:
        with open(f'{weather_path}/pid.txt', 'w') as pid_file:
            pid_file.write(str(os.getpid()))

        try:
            with open(f'{weather_path}/checked_dates.json', 'r') as date_file:
                checked_dates = json.load(date_file)

        # If the list ever gets deleted by accident
        except FileNotFoundError:
            checked_dates = {}

        # Running the main program on each of the detectors

        # THOR1
        checked_dates = make_file('THOR1', checked_dates, weather_path, '/media/AllDetectorData/Detectors/THOR')

        # THOR2
        checked_dates = make_file('THOR2', checked_dates, weather_path, '/media/AllDetectorData/Detectors/THOR')

        # THOR3
        checked_dates = make_file('THOR3', checked_dates, weather_path, '/media/AllDetectorData/Detectors/THOR')

        # THOR4
        checked_dates = make_file('THOR4', checked_dates, weather_path, '/media/AllDetectorData/Detectors/THOR')

        # THOR5
        checked_dates = make_file('THOR5', checked_dates, weather_path, '/media/AllDetectorData/Detectors/THOR')

        # THOR6
        checked_dates = make_file('THOR6', checked_dates, weather_path, '/media/AllDetectorData/Detectors/THOR')

        # GODOT
        checked_dates = make_file('GODOT', checked_dates, weather_path, '/media/AllDetectorData/Detectors/GODOT')

        # SANTIS
        checked_dates = make_file('SANTIS', checked_dates, weather_path, '/media/AllDetectorData/Detectors/SANTIS')

        # Deletes the pid file
        os.remove(f'{weather_path}/pid.txt')


if __name__ == '__main__':
    main()
