from nicegui import ui


# basic button
ui.label('Hello NiceGUI!')
ui.button('BUTTON', on_click=lambda: ui.notify('button was pressed'))


# basic table
table = ui.table({
    'columnDefs': [
        {'headerName': 'Name', 'field': 'name'},
        {'headerName': 'Age', 'field': 'age'},
    ],
    'rowData': [
        {'name': 'Alice', 'age': 18},
        {'name': 'Bob', 'age': 21},
        {'name': 'Carol', 'age': 42},
    ],
}).classes('max-h-40')

def update():
    table.options['rowData'][0]['age'] += 1
    table.update()

ui.button('Update', on_click=update)
ui.run()