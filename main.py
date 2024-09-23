from nicegui import app, ui
import pandas as pd
import plotly.express as px
from io import StringIO

# set native app settings
app.native.window_args['resizable'] = True
app.native.start_args['debug'] = False # open with debug window
app.native.settings['ALLOW_DOWNLOADS'] = True

df_global = pd.DataFrame()  # dataframe to store uploaded data
df_signals = pd.DataFrame(columns=['csv_filename', 'signal_name', 'plot1', 'plot2', 'plot3', 'plot4'])  # dataframe to store signal settings
processed_filenames = set()  # set to keep track of processed filenames

left_drawer_state =  True # left drawer state on app start

# function to handle CSV upload
def handle_upload(event):
    global df_global, df_signals, processed_filenames, grid

    csv_filename = event.name  # get the filename of the uploaded CSV
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
        'plot4': True, # die linie macht de plot 4 uf true, wenn de csv file hochglade wird
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

# function to customize the plot
def customize_plot(fig, line_width=1):
    # Update layout to remove margins and padding around the plot
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0)
    )
    # Update traces to set the line thickness
    fig.update_traces(line=dict(width=line_width))
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
    if column_name == 'all':
        for plot in ['plot1', 'plot2', 'plot3', 'plot4']:
            df_signals[plot] = value
    else:
        # set all values in the specified column to the given value
        df_signals[column_name] = value

    # rerender the grid with updated data
    grid.options['rowData'] = df_signals.to_dict(orient='records')
    grid.update()  # asynchronously update the grid to reflect the changes
    update_visibility()  # update plot visibility based on new settings

# function to handle plot checkbox changes
async def handle_plot_checkbox_change(plot, e):
    await set_entire_plot_column(plot, e.value)

# set select rows to false in a specified plot
async def set_selected_rows_value(plot, value):
    global df_signals, grid
    # Get the selected rows from the grid
    rows = await grid.get_selected_rows()
    if rows:
        for row in rows:
            csv_filename = row['csv_filename']
            signal_name = row['signal_name']
            mask = (df_signals['csv_filename'] == csv_filename) & (df_signals['signal_name'] == signal_name)

            if plot in ['plot1', 'plot2', 'plot3', 'plot4']:
                # update corresponding value in df_signals to provided value (true or false)
                df_signals.loc[mask, plot] = value
            elif plot == 'all':
                # update the corresponding row in df_signals
                if not df_signals[mask].empty:
                    df_signals.loc[mask, ['plot1', 'plot2', 'plot3', 'plot4']] = value
    else:
        ui.notify("No rows selected", type='warning')

    # Rerender the grid with the updated data
    grid.options['rowData'] = df_signals.to_dict(orient='records')
    grid.update()

    # Update plot visibility based on new settings
    update_visibility()

async def get_selected_rows():
    rows = await grid.get_selected_rows()
    print(rows)

# load the main content
def show_results():
    global df_global, plot1, plot2, plot3, plot4, sync_checkboxes, figs, plots, grid, data, line_width_slider

    y_columns = [col for col in df_global.columns if 'Unnamed' not in col and col != 'Time']

    with ui.dialog() as upload_dialog, ui.card():
        with ui.card().classes("mx-auto").style('background: transparent; border: none; box-shadow: none;'):
            ui.upload(on_upload=handle_upload).props('accept=".csv"').classes('max-w-full')
            ui.button('Close', on_click=upload_dialog.close)

    # navbar
    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')

    # settings sidebar
    with ui.left_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as left_drawer:

        ui.label('Settings').style('font-size: 22px; font-weight: bold;')
        ui.separator()

        # button to upload CSV
        ui.label('Upload CSV').style('font-size: 16px; font-weight: bold;')
        ui.button('Upload CSV', icon='file_present').on('click', upload_dialog.open).classes('mx-auto')

        ui.separator()

        # toggle to select layout
        ui.label('Layout').style('font-size: 16px; font-weight: bold;')
        toggle1 = ui.toggle(["1x1", "1x2", "2x1", "2x2"], value="1x1").classes('mx-auto')

        ui.label('Sync Settings').style('font-size: 16px; font-weight: bold;')
        # create checkboxes for sync settings
        sync_checkboxes = []
        with ui.column():
            for i in range(4):
                checkbox = ui.checkbox(f'Sync Plot {i+1}', value=False).style('height: 10px;')
                sync_checkboxes.append(checkbox)

        ui.separator()

        # buttons for selection
        with ui.column():
            ui.label('Selection Actions').style('font-size: 18px; font-weight: bold;')
            ui.label('All Plots').style('font-size: 14px; font-weight: bold;')
            with ui.column():
                with ui.button_group():
                    ui.button("Select Row", on_click=lambda: set_selected_rows_value('all', True))
                    ui.button("Deselect Row", on_click=lambda: set_selected_rows_value('all', False))
                with ui.button_group():
                    ui.button("Select All", on_click=lambda: set_entire_plot_column('all', True))
                    ui.button("Deselect All", on_click=lambda: set_entire_plot_column('all', False))

            ui.label('Plot 1').style('font-size: 14px; font-weight: bold;')
            with ui.column():
                with ui.button_group():
                    ui.button("Select", on_click=lambda: set_selected_rows_value('plot1', True))
                    ui.button("Deselect", on_click=lambda: set_selected_rows_value('plot1', False))
                with ui.button_group():
                    ui.button("Select All", on_click=lambda: set_entire_plot_column('plot1', True))
                    ui.button("Deselect All", on_click=lambda: set_entire_plot_column('plot1', False))
            
            ui.label('Plot 2').style('font-size: 14px; font-weight: bold;')
            with ui.column():
                with ui.button_group():
                    ui.button("Select", on_click=lambda: set_selected_rows_value('plot2', True))
                    ui.button("Deselect", on_click=lambda: set_selected_rows_value('plot2', False))
                with ui.button_group():
                    ui.button("Select All", on_click=lambda: set_entire_plot_column('plot2', True))
                    ui.button("Deselect All", on_click=lambda: set_entire_plot_column('plot2', False))
            
            ui.label('Plot 3').style('font-size: 14px; font-weight: bold;')
            with ui.column():
                with ui.button_group():
                    ui.button("Select", on_click=lambda: set_selected_rows_value('plot3', True))
                    ui.button("Deselect", on_click=lambda: set_selected_rows_value('plot3', False))
                with ui.button_group():
                    ui.button("Select All", on_click=lambda: set_entire_plot_column('plot3', True))
                    ui.button("Deselect All", on_click=lambda: set_entire_plot_column('plot3', False))
            
            ui.label('Plot 4').style('font-size: 14px; font-weight: bold;')
            with ui.column():
                with ui.button_group():
                    ui.button("Select", on_click=lambda: set_selected_rows_value('plot4', True))
                    ui.button("Deselect", on_click=lambda: set_selected_rows_value('plot4', False))
                with ui.button_group():
                    ui.button("Select All", on_click=lambda: set_entire_plot_column('plot4', True))
                    ui.button("Deselect All", on_click=lambda: set_entire_plot_column('plot4', False))
            
            
           
        

    # main content
    with ui.row().classes('mx-auto'):
        # initialize tab panels
        with ui.tabs().classes('w-full') as tabs:
            line_chart = ui.tab('Line Chart View')
            signals_table = ui.tab('Signals Table')

        # create tab panels
        with ui.tab_panels(tabs, value=line_chart).classes('w-full'):
            with ui.tab_panel(line_chart):

                with ui.row().classes('w-full justify-around'):
                    def update_layout():
                        global left_drawer_state
                        layout = toggle1.value
                        drawer_width = 300 if left_drawer_state else 0  # Width of the drawer in pixels, 0 if closed
                        full_width = f'calc(95vw - {drawer_width}px)'
                        half_width = f'calc(47vw - {drawer_width/2}px)'
                        full_height = f'calc(95vh - 135px)' # approximately height of the navbar + tabsbar
                        half_height = f'calc(45vh - 67px)'

                        if layout == "1x1":
                            plot1.style(f'display: block; width: {full_width}; height: {full_height};').classes('mx-auto')
                            plot2.style('display: none;')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                        elif layout == "1x2":
                            plot1.style(f'display: block; width: {half_width}; height: {full_height};').classes('mx-auto')
                            plot2.style(f'display: block; width: {half_width}; height: {full_height};').classes('mx-auto')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                        elif layout == "2x1":
                            plot1.style(f'display: block; width: {full_width}; height: {half_height};').classes('mx-auto')
                            plot2.style(f'display: block; width: {full_width}; height: {half_height};').classes('mx-auto')
                            plot3.style('display: none;')
                            plot4.style('display: none;')
                        elif layout == "2x2":
                            plot1.style(f'display: block; width: {half_width}; height: {half_height};').classes('mx-auto')
                            plot2.style(f'display: block; width: {half_width}; height: {half_height};').classes('mx-auto')
                            plot3.style(f'display: block; width: {half_width}; height: {half_height};').classes('mx-auto')
                            plot4.style(f'display: block; width: {half_width}; height: {half_height};').classes('mx-auto')

                        ui.run_javascript('window.dispatchEvent(new Event("resize"));')

                    # Update drawer state and layout when drawer is toggled
                    def on_drawer_toggle(state):
                        global left_drawer_state
                        left_drawer_state = state
                        update_layout()
                        
                        # calculate new grid width
                        grid_width = f'calc(95vw - {300 if left_drawer_state else 0}px)'
                        
                        # update new grid width
                        grid.style(f'width: {grid_width}; height: 85vh;')
                        grid.update()

                    # Connect drawer toggle event to our custom function
                    left_drawer.on('show', lambda: on_drawer_toggle(True))
                    left_drawer.on('hide', lambda: on_drawer_toggle(False))


                    # Connect layout toggle to update function
                    toggle1.on_value_change(update_layout)

                    # create plots with custom settings
                    fig1 = customize_plot(px.line(df_global, x='Time', y=y_columns, title='Plot 1', template="plotly_white"))
                    plot1 = ui.plotly(fig1).on('plotly_relayout', lambda event: on_zoom(0, event)).classes('mx-auto').style('display: none;')

                    fig2 = customize_plot(px.line(df_global, x='Time', y=y_columns, title='Plot 2', template="plotly_white"))
                    plot2 = ui.plotly(fig2).on('plotly_relayout', lambda event: on_zoom(1, event)).classes('mx-auto').style('display: none;')

                    fig3 = customize_plot(px.line(df_global, x='Time', y=y_columns, title='Plot 3', template="plotly_white"))
                    plot3 = ui.plotly(fig3).on('plotly_relayout', lambda event: on_zoom(2, event)).classes('mx-auto').style('display: none;')

                    fig4 = customize_plot(px.line(df_global, x='Time', y=y_columns, title='Plot 4', template="plotly_white"))
                    plot4 = ui.plotly(fig4).on('plotly_relayout', lambda event: on_zoom(3, event)).classes('mx-auto').style('display: none;')

                    figs = [fig1, fig2, fig3, fig4]
                    plots = [plot1, plot2, plot3, plot4]

                    # Update plot visibility based on settings 
                    update_visibility()

            # signals table with ui.aggrid
            with ui.tab_panel(signals_table):
                # data from df_signals
                data = df_signals.to_dict(orient='records')

                # aggrid structure
                column_defs = [
                    {"headerName": f"CSV File name | Total files: {len(processed_filenames)}", "field": "csv_filename"},
                    {"headerName": "Signal Name", "field": "signal_name"}, 
                    {"headerName": "Plot 1", "field": "plot1", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 2", "field": "plot2", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 3", "field": "plot3", "cellEditor": "agCheckboxCellEditor", "editable": True},
                    {"headerName": "Plot 4", "field": "plot4", "cellEditor": "agCheckboxCellEditor", "editable": True},
                ]
                
                grid_width = f'calc(95vw - {300 if left_drawer_state else 0}px)'
                # create aggrid grid
                grid = ui.aggrid({
                    'defaultColDef': {'flex': 1},
                    'columnDefs': column_defs,
                    'rowData': data,
                    'rowSelection': 'multiple',
                }).style(f'width: {grid_width}; height: 85vh;').classes('mx-auto')

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

# run in native mode
ui.run(title="PlottingApplication", native=True, fullscreen=False, window_size=(2500, 1300))