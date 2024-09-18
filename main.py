from nicegui import ui
import pandas as pd
import plotly.express as px
from io import StringIO

df_global = pd.DataFrame()  # dataframe to store uploaded data
df_signals = pd.DataFrame(columns=['csv_filename', 'signal_name', 'plot1', 'plot2', 'plot3', 'plot4'])  # dataframe to store signal settings
processed_filenames = set()  # set to keep track of processed filenames

# function to handle CSV upload
def handle_upload(event):
    global df_global, df_signals, processed_filenames, grid

    csv_filename = event.name  # get the filename of the uploaded CSV

    # check if the file has already been uploaded
    if csv_filename in processed_filenames:
        ui.notify(f'The file "{csv_filename}" has already been uploaded.', type='warning')
        return

    content = event.content.read().decode('utf-8')
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

    # Remove rows where 'signal_name' contains 'Time' or 'Unnamed'
    new_signals_df = new_signals_df[~new_signals_df['signal_name'].str.contains('Time|Unnamed', case=False, na=False)]

    # Update the df_signals dataframe
    df_signals = pd.concat([df_signals, new_signals_df], ignore_index=True)

    # add filename to the processed set
    processed_filenames.add(csv_filename)

    # update the aggrid columnDefs with the new total count
    column_defs = [
        {"headerName": f"CSV File name | Total files: {len(processed_filenames)}", "field": "csv_filename"},
        {"headerName": "Signal Name", "field": "signal_name"},
        {"headerName": "Plot 1", "field": "plot1", "cellEditor": "agCheckboxCellEditor", "editable": True},
        {"headerName": "Plot 2", "field": "plot2", "cellEditor": "agCheckboxCellEditor", "editable": True},
        {"headerName": "Plot 3", "field": "plot3", "cellEditor": "agCheckboxCellEditor", "editable": True},
        {"headerName": "Plot 4", "field": "plot4", "cellEditor": "agCheckboxCellEditor", "editable": True},
    ]
    # try updating the grid's columnDefs and rowData with the new data
    try:
        grid.options['columnDefs'] = column_defs
        grid.options['rowData'] = df_signals.to_dict(orient='records')
        grid.update()  # asynchronously update the grid to reflect the changes
    except:
        pass

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
def on_zoom(plot_index, event):
    relayout_data = event.args  # axes values
    triggering_checkbox = sync_checkboxes[plot_index].value  # Check if the triggering plot has sync enabled

    # Only sync if the triggering plot's checkbox is enabled
    if not triggering_checkbox:
        return  # Ignore zoom events for plots without sync enabled

    if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
        x_start = relayout_data['xaxis.range[0]']
        x_end = relayout_data['xaxis.range[1]']

        # Synchronize only those plots where the sync checkbox is checked
        for i, checkbox in enumerate(sync_checkboxes):
            if checkbox.value and i != plot_index:  # Sync only the checked plots, excluding the triggering one
                figs[i].update_xaxes(range=[x_start, x_end])
                plots[i].update()
    elif 'xaxis.autorange' in relayout_data:
        # Reset the x-axis range for synced plots
        for i, checkbox in enumerate(sync_checkboxes):
            if checkbox.value and i != plot_index:  # Sync only the checked plots, excluding the triggering one
                figs[i].update_xaxes(range=None)
                plots[i].update()
       
# function to set all values in a column to true or false
async def set_entire_plot_column(column_name, value):
    global df_signals, grid
    # set all values in the specified column to the given value
    df_signals[column_name] = value

    # rerender the grid with updated data
    grid.options['rowData'] = df_signals.to_dict(orient='records')
    grid.update()  # asynchronously update the grid to reflect the changes
    update_visibility()  # update plot visibility based on new settings

async def handle_plot_checkbox_change(plot, e):
    await set_entire_plot_column(plot, e.value)


# load the main content
def show_results():
    global df_global, plot1, plot2, plot3, plot4, sync_checkboxes, figs, plots, grid, data

    y_columns = [col for col in df_global.columns if 'Unnamed' not in col and col != 'Time']

    with ui.dialog() as upload_dialog, ui.card():
        with ui.card().classes("mx-auto").style('background: transparent; border: none; box-shadow: none;'):
            ui.upload(on_upload=handle_upload).props('accept=".csv"').classes('max-w-full')
            ui.button('Close', on_click=upload_dialog.close)

    # navbar
    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.button('Upload CSV', icon='file_present').on('click', upload_dialog.open)

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

                    # create plots
                    fig1 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 1'))
                    plot1 = ui.plotly(fig1).on('plotly_relayout', lambda event: on_zoom(0, event)).classes('mx-auto').style('display: none;')

                    fig2 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 2'))
                    plot2 = ui.plotly(fig2).on('plotly_relayout', lambda event: on_zoom(1, event)).classes('mx-auto').style('display: none;')

                    fig3 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 3'))
                    plot3 = ui.plotly(fig3).on('plotly_relayout', lambda event: on_zoom(2, event)).classes('mx-auto').style('display: none;')

                    fig4 = remove_margins_from_plots(px.line(df_global, x='Time', y=y_columns, title='Plot 4'))
                    plot4 = ui.plotly(fig4).on('plotly_relayout', lambda event: on_zoom(3, event)).classes('mx-auto').style('display: none;')   

                    figs = [fig1, fig2, fig3, fig4]
                    plots = [plot1, plot2, plot3, plot4]

                    # Update plot visibility based on settings 
                    update_visibility()

            # ui.aggrid table with the uploaded data
            with ui.tab_panel(signals_table):
                # data from df_signals
                data = df_signals.to_dict(orient='records')

                # create checkboxes for sync
                sync_checkboxes = []
                with ui.row().classes('mx-auto'):
                    for i in range(4):
                        checkbox = ui.checkbox(f'Sync Plot {i+1}', value=False)
                        sync_checkboxes.append(checkbox)

                # add checkboxes to set plot column values
                with ui.row().classes('mx-auto'):
                    ui.checkbox('Set all Plot 1', value=True).on_value_change(lambda e: handle_plot_checkbox_change('plot1', e))
                    ui.checkbox('Set all Plot 2', value=True).on_value_change(lambda e: handle_plot_checkbox_change('plot2', e))
                    ui.checkbox('Set all Plot 3', value=True).on_value_change(lambda e: handle_plot_checkbox_change('plot3', e))
                    ui.checkbox('Set all Plot 4', value=True).on_value_change(lambda e: handle_plot_checkbox_change('plot4', e))

                # aggrid structure
                column_defs = [
                    {"headerName": f"CSV File name | Total files: {len(processed_filenames)}", "field": "csv_filename"},
                    {"headerName": "Signal Name", "field": "signal_name"},
                    {"headerName": "Plot 1", "field": "plot1", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 2", "field": "plot2", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 3", "field": "plot3", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 4", "field": "plot4", "cellEditor": "agCheckboxCellEditor", "editable": True},
                ]
                
                # create aggrid grid
                grid = ui.aggrid({
                    'defaultColDef': {'flex': 1},
                    'columnDefs': column_defs,
                    'rowData': data,
                    'rowSelection': 'multiple',
                }).style('width: 85vw; height: 77vh;').classes('mx-auto')

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

                    update_visibility() # update plot visibility based on new settings

                # event listener for ui.aggrid (checkboxes) value changes
                grid.on('cellValueChanged', on_grid_value_change)

    update_layout()

# create main (upload) page
@ui.page('/')
def main_page():
    ui.markdown('### Upload CSV file').classes('mx-auto')
    with ui.card().classes("mx-auto").style('background: transparent; border: none; box-shadow: none;'):
        ui.upload(on_upload=handle_upload).props('accept=".csv"').classes('max-w-full')

# create results route
@ui.page('/results')
def results_page():
    show_results()

ui.run()