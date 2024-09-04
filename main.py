from nicegui import ui
import pandas as pd
from io import StringIO

def handle_upload(event):
    upload_component.visible = False
    content = event.content.read().decode('utf-8')
    # create table from csv
    df = pd.read_csv(StringIO(content), delimiter=';', usecols=lambda column: column not in ['Unnamed: 6'])
    ui.table(columns=[{'name': col, 'label': col, 'field': col} for col in df.columns], rows=df.to_dict(orient='records')).classes('mx-auto')

with ui.card().classes("mx-auto").style('background: transparent; border: none; box-shadow: none;'):
    upload_component = ui.upload(on_upload=handle_upload).props('accept=".csv"').classes('max-w-full')

ui.run()
