"""A script that prints weather information for a given range of dates."""
import weather_scraper as ws


def get_valid_date(message):
    while True:
        date = input(message)
        if ws.is_valid_date(date):
            return date

        print('Not a valid date.')


def main():
    first_date = ws.full_date_to_short(get_valid_date('Enter the first date (yyyy-mm-dd): '))
    second_date = ws.full_date_to_short(get_valid_date('Enter the second date (yyyy-mm-dd: '))
    station = input('Enter the nearest weather station (4-letter call sign): ')

    requested_dates = [ws.short_to_full_date(first_date)]
    if first_date != second_date:
        date_str = first_date
        century = '20'
        while True:
            date_str = ws.roll_date_forward(date_str)

            if date_str == second_date:
                requested_dates.append(ws.short_to_full_date(date_str))
                break
            else:
                requested_dates.append(ws.short_to_full_date(date_str))

    log = open('Lightning_Summary.txt', 'w')

    for full_date_str in requested_dates:
        print(f'{full_date_str}:')
        print(f'{full_date_str}:', file=log)
        weather_table = ws.scrape_weather(full_date_str, station)
        if weather_table is not None:
            found = False
            for i in range(len(weather_table['Condition'])):
                condition = weather_table['Condition'][i]
                if type(condition) != float:
                    for variation in ['Thunder', 'T-Storm', 'Storm', 'Lightning', 'Hail']:
                        if variation in condition:
                            found = True
                            print(f'{condition} at {weather_table["Time"][i]}')
                            print(f'{condition} at {weather_table["Time"][i]}', file=log)
                            break

                else:
                    break

            if not found:
                print('Nothing found')
                print('Nothing found', file=log)

        else:
            print('Error getting table')
            print('Error getting table', file=log)

        print('')
        print('', file=log)

    log.close()


if __name__ == '__main__':
    main()
