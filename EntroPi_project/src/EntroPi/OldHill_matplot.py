import matplotlib.pyplot as plt
import pandas as pd
import csv
from loguru import logger
from file_search_5 import let_user_choose

@logger.catch
def main():
    readings_by_location = {}
    dataset = let_user_choose() # dataset is a _TemporaryFileWrapper object
    # Open the CSV file and read the contents
    with open(dataset.name, "r") as f:
        logger.info(f'Loading data from: {dataset.name}')
        reader = csv.DictReader(f)
        # Iterate through the rows of the CSV file
        for row in reader:
            r = row["device location"]
            v = (row["temperature"], row["most recent date accessed"])
            # TODO allow specification of minimum/maximum sample rate by discarding extra samples
            if r in readings_by_location.keys():
                readings_by_location[r] = readings_by_location[r] + [v]
            else:
                readings_by_location[r] = [v]

    # logger.info(f'READINGS BY LOCATION DICT:\n{readings_by_location}')

    # Open the output CSV file and write the results
    out_csv = "temperature_Report.csv"

    with open(out_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name", "Temp", "Time"])
        for key, value in readings_by_location.items():
            for val in value:
                writer.writerow([key, val[0], val[1]])

    logger.info(f"Output file saved as {out_csv}.")

    df = pd.read_csv("temperature_Report.csv")
    logger.info(df)

    df = df.pivot_table(index="Time", columns="Name", values="Temp")
    # df = df.fillna(df.avg())
    df = df.interpolate()
    # df = df.rolling(window=3, min_periods=1).mean()
    # df['Temp'] = df['Temp'].interpolate(method='polynomial', order=2)
    logger.info(df)

    ax = df.plot.line()
    ax.set_ylabel("Temperature")
    ax.set_title(f"HVAC 3023 old hill")
    # logger.info(ax)
    # plt.draw()
    plt.pause(60 * 60 * 24)
    return


main()
