from nicegui import ui
import pandas as pd
import plotly.express as px
from io import StringIO

df_global = pd.DataFrame() # dataframe to store uploaded data
plot_settings = {} # stores plot visibility settings for each plot

# functio to handle csv upload
def handle_upload(event):
    global df_global
    content = event.content.read().decode('utf-8')
    new_df = pd.read_csv(StringIO(content), delimiter=';')

    # merge new data with existing global dataframe
    df_global = pd.concat([df_global, new_df], ignore_index=True)

    # redirect to results page
    ui.run_javascript('window.location.href = "/results";')

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
        # Add True for new columns
        saved_settings.extend([True] * (len(y_columns) - len(saved_settings)))
    elif len(saved_settings) > len(y_columns):
        # Trim saved settings if fewer columns are present in the new CSV
        saved_settings = saved_settings[:len(y_columns)]

    # Save the adjusted settings back into plot_settings
    plot_settings[plot_id] = saved_settings

    # Create the dialog with checkboxes
    with ui.dialog() as signals_dialog:
        with ui.card():
            ui.label(f"{title} signals")
            for i, col in enumerate(y_columns):
                checkbox = ui.checkbox(
                    f'{col}', 
                    value=saved_settings[i],  # Use saved value if available
                    on_change=lambda: update_visibility(checkboxes, fig, plot, plot_id)
                )
                checkboxes.append(checkbox)
            ui.button('Close', on_click=signals_dialog.close)
    signals_dialog.open()


# show results function
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

        # create plot settings dialog
        def open_plot1_settings():
            open_plot_settings(y_columns, fig1, plot1, 'Plot 1', 'plot1')

        def open_plot2_settings():
            open_plot_settings(y_columns, fig2, plot2, 'Plot 2', 'plot2')

        def open_plot3_settings():
            open_plot_settings(y_columns, fig3, plot3, 'Plot 3', 'plot3')

        def open_plot4_settings():
            open_plot_settings(y_columns, fig4, plot4, 'Plot 4', 'plot4')

        # Add buttons to open dialogs for plot settings
        button_plot1 = ui.button('Plot 1 settings', on_click=open_plot1_settings).classes('w-full')
        button_plot2 = ui.button('Plot 2 settings', on_click=open_plot2_settings).classes('w-full')
        button_plot3 = ui.button('Plot 3 settings', on_click=open_plot3_settings).classes('w-full')
        button_plot4 = ui.button('Plot 4 settings', on_click=open_plot4_settings).classes('w-full')

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
