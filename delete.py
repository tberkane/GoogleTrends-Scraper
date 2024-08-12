import os
import csv

def is_second_column_empty(file_path):
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            if len(row) > 1 and row[1].strip():
                return False
    return True

def delete_empty_csv_files(directory):
    deleted_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            if is_second_column_empty(file_path):
                os.remove(file_path)
                deleted_files.append(filename)
    return deleted_files

# Directory path
results_dir = 'results/'

# Delete empty CSV files and get the list of deleted files
deleted = delete_empty_csv_files(results_dir)

# Print the results
if deleted:
    print(f"Deleted {len(deleted)} files:")
    for file in deleted:
        print(f"- {file}")
else:
    print("No files were deleted.")