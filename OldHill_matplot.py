import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import csv
from loguru import logger

@logger.catch
def main():
    readings_by_location = {}
    # Open the CSV file and read the contents
    with open('20230120_HVAC_temps.csv', 'r') as f:
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

    # print(f'READINGS BY LOCATION DICT:\n{readings_by_location}')

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
    # df = df.fillna(df.avg())
    df = df.interpolate()
    # df = df.rolling(window=3, min_periods=1).mean()
    # df['Temp'] = df['Temp'].interpolate(method='polynomial', order=2)
    print(df)

    ax = df.plot.line()
    ax.set_ylabel('Temperature')
    ax.set_title(f"HVAC 3023 old hill")
    # print(ax)
    #plt.draw()
    plt.pause(60*60*24)
    return


main()

"""
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('20230116_HVAC_temps_new.csv')


# Use the plot() function to create a line plot of the data
#plt.plot(df['most recent date accessed'], df['temperature'])

# Add labels and title
plt.xlabel('X-axis Label')
plt.ylabel('Y-axis Label')
plt.title('Your Title')

# Show the plot
plt.show()

# Create a line plot of 'highest value' vs 'highest date'
plt.plot(df['most recent date accessed'], df['temperature'])
"""