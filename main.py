from nicegui import ui
import pandas as pd
import plotly.express as px
from io import StringIO

df_global = pd.DataFrame()  # dataframe to store uploaded data
plot_settings = {}  # stores plot visibility settings for each plot
df_signals = pd.DataFrame(columns=['csv_filename', 'signal_name', 'plot1', 'plot2', 'plot3', 'plot4', 'sync_x_axis'])  # dataframe to store signal settings

# function to handle CSV upload
def handle_upload(event):
    global df_global, df_signals
    content = event.content.read().decode('utf-8')
    csv_filename = event.name  # get the filename of the uploaded CSV
    new_df = pd.read_csv(StringIO(content), delimiter=';')

    # merge new data with existing global dataframe
    df_global = pd.concat([df_global, new_df], ignore_index=True)

    # Create a new dataframe with signal names, filename, and default settings
    new_signals_df = pd.DataFrame({
        'csv_filename': [csv_filename] * len(new_df.columns),  # repeat the filename for all columns
        'signal_name': new_df.columns,  # the column names as signal names
        'plot1': True,
        'plot2': True,
        'plot3': True,
        'plot4': True,
        'sync_x_axis': False
    })

    # Update the df_signals dataframe
    df_signals = pd.concat([df_signals, new_signals_df], ignore_index=True)

    # Remove rows where 'signal_name' contains 'Time' or 'Unnamed'
    df_signals = df_signals[~df_signals['signal_name'].str.contains('Time|Unnamed', case=False, na=False)]

    # redirect to results page
    ui.run_javascript('window.location.href = "/results";')

# function to remove margins from plots
def remove_margins_from_plots(fig):
    # Update layout to remove margins and padding around the plot
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),  # No margins
        paper_bgcolor='rgba(0,0,0,0)',    # Transparent background
        plot_bgcolor='rgba(0,0,0,0)'      # Transparent plot area
    )
    return fig

# function to update plot visibility
def update_visibility(checkboxes, fig, plot, plot_id):
    global plot_settings
    settings = [checkbox.value for checkbox in checkboxes]

    # save settings for the specific plot
    plot_settings[plot_id] = settings

    for i, checkbox in enumerate(checkboxes):
        fig.data[i].visible = checkbox.value
    plot.update()

# function to create settings dialog for each plot
def open_plot_settings(y_columns, fig, plot, title, plot_id):
    global plot_settings
    checkboxes = []

    # Retrieve saved settings, default to True for new columns without overriding existing ones
    saved_settings = plot_settings.get(plot_id, [True] * len(y_columns))

    # Adjust saved_settings if the number of columns has changed
    if len(saved_settings) < len(y_columns):
        saved_settings.extend([True] * (len(y_columns) - len(saved_settings)))
    elif len(saved_settings) > len(y_columns):
        saved_settings = saved_settings[:len(y_columns)]

    plot_settings[plot_id] = saved_settings

    # dialog with checkboxes and buttons
    with ui.dialog() as signals_dialog:
        with ui.card().style('max-width: 80vh; max-height: 60vh; display: flex; flex-direction: column;'):
            ui.label(f"{title} signals")
            with ui.element('div').style('flex: 1; overflow-y: auto;'):
                with ui.column():
                    for i, col in enumerate(y_columns):
                        checkbox = ui.checkbox(
                            f'{col}', 
                            value=saved_settings[i],  # use saved value if available
                            on_change=lambda: update_visibility(checkboxes, fig, plot, plot_id)
                        )
                        checkboxes.append(checkbox)

            with ui.row().style('flex-shrink: 0;'):
                ui.button('Hide All', on_click=lambda: set_all_checkboxes(checkboxes, fig, plot, plot_id, False))
                ui.button('Show All', on_click=lambda: set_all_checkboxes(checkboxes, fig, plot, plot_id, True))
    
    signals_dialog.open()

# function to set all checkboxes to the same value
def set_all_checkboxes(checkboxes, fig, plot, plot_id, value):
    global plot_settings
    for checkbox in checkboxes:
        checkbox.value = value

    plot_settings[plot_id] = [value] * len(checkboxes)
    update_visibility(checkboxes, fig, plot, plot_id)

# show results function
def show_results():
    global df_global

    y_columns = [col for col in df_global.columns if 'Unnamed' not in col and col != 'Time']

    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')

    with ui.left_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as left_drawer:
        ui.label('Signals')

        def open_plot1_settings():
            open_plot_settings(y_columns, fig1, plot1, 'Plot 1', 'plot1')

        def open_plot2_settings():
            open_plot_settings(y_columns, fig2, plot2, 'Plot 2', 'plot2')

        def open_plot3_settings():
            open_plot_settings(y_columns, fig3, plot3, 'Plot 3', 'plot3')

        def open_plot4_settings():
            open_plot_settings(y_columns, fig4, plot4, 'Plot 4', 'plot4')

        button_plot1 = ui.button('Plot 1 settings', on_click=open_plot1_settings).classes('w-full')
        button_plot2 = ui.button('Plot 2 settings', on_click=open_plot2_settings).classes('w-full')
        button_plot3 = ui.button('Plot 3 settings', on_click=open_plot3_settings).classes('w-full')
        button_plot4 = ui.button('Plot 4 settings', on_click=open_plot4_settings).classes('w-full')

        ui.button('Upload CSV').on('click', lambda: ui.run_javascript('window.location.href = "/";')).classes('mx-auto')

    with ui.row().classes('mx-auto'):

        toggle1 = ui.toggle(["1x1", "1x2", "2x1", "2x2"], value="1x1").classes('mx-auto')

        with ui.tabs().classes('w-full') as tabs:
            line_chart = ui.tab('Line Chart View')
            signals_table = ui.tab('Signals Table')

        with ui.tab_panels(tabs, value=line_chart).classes('w-full'):
            with ui.tab_panel(line_chart):
                with ui.row().classes('w-full justify-around'):
                    def update_layout():
                        layout = toggle1.value
                        if layout == "1x1":
                            plot1.style('display: block; width: 85vw; height: 80vh;').classes('mx-auto')
                            plot2.style('display: none;')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                            button_plot1.style('display: block;')
                            button_plot2.style('display: none;')
                            button_plot3.style('display: none;')
                            button_plot4.style('display: none;')
                        elif layout == "1x2":
                            plot1.style('display: block; width: 40vw; height: 80vh;').classes('mx-auto')
                            plot2.style('display: block; width: 40vw; height: 80vh;').classes('mx-auto')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                            button_plot1.style('display: block;')
                            button_plot2.style('display: block;')
                            button_plot3.style('display: none;')
                            button_plot4.style('display: none;')
                        elif layout == "2x1":
                            plot1.style('display: block; width: 85vw; height: 40vh;').classes('mx-auto')
                            plot2.style('display: block; width: 85vw; height: 40vh;').classes('mx-auto')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                            button_plot1.style('display: block;')
                            button_plot2.style('display: block;')
                            button_plot3.style('display: none;')
                            button_plot4.style('display: none;')
                        elif layout == "2x2":
                            plot1.style('display: block; width: 42vw; height: 40vh;').classes('mx-auto')
                            plot2.style('display: block; width: 42vw; height: 40vh;').classes('mx-auto')
                            plot3.style('display: block; width: 42vw; height: 40vh;').classes('mx-auto')
                            plot4.style('display: block; width: 42vw; height: 40vh;').classes('mx-auto')
                            button_plot1.style('display: block;')
                            button_plot2.style('display: block;')
                            button_plot3.style('display: block;')
                            button_plot4.style('display: block;')

                        ui.run_javascript(f'Plotly.relayout("{plot1.id}", {{}});')
                        ui.run_javascript(f'Plotly.relayout("{plot2.id}", {{}});')
                        ui.run_javascript(f'Plotly.relayout("{plot3.id}", {{}});')
                        ui.run_javascript(f'Plotly.relayout("{plot4.id}", {{}});')
                        ui.run_javascript('window.dispatchEvent(new Event("resize"));')

                    toggle1.on_value_change(update_layout)

                    fig1 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 1'))
                    plot1 = ui.plotly(fig1).classes('mx-auto').style('display: none;')

                    fig2 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 2'))
                    plot2 = ui.plotly(fig2).classes('mx-auto').style('display: none;')

                    fig3 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 3'))
                    plot3 = ui.plotly(fig3).classes('mx-auto').style('display: none;')

                    fig4 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 4'))
                    plot4 = ui.plotly(fig4).classes('mx-auto').style('display: none;')

                    update_layout()

            # ui.aggrid table with the uploaded data
            with ui.tab_panel(signals_table):

                # data from df_signals
                data = df_signals.to_dict(orient='records')

                # aggrid structure
                column_defs = [
                    {"headerName": "CSV File name", "field": "csv_filename"},
                    {"headerName": "Signal Name", "field": "signal_name"},
                    {"headerName": "Plot 1", "field": "plot1", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 2", "field": "plot2", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 3", "field": "plot3", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 4", "field": "plot4", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Sync X-axis", "field": "sync_x_axis", "cellEditor": "agCheckboxCellEditor", "editable": True}]
                
                # create aggrid
                grid = ui.aggrid({
                    'defaultColDef': {'flex': 1},
                    'columnDefs': column_defs,
                    'rowData': data,
                    'rowSelection': 'multiple',
                }).style('width: 85vw; height: 80vh;').classes('mx-auto')


# create main (upload) page
@ui.page('/')
def main_page():
    ui.markdown('## Upload CSV file').classes('mx-auto')
    with ui.card().classes("mx-auto").style('background: transparent; border: none; box-shadow: none;'):
        ui.upload(on_upload=handle_upload).props('accept=".csv"').classes('max-w-full')

# create results route
@ui.page('/results')
def results_page():
    show_results()

ui.run()