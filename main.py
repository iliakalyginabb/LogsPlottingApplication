from nicegui import ui
import pandas as pd
import plotly.express as px
from io import StringIO

def handle_upload(event):
    content = event.content.read().decode('utf-8')
    df = pd.read_csv(StringIO(content), delimiter=';')
    
    def show_results():

        # navbar
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')

        # sidebar
        with ui.left_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as left_drawer:
            ui.label('Signals')

            # update plot visibility for the first plot
            def update_visibility_first_plot():
                for i, checkbox in enumerate(checkboxes_first_plot):
                    fig1.data[i].visible = checkbox.value
                plot1.update()

            # update plot visibility for the second plot
            def update_visibility_second_plot():
                for i, checkbox in enumerate(checkboxes_second_plot):
                    fig2.data[i].visible = checkbox.value
                plot2.update()

            # create checkboxes for the first plot
            checkboxes_first_plot = []
            y_columns = [col for col in df.columns if col not in ['Time', 'Unnamed: 6']]
            for col in y_columns:
                checkbox = ui.checkbox(f'{col}', value=True, on_change=update_visibility_first_plot)
                checkboxes_first_plot.append(checkbox)

            # create checkboxes for the second plot
            checkboxes_second_plot = []
            for col in y_columns:
                checkbox = ui.checkbox(f'{col}', value=True, on_change=update_visibility_second_plot)
                checkboxes_second_plot.append(checkbox)
            

            # upload csv button
            ui.button('Upload CSV').on('click', lambda: ui.run_javascript('window.location.href = "/";')).classes('mx-auto')

        # main content
        with ui.row().classes('mx-auto'):

            # layout toggle
            toggle1 = ui.toggle(["1x1", "1x2", "2x1", "2x2"], value="1x1").classes('mx-auto')

            # tabs
            with ui.tabs().classes('w-full') as tabs:
                line_chart = ui.tab('Line Chart View')
                table_view = ui.tab('Table View')

            # tab panels
            with ui.tab_panels(tabs, value=line_chart).classes('w-full'):
                with ui.tab_panel(line_chart):
                    with ui.row().classes('w-full justify-around'):
                        # create first plotly graph from csv
                        fig1 = px.line(df, x='Time', y=y_columns,
                                    labels={'value': 'Values', 'variable': 'Variables'},
                                    title='Plot 1')
                        plot1 = ui.plotly(fig1).classes('mx-auto').style('width: 42vw; height: 80vh;')

                        # create second plotly graph from csv
                        fig2 = px.line(df, x='Time', y=y_columns,
                                    labels={'value': 'Values', 'variable': 'Variables'},
                                    title='Plot 2')
                        plot2 = ui.plotly(fig2).classes('mx-auto').style('width: 42vw; height: 80vh;')

                with ui.tab_panel(table_view):
                    # create table from csv
                    df_table = df.drop(columns=['Unnamed: 6'], errors='ignore')
                    ui.table(columns=[{'name': col, 'label': col, 'field': col, 'sortable':True} for col in df_table.columns], rows=df_table.to_dict(orient='records')).classes('mx-auto')
                
                

    ui.page('/results')(show_results)
    ui.run_javascript('window.location.href = "/results";')  # load results page

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
