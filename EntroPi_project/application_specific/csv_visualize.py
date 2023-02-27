import matplotlib.pyplot as plt
import pandas as pd
import csv
from loguru import logger


@logger.catch
def main():
    # TODO simplify this. Much of this could be done by pandas.
    #        At the time of writing I was struggling to correctly display the data
    #          and went about manually discarding data from the CSV. Pandas can drop the data quicker and better.

    readings_by_location = {}
    # Open the CSV file and read the contents
    with open('20230125_HVAC_temps.csv', 'r') as f:
        # TODO make compat with zipped csv 
        # TODO make interactive to choose from several
        # TODO make to choose most recent from directory automatically
        reader = csv.DictReader(f)
        # Iterate through the rows of the CSV file
        for row in reader:
            r = row['device location']
            v = (row['temperature'], row['most recent date accessed'])
            # TODO allow specification of minimum/maximum sample rate by discarding extra samples
            if r in readings_by_location.keys():
                readings_by_location[r] = readings_by_location[r] + [v]
            else:
                readings_by_location[r] = [v]

    # Open the output CSV file and write the results
    out_csv = 'temperature_Report.csv'
    with open(out_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Temp', 'Time'])
        for key, value in readings_by_location.items():
            for val in value:
                writer.writerow([key, val[0], val[1]])
    print(f'Output file saved as {out_csv}.')  



    df = pd.read_csv('temperature_Report.csv')
    print(df)

    df = df.pivot_table(index='Time', columns='Name', values='Temp')
    # smooth the missing values in the dataframe. Various options exist
    # df = df.fillna(df.avg())
    df = df.interpolate()
    # df = df.rolling(window=3, min_periods=1).mean()
    # df['Temp'] = df['Temp'].interpolate(method='polynomial', order=2)
    print(df)

    try:
        ax = df.plot.line() # NOTE: a dataframe without any 'columns' data (e.g. NaN) will trigger an error
    except TypeError as error:
        # TODO log this error
        print(f'{error} ::: Could the data be missing labels for sensor locations?')
        exit()
    ax.set_ylabel('Temperature')
    ax.set_title(f"HVAC 3023 old hill")
    plt.pause(60*60*24)
    return


if __name__ == '__main__':
    main()
