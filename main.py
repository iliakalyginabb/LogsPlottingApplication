from nicegui import ui
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
from io import StringIO
import plotly.colors as colors

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

            # update plot visibility
            def update_visibility():
                for i, checkbox in enumerate(checkboxes):
                    fig.data[i].visible = checkbox.value
                plot.update()

            # create checkboxes
            checkboxes = []
            y_columns = [col for col in df.columns if col not in ['Time', 'Unnamed: 6']]
            for col in y_columns:
                checkbox = ui.checkbox(f'{col}', value=True, on_change=update_visibility)
                checkboxes.append(checkbox)

            # back button
            ui.button('Upload another').on('click', lambda: ui.run_javascript('window.location.href = "/";')).classes('mx-auto')

        # main content
        with ui.row().classes('mx-auto'):
            
            # layout button
            with ui.button('Layout').classes('mx-auto'):
                with ui.menu() as menu:
                    ui.menu_item('1x1', on_click=lambda: update_layout(1, 1))
                    ui.menu_item('1x2', on_click=lambda: update_layout(1, 2))
                    ui.menu_item('2x1', on_click=lambda: update_layout(2, 1))
                    ui.menu_item('2x2', on_click=lambda: update_layout(2, 2))

            # tabs
            with ui.tabs().classes('w-full') as tabs:
                line_chart = ui.tab('Line Chart View')
                table_view = ui.tab('Table View')

            # tab panels
            with ui.tab_panels(tabs, value=line_chart).classes('w-full'):
                with ui.tab_panel(line_chart):
                    # create default 1x1 plotly graph from csv
                    fig = make_subplots(rows=1, cols=1, subplot_titles=["Plot 1"])
                    color_sequence = colors.qualitative.Plotly
                    for i, col in enumerate(y_columns):
                        fig.add_trace(px.line(df, x='Time', y=col, color_discrete_sequence=[color_sequence[i % len(color_sequence)]]).data[0], row=1, col=1)
                    plot = ui.plotly(fig).classes('mx-auto').style('width: 85vw; height: 80vh;')
                
                with ui.tab_panel(table_view):
                    # create table from csv
                    df_table = df.drop(columns=['Unnamed: 6'], errors='ignore')
                    ui.table(columns=[{'name': col, 'label': col, 'field': col, 'sortable':True} for col in df_table.columns], rows=df_table.to_dict(orient='records')).classes('mx-auto')

        # adjust layout 1x1, 1x2, 2x1, 2x2
        def update_layout(rows, cols):
            fig = make_subplots(rows=rows, cols=cols, subplot_titles=[f"Plot {i+1}" for i in range(rows*cols)])
            for i, column in enumerate(y_columns):
                row = (i // cols) + 1
                col = (i % cols) + 1
                if row <= rows and col <= cols:
                    fig.add_trace(px.line(df, x='Time', y=column, color_discrete_sequence=[color_sequence[i % len(color_sequence)]]).data[0], row=row, col=col)
            plot.figure = fig
            plot.update()

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
