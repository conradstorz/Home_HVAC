import os
import tempfile
import zipfile

def find_csv_files():
    csv_files = []
    for filename in os.listdir('.'):
        if filename.endswith('.csv'):
            csv_files.append(filename)
        elif filename.endswith('.zip'):
            with zipfile.ZipFile(filename) as zip_file:
                for inner_filename in zip_file.namelist():
                    if inner_filename.endswith('.csv'):
                        csv_files.append(f'{inner_filename}({filename})')
    return csv_files

def select_csv_file(csv_files):
    print('Select a CSV file to process:')
    for i, filename in enumerate(csv_files):
        print(f'{i+1}: {filename}')
    selection = input('> ')
    try:
        selection_index = int(selection) - 1
        selected_filename = csv_files[selection_index]
    except (ValueError, IndexError):
        print('Invalid selection')
        return None
    return selected_filename

def extract_csv_from_zip(zip_filename, csv_filename):
    with zipfile.ZipFile(zip_filename) as zip_file:
        try:
            selected_file_data = zip_file.read(csv_filename).decode('utf-8')
        except KeyError:
            print(f"{csv_filename} not found in {zip_filename}")
            return None
    with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='') as temp_file:
        temp_file.write(selected_file_data)
    return temp_file

def process_csv_file(filename):
    # check if filename is a composite
    if filename.endswith('.zip)'):
        filename = filename[:-1]
        csvfile, zipfile = filename.split('(')
        print(f'{csvfile=}')
        print(f'{zipfile=}')
        # now extract csv file from zipfile
        return extract_csv_from_zip(zipfile, csvfile)
    # file is not compressed, copy to namedtempfile
    with open(filename, 'r') as csv_file:
        csv_data = csv_file.read()
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(csv_data)
    return temp_file
    
def let_user_choose():
    temp_file = None
    csv_files = find_csv_files()
    selected_filename = select_csv_file(csv_files)
    if selected_filename:
        temp_file = process_csv_file(selected_filename)
        print(f'CSV file copied to {temp_file.name}')
    return temp_file

if __name__ == '__main__':
    let_user_choose()
