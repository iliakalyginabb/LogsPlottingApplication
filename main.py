from nicegui import ui
import pandas as pd
import plotly.express as px
from io import StringIO

# initialize global dataframe to store uploaded data
df_global = pd.DataFrame()

def handle_upload(event):
    global df_global
    content = event.content.read().decode('utf-8')
    new_df = pd.read_csv(StringIO(content), delimiter=';')

    # merge new data with existing global dataframe
    df_global = pd.concat([df_global, new_df], ignore_index=True)

    # redirect to results page
    ui.run_javascript('window.location.href = "/results";')

def show_results():
    global df_global

    # define y columns (excluding 'Time' and all 'Unnamed')
    y_columns = [col for col in df_global.columns if 'Unnamed' not in col and col != 'Time']

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

        # update plot visibility for the second plot
        def update_visibility_third_plot():
            for i, checkbox in enumerate(checkboxes_second_plot):
                fig3.data[i].visible = checkbox.value
            plot3.update()
        
        # update plot visibility for the second plot
        def update_visibility_fourth_plot():
            for i, checkbox in enumerate(checkboxes_second_plot):
                fig4.data[i].visible = checkbox.value
            plot4.update()

        # create Plot 1 signals dialog
        def open_plot1_settings():
            global checkboxes_first_plot
            checkboxes_first_plot = []
            with ui.dialog() as plot1_signals_dialog:
                with ui.card():
                    ui.label("Plot 1 signals")
                    for col in y_columns:
                        checkbox = ui.checkbox(f'{col}', value=True, on_change=update_visibility_first_plot)
                        checkboxes_first_plot.append(checkbox)
                    ui.button('Close', on_click=plot1_signals_dialog.close)
            plot1_signals_dialog.open()

        # create Plot 2 signals dialog
        def open_plot2_settings():
            global checkboxes_second_plot
            checkboxes_second_plot = []
            with ui.dialog() as plot2_signals_dialog:
                with ui.card():
                    ui.label("Plot 2 signals")
                    for col in y_columns:
                        checkbox = ui.checkbox(f'{col}', value=True, on_change=update_visibility_second_plot)
                        checkboxes_second_plot.append(checkbox)
                    ui.button('Close', on_click=plot2_signals_dialog.close)
            plot2_signals_dialog.open()
        
        # create Plot 3 settings dialog
        def open_plot3_settings():
            global checkboxes_second_plot
            checkboxes_second_plot = []
            with ui.dialog() as plot3_signals_dialog:
                with ui.card():
                    ui.label("Plot 3 signals")
                    for col in y_columns:
                        checkbox = ui.checkbox(f'{col}', value=True, on_change=update_visibility_third_plot)
                        checkboxes_second_plot.append(checkbox)
                    ui.button('Close', on_click=plot3_signals_dialog.close)
            plot3_signals_dialog.open()
        
        # create Plot 2 settings dialog
        def open_plot4_settings():
            global checkboxes_second_plot
            checkboxes_second_plot = []
            with ui.dialog() as plot4_signals_dialog:
                with ui.card():
                    ui.label("Plot 4 signals")
                    for col in y_columns:
                        checkbox = ui.checkbox(f'{col}', value=True, on_change=update_visibility_fourth_plot)
                        checkboxes_second_plot.append(checkbox)
                    ui.button('Close', on_click=plot4_signals_dialog.close)
            plot4_signals_dialog.open()

        # Add buttons to open dialogs for plot settings
        ui.button('Plot 1 settings', on_click=open_plot1_settings).classes('w-full')
        ui.button('Plot 2 settings', on_click=open_plot2_settings).classes('w-full')
        ui.button('Plot 3 settings', on_click=open_plot3_settings).classes('w-full')
        ui.button('Plot 4 settings', on_click=open_plot4_settings).classes('w-full')

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
                    
                    # function to update the layout dynamically
                    def update_layout():
                        layout = toggle1.value
                        if layout == "1x1":
                            plot1.style('display: block; width: 85vw; height: 80vh;').classes('mx-auto')
                            plot2.style('display: none;')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                        elif layout == "1x2":
                            plot1.style('display: block; width: 40vw; height: 80vh;').classes('mx-auto')
                            plot2.style('display: block; width: 40vw; height: 80vh;').classes('mx-auto')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                        elif layout == "2x1":
                            plot1.style('display: block; width: 85vw; height: 40vh;').classes('mx-auto')
                            plot2.style('display: block; width: 85vw; height: 40vh;').classes('mx-auto')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                        elif layout == "2x2":
                            plot1.style('display: block; width: 42vw; height: 40vh;').classes('mx-auto')
                            plot2.style('display: block; width: 42vw; height: 40vh;').classes('mx-auto')
                            plot3.style('display: block; width: 42vw; height: 40vh;').classes('mx-auto')
                            plot4.style('display: block; width: 42vw; height: 40vh;').classes('mx-auto')

                        # trigger resize for plots after layout update
                        ui.run_javascript(f'Plotly.relayout("{plot1.id}", {{}});')
                        ui.run_javascript(f'Plotly.relayout("{plot2.id}", {{}});')
                        ui.run_javascript(f'Plotly.relayout("{plot3.id}", {{}});')
                        ui.run_javascript(f'Plotly.relayout("{plot4.id}", {{}});')
                        ui.run_javascript('window.dispatchEvent(new Event("resize"));')


                    # attach the toggle change event to the layout update function
                    toggle1.on_value_change(update_layout)

                    # create plotly graphs from global dataframe
                    fig1 = px.line(df_global, x='Time', y=y_columns,
                                   labels={'value': 'Values', 'variable': 'Variables'},
                                   title='Plot 1')
                    plot1 = ui.plotly(fig1).classes('mx-auto').style('display: none;')

                    fig2 = px.line(df_global, x='Time', y=y_columns,
                                   labels={'value': 'Values', 'variable': 'Variables'},
                                   title='Plot 2')
                    plot2 = ui.plotly(fig2).classes('mx-auto').style('display: none;')

                    fig3 = px.line(df_global, x='Time', y=y_columns,
                                   labels={'value': 'Values', 'variable': 'Variables'},
                                   title='Plot 3')
                    plot3 = ui.plotly(fig3).classes('mx-auto').style('display: none;')

                    fig4 = px.line(df_global, x='Time', y=y_columns,
                                   labels={'value': 'Values', 'variable': 'Variables'},
                                   title='Plot 4')
                    plot4 = ui.plotly(fig4).classes('mx-auto').style('display: none;')

                    # initialize layout on load
                    update_layout()

            # create table from global dataframe
            with ui.tab_panel(table_view):
                df_table = df_global.drop(columns=['Unnamed: 6'], errors='ignore')
                ui.table(columns=[{'name': col, 'label': col, 'field': col, 'sortable':True} for col in df_table.columns], rows=df_table.to_dict(orient='records')).classes('mx-auto')

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
    show_results()

ui.run()
