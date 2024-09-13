from nicegui import ui
import pandas as pd
import plotly.express as px
from io import StringIO

df_global = pd.DataFrame()  # dataframe to store uploaded data
df_signals = pd.DataFrame(columns=['csv_filename', 'signal_name', 'plot1', 'plot2', 'plot3', 'plot4'])  # dataframe to store signal settings

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
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig

# function to update trace visibility per plot based on the data from df_signals
def update_visibility():
    global df_signals

    # dictionary to map plot ids to plots
    plots = {'plot1': plot1, 'plot2': plot2, 'plot3': plot3, 'plot4': plot4}

    for _, row in df_signals.iterrows():  # unpack the tuple into index and row
        signal_name = row['signal_name']
        visible_plots = {
            'plot1': row['plot1'],
            'plot2': row['plot2'],
            'plot3': row['plot3'],
            'plot4': row['plot4']
        }

        for plot_id, is_visible in visible_plots.items():
            if plot_id in plots:
                # Update the visibility of traces in the plot
                fig = plots[plot_id].figure
                if is_visible:
                    fig.update_traces(selector=dict(name=signal_name), visible=True)
                else:
                    fig.update_traces(selector=dict(name=signal_name), visible=False)

                plots[plot_id].update()

# function to handle zoom events and synchronize x-axis
def on_zoom(event):
    relayout_data = event.args # axes values
    if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
        x_start = relayout_data['xaxis.range[0]']
        x_end = relayout_data['xaxis.range[1]']
        for i, checkbox in enumerate(checkboxes):
            if checkbox.value != False:
                figs[i].update_xaxes(range=[x_start, x_end])
                plots[i].update()
    elif 'xaxis.autorange' in relayout_data:
        for i, checkbox in enumerate(checkboxes):
            if checkbox.value != False:
                figs[i].update_xaxes(range=None)
                plots[i].update()

def show_results():
    global df_global, plot1, plot2, plot3, plot4, checkboxes, figs, plots

    y_columns = [col for col in df_global.columns if 'Unnamed' not in col and col != 'Time']

    # navbar
    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.button('Upload CSV', icon='file_present').on('click', lambda: ui.run_javascript('window.location.href = "/";'))

    # main content
    with ui.row().classes('mx-auto'):
        # initialize tab panels
        with ui.tabs().classes('w-full') as tabs:
            line_chart = ui.tab('Line Chart View')
            signals_table = ui.tab('Signals Table')

        # create tab panels
        with ui.tab_panels(tabs, value=line_chart).classes('w-full'):
            with ui.tab_panel(line_chart):
                # toggle to select layout
                toggle1 = ui.toggle(["1x1", "1x2", "2x1", "2x2"], value="1x1").classes('mx-auto')

                with ui.row().classes('w-full justify-around'):
                    def update_layout():
                        layout = toggle1.value
                        if layout == "1x1":
                            plot1.style('display: block; width: 95vw; height: 80vh;').classes('mx-auto')
                            plot2.style('display: none;')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                        elif layout == "1x2":
                            plot1.style('display: block; width: 45vw; height: 80vh;').classes('mx-auto')
                            plot2.style('display: block; width: 45vw; height: 80vh;').classes('mx-auto')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                        elif layout == "2x1":
                            plot1.style('display: block; width: 95vw; height: 40vh;').classes('mx-auto')
                            plot2.style('display: block; width: 95vw; height: 40vh;').classes('mx-auto')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                        elif layout == "2x2":
                            plot1.style('display: block; width: 45vw; height: 40vh;').classes('mx-auto')
                            plot2.style('display: block; width: 45vw; height: 40vh;').classes('mx-auto')
                            plot3.style('display: block; width: 45vw; height: 40vh;').classes('mx-auto')
                            plot4.style('display: block; width: 45vw; height: 40vh;').classes('mx-auto')

                        ui.run_javascript('window.dispatchEvent(new Event("resize"));')

                    toggle1.on_value_change(update_layout)

                    fig1 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 1'))
                    plot1 = ui.plotly(fig1).on('plotly_relayout', on_zoom).classes('mx-auto').style('display: none;')

                    fig2 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 2'))
                    plot2 = ui.plotly(fig2).on('plotly_relayout', on_zoom).classes('mx-auto').style('display: none;')

                    fig3 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 3'))
                    plot3 = ui.plotly(fig3).on('plotly_relayout', on_zoom).classes('mx-auto').style('display: none;')

                    fig4 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 4'))
                    plot4 = ui.plotly(fig4).on('plotly_relayout', on_zoom).classes('mx-auto').style('display: none;')

                    figs = [fig1, fig2, fig3, fig4]
                    plots = [plot1, plot2, plot3, plot4]

                    # Update plot visibility based on settings  
                    update_visibility()

            # ui.aggrid table with the uploaded data
            with ui.tab_panel(signals_table):
                # data from df_signals
                data = df_signals.to_dict(orient='records')

                # create checkboxes for sync
                checkboxes = []
                with ui.row().classes('mx-auto'):
                    for i in range(4):
                        checkbox = ui.checkbox(f'Sync Plot {i+1}', value=False)
                        checkboxes.append(checkbox)

                # aggrid structure
                column_defs = [
                    {"headerName": "CSV File name", "field": "csv_filename"},
                    {"headerName": "Signal Name", "field": "signal_name"},
                    {"headerName": "Plot 1", "field": "plot1", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 2", "field": "plot2", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 3", "field": "plot3", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 4", "field": "plot4", "cellEditor": "agCheckboxCellEditor", "editable": True},
                ]
                
                # create aggrid
                grid = ui.aggrid({
                    'defaultColDef': {'flex': 1},
                    'columnDefs': column_defs,
                    'rowData': data,
                    'rowSelection': 'multiple',
                }).style('width: 85vw; height: 80vh;').classes('mx-auto')

                # event handler for grid value change
                def on_grid_value_change(event):
                    global df_signals

                    # extract data from the event
                    data = event.args['data']
                    
                    # Find the row in df_signals to update
                    csv_filename = data['csv_filename']
                    signal_name = data['signal_name']
                    
                    # Update the relevant row in df_signals
                    mask = (df_signals['csv_filename'] == csv_filename) & (df_signals['signal_name'] == signal_name)
                    if not df_signals[mask].empty:
                        df_signals.loc[mask, 'plot1'] = data['plot1']
                        df_signals.loc[mask, 'plot2'] = data['plot2']
                        df_signals.loc[mask, 'plot3'] = data['plot3']
                        df_signals.loc[mask, 'plot4'] = data['plot4']

                    # Update plot visibility based on new settings
                    update_visibility()

                    # Print updated df_signals to verify changes
                    print(df_signals)

                # event listener for ui.aggrid (checkboxes) value changes
                grid.on('cellValueChanged', on_grid_value_change)

    update_layout()

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