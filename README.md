# Plotting Application

## Overview

Python-based plotting application built using the NiceGUI framework. It allows users to upload CSV files, visualize data in interactive plots, and manage signal visibility across multiple plots.

## Features

- CSV file upload and parsing
- Interactive line charts with up to four plot views
- Flexible layout options (1x1, 1x2, 2x1, 2x2)
- Synchronizable zoom across plots
- Signal management through an interactive table
- Context menu for quick signal selection/deselection
- Responsive design adapting to window size and drawer state

## Requirements

- Python 3.7+
- NiceGUI
- pandas
- plotly
- io

## Installation

1. Clone this repository
2. Install the required packages:

    ```bash
   pip install nicegui pandas plotly
   ```

## Usage

1. Run the application:

   ```bash
   python main.py
   ```

2. The application will open in a native window.
3. Use the "Upload CSV" button in the left drawer to load your data.
4. Interact with the plots and use the signals table to manage visibility.

## Main Components

### CSV Upload

- Use the "Upload CSV" button in the left drawer to load data.
- The application supports CSV files with a semicolon (;) delimiter.
- In the csv_logs_1 and csv_logs_2 are some sample csvs to test the applications funcationalty

### Plotting

- Up to four interactive line plots can be displayed.
- Use the layout toggle in the left drawer to change the plot arrangement.
- Zoom synchronization can be enabled/disabled for each plot.

### Signal Management

- The "Signals Table" tab provides an interactive grid to manage signal visibility.
- Use checkboxes to show/hide signals on specific plots.
- The context menu offers quick selection/deselection options.

### Settings

- The left drawer contains various settings and actions:
  - CSV upload
  - Layout selection
  - Zoom synchronization
  - Bulk selection/deselection actions

## Customization

- Modify the `customize_plot` function to change plot appearance.
- Adjust the `column_defs` in the signals table to alter the grid structure.
