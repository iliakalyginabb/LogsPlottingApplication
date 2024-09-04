from nicegui import ui

with ui.card().classes("mx-auto").style('background: transparent; border: none; box-shadow: none;'):
    ui.upload(on_upload=lambda e: ui.notify(f'Uploaded {e.name}')).classes('max-w-full')

ui.run()
