import matplotlib.pyplot as plt
import pandas as pd
import csv
from loguru import logger


@logger.catch

@logger.catch
def get_CSV_data():
    """Return a dict of CSV keys/values"""
    readings_by_location = {}
    # Open the CSV file and read the contents
    # TODO make compat with zipped csv
    # TODO make interactive to choose from several
    # TODO make to choose most recent from directory automatically    
    try:
        with open("20230225_HVAC_temps.csv", "r") as f:
            reader = csv.DictReader(f)
            # Iterate through the rows of the CSV file
            for row in reader:
                device = row["device location"]
                observation = (row["temperature"], row["most recent date accessed"])
                # TODO allow specification of minimum/maximum sample rate by discarding extra samples
                if device in readings_by_location.keys():
                    readings_by_location[device] = readings_by_location[device] + [observation]
                else:
                    readings_by_location[device] = [observation]
    except FileNotFoundError as err:
        return None            
    return readings_by_location


@logger.catch
def send_data_to_csv(data):
    """Send a dict to CSV and return the filename."""
    # Open the output CSV file and write the results
    out_csv = "temperature_Report.csv"
    with open(out_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name", "Temp", "Time"])
        for location_name, location_details in data.items():
            for val in location_details:
                writer.writerow([location_name, val[0], val[1]])
    return out_csv


@logger.catch
def main():
    # access the data
    readings = get_CSV_data()
    if readings == None:
        logger.info(f'No input found.')
        return
    
    # send the dict data to a new CSV
    outputfile = send_data_to_csv(readings)
    print(f"Output file saved as {outputfile}.")

    df = pd.read_csv(outputfile)
    print(df)

    df = df.pivot_table(index="Time", columns="Name", values="Temp")
    # df = df.fillna(df.avg())
    df = df.interpolate()
    # df = df.rolling(window=3, min_periods=1).mean()
    # df = df.interpolate(method='polynomial', order=2)
    print(df)

    ax = df.plot.line()
    ax.set_ylabel("Temperature")
    ax.set_title(f"HVAC 3023 old hill")
    # print(ax)
    # plt.draw()
    plt.pause(60 * 60 * 24)
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
