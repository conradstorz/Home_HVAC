import matplotlib.pyplot as plt
import pandas as pd
import csv
from loguru import logger


@logger.catch
def main():
    readings_by_location = {}
    # Open the CSV file and read the contents
    with open("20230122_HVAC_temps.csv", "r") as f:
        # TODO make compat with zipped csv
        """03-02-2023 ChatGPT suggested code for dealing with zip files and multiple CSV files inside or outside of a zip.
        import glob
        import zipfile
        import io

        # Find all the CSV files in the current directory, including those in zip files
        csv_files = []
        for file in glob.glob("*"):
            if file.endswith(".csv"):
                csv_files.append(file)
            elif file.endswith(".zip"):
                with zipfile.ZipFile(file, 'r') as zip:
                    for zip_file in zip.namelist():
                        if zip_file.endswith(".csv"):
                            csv_files.append(f"{file}!{zip_file}")

        # Print out the list of CSV files
        print('Available files:')
        for i, file in enumerate(csv_files):
            print(f'{i+1}. {file}')

        # Prompt the user to select a file
        while True:
            try:
                selection = int(input('Enter the number of the file you want to use: '))
                if selection < 1 or selection > len(csv_files):
                    raise ValueError
                break
            except ValueError:
                print(f'Invalid selection. Please enter a number between 1 and {len(csv_files)}')

        # Get the selected file name and, if it's in a zip file, decompress it to a temporary file
        selected_file = csv_files[selection-1]
        if "!" in selected_file:
            zip_file, csv_file = selected_file.split("!")
            with zipfile.ZipFile(zip_file, 'r') as zip:
                with zip.open(csv_file) as csv:
                    temp_file = io.StringIO(csv.read().decode())
        else:
            temp_file = open(selected_file, 'r')

        # Now you can use the temp_file variable to read the CSV data and plot the graph

        # Once you're done, make sure to close the temp_file
        temp_file.close()

        """
        # TODO make interactive to choose from several
        """ChatGPT suggested code for when there are too many files to reasonably display.
        import re
        import os
        import zipfile
        import io

        csv_files = []

        # Find all the CSV files in the current directory
        for file in os.listdir():
            if file.endswith(".csv"):
                csv_files.append(file)
            elif file.endswith(".zip"):
                with zipfile.ZipFile(file, 'r') as zip:
                    for zip_file in zip.namelist():
                        if zip_file.endswith(".csv"):
                            csv_files.append(f"{file}!{zip_file}")

        # Prompt the user to enter a search query
        print("Enter a search query to find the file you want to plot.")
        while True:
            search_query = input("Search: ")
            # Sanitize the search query
            search_query = re.sub(r"[^a-zA-Z0-9_ ]", "", search_query)
            if search_query:
                break
            else:
                print("Invalid search query. Please try again.")

        # Filter the list of CSV files based on the search query
        filtered_csv_files = [f for f in csv_files if search_query in f]
        if not filtered_csv_files:
            print("No matching files found.")
            exit()
        elif len(filtered_csv_files) == 1:
            file = filtered_csv_files[0]
        else:
            # Display the list of matching CSV files to the user
            print("Matching files:")
            for i, file in enumerate(filtered_csv_files):
                print(f"{i+1}. {file}")
            # Prompt the user to choose a file
            while True:
                choice = input("Enter the number of the file you want to plot (q to quit): ")
                if choice == "q":
                    exit()
                try:
                    index = int(choice) - 1
                    file = filtered_csv_files[index]
                    break
                except (ValueError, IndexError):
                    print("Invalid choice. Please try again.")
    
        """
        # TODO make to choose most recent from directory automatically
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
