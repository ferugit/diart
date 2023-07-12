import sqlite3
from openpyxl import Workbook

conn = sqlite3.connect('/home/azureuser/resources/output/temp_output.db')
cursor = conn.cursor()

# List of specific tables you want to read
tables = ['trial_params', 'trial_values', 'trials']

wb = Workbook()

for table in tables:
    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()

    # Create a new sheet for each table
    ws = wb.create_sheet(title=table)

    for row in rows:
        ws.append(row)

wb.save('/home/azureuser/resources/output/db_file.xlsx')

cursor.close()
conn.close()
