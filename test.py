from nicegui import ui
import pandas as pd
import plotly.express as px
from io import StringIO

# Global DataFrame to store merged data
merged_df = pd.DataFrame()

def handle_upload(event):
    global merged_df
    content = event.content.read().decode('utf-8')
    df = pd.read_csv(StringIO(content), delimiter=';')
    
    # Merge new data with the global DataFrame
    if merged_df.empty:
        merged_df = df
    else:
        merged_df = pd.merge(merged_df, df, on='Time', how='outer')
        
    ui.page('/results')(show_results)
    ui.run_javascript('window.location.href = "/results";')

def show_results():
    with ui.row().classes('mx-auto'):
        ui.button('Back').on('click', lambda: ui.open('/')).classes('mx-auto')

        with ui.tabs().classes('w-full') as tabs:
            table_view = ui.tab('Table View')
            line_chart = ui.tab('Line Chart View')
    
        with ui.tab_panels(tabs, value=table_view).classes('w-full'):
            with ui.tab_panel(table_view):
                # create table from merged data
                df_table = merged_df.drop(columns=['Unnamed: 6'], errors='ignore')
                ui.table(columns=[{'name': col, 'label': col, 'field': col, 'sortable':True} for col in df_table.columns], rows=df_table.to_dict(orient='records')).classes('mx-auto')
            
            with ui.tab_panel(line_chart):
                # create plotly graph from merged data
                y_columns = [col for col in merged_df.columns if col not in ['Time', 'Unnamed: 6']]
                fig = px.line(merged_df, x='Time', y=y_columns,
                            labels={'value': 'Values', 'variable': 'Variables'},
                            title='')
                plot = ui.plotly(fig).classes('mx-auto').style('width: 85vw; height: 80vh;')

                # update plot visibility
                def update_visibility():
                    for i, checkbox in enumerate(checkboxes):
                        fig.data[i].visible = checkbox.value
                    plot.update()

                # create checkboxes
                checkboxes = []
                with ui.row().classes('mx-auto'):
                    for col in y_columns:
                        checkbox = ui.checkbox(f'Show {col}', value=True, on_change=update_visibility)
                        checkboxes.append(checkbox)

                # Sidebar for signal selection
                with ui.sidebar().classes('w-1/4'):
                    ui.markdown('## Select Signals')
                    for col in y_columns:
                        ui.checkbox(f'Show {col}', value=True, on_change=update_visibility)

                # Layout selection
                with ui.row().classes('mx-auto'):
                    ui.markdown('## Select Layout')
                    layout_options = ['1x1', '1x2', '2x1', '2x2']
                    layout_select = ui.select(layout_options, value='1x1').classes('mx-auto')

                # Update layout based on selection
                def update_layout():
                    layout = layout_select.value
                    # Update plot layout logic here

                layout_select.on('change', update_layout)

ui.page('/results')(show_results)

# create main (upload) page
@ui.page('/')
def main_page():
    global upload_component
    ui.markdown('## Upload CSV file').classes('mx-auto')
    with ui.card().classes("mx-auto").style('background: transparent; border: none; box-shadow: none;'):
        upload_component = ui.upload(on_upload=handle_upload).props('accept=".csv"').classes('max-w-full')

# create results route
@ui.page('/results')
def results_page():
    pass

ui.run()
