from nicegui import ui
from htr_readings import retrieve_json

SENSOR_JSON_FILE = "w1devices.json"
# read the JSON file
device_data = retrieve_json(SENSOR_JSON_FILE)

# pick a sample data element
random_key = list(device_data.keys())[0]
values = device_data[random_key]

Column_definitions = []
# declare all the column names
for k, v in values.items():
    fieldname = f"field:{k}"
    Column_definitions = Column_definitions + [{"headerName": k, "field": fieldname}]
# add a cloumn for the key value in the data table
Column_definitions = [
    {"headerName": "Device ID", "field": "field:Device ID"}
] + Column_definitions

# build all the table data
Row_Data = []
# step through the data
for key, values in device_data.items():
    device_table = {f"field:Device ID": key}
    # step through the device values
    for name, data in values.items():
        # add the descriptor 'field:' onto each data item in the dict.
        device_table[f"field:{name}"] = data

    # add the dict to the Row Data
    Row_Data = Row_Data + [device_table]

# format the 2 lists of dicts into the NiceGUI table form
table_definition = {"columnDefs": Column_definitions, "rowData": Row_Data}


# basic button
ui.label("Hello NiceGUI!")
ui.button("BUTTON", on_click=lambda: ui.notify("button was pressed"))


# basic table
table = ui.table(table_definition).classes("max-h-50")


def update():
    table.options["rowData"][0]["field:device type"] += 1
    table.update()


def handle_click(sender):
    """returns:
    {'id': 6,
     'type': 'cellClicked',
     'args': {'value': actual value of field clicked,
              'rowIndex': 0,
              'data': dict of entire row,
              'colId': fieldname clicked,
              'selected': bool
              'rowHeight': int,
              'rowID': str
              }
     }
    """
    print(f"\n{sender}\n")
    # TODO log sender value
    if sender["type"] == "cellClicked":
        # offer user option to edit value of field
        # TODO limit editable fields to device location
        if sender["args"]["colId"] == "field:device location":
            old_value = sender["args"]["value"]
            ui.input(
                label="New location description",
                placeholder=old_value,
                on_change=lambda e: result.set_text("you typed: " + e.value),
            )
            result = ui.label()
        else:
            ui.notify("That field is NOT editable")

    return  # nothing is expected in return as far as I know


table.on("cellClicked", handle_click)

ui.button("Update", on_click=update)
ui.run()
