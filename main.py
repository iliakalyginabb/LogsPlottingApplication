from nicegui import ui
import pandas as pd
import plotly.express as px
from io import StringIO

def handle_upload(event):
    content = event.content.read().decode('utf-8')
    df = pd.read_csv(StringIO(content), delimiter=';')
    
    def show_results():
        with ui.tabs().classes('w-full') as tabs:
            table_view = ui.tab('Table View')
            line_chart = ui.tab('Line Chart View')
        
        with ui.tab_panels(tabs, value=line_chart).classes('w-full'):
            with ui.tab_panel(table_view):
                # create table from csv
                df_table = df.drop(columns=['Unnamed: 6'], errors='ignore')
                ui.table(columns=[{'name': col, 'label': col, 'field': col} for col in df_table.columns], rows=df_table.to_dict(orient='records')).classes('mx-auto')
            
            with ui.tab_panel(line_chart):
                # create plotly graph from csv
                y_columns = [col for col in df.columns if col not in ['Time', 'Unnamed: 6']]
                fig = px.line(df, x='Time', y=y_columns,
                              labels={'value': 'Values', 'variable': 'Variables'},
                              title='Time Series Data')
                ui.plotly(fig).classes('mx-auto').style('width: 85vw; height: 80vh;')
    
    ui.page('/results')(show_results)
    ui.run_javascript('window.location.href = "/results";')  # Navigate to the results page after upload is complete

@ui.page('/')
def main_page():
    global upload_component
    with ui.card().classes("mx-auto").style('background: transparent; border: none; box-shadow: none;'):
        upload_component = ui.upload(on_upload=handle_upload).props('accept=".csv"').classes('max-w-full')

@ui.page('/results')
def results_page():
    pass  # The content of this page will be generated dynamically in handle_upload

ui.run()
