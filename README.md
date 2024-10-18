# Plotting Application

- [Plotting Application](#plotting-application)
  - [Overview](#overview)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Main Components](#main-components)
    - [CSV Upload](#csv-upload)
    - [Plotting](#plotting)
    - [Signal Management](#signal-management)
    - [Settings](#settings)
  - [Customization](#customization)
  - [Screenshots](#screenshots)

## Overview

Python-based plotting application built using the NiceGUI and Plotly framework. It allows users to upload CSV files, visualize data in interactive plots, and manage signal visibility across multiple plots.

## Features

- CSV file upload and parsing
- Interactive line charts with up to four plot views
- Flexible layout options (1x1, 1x2, 2x1, 2x2)
- Synchronizable x-axis zoom across plots
- Signal management through an interactive table
- Context menu for quick signal selection/deselection
- Responsive design adapting to window size and drawer state

## Tools and Versions Used in Development

| Name    | Version |
|---------|---------|
| python  | 3.11.2  |
| nicegui | 2.1.0   |
| pandas  | 2.2.2   |
| plotly  | 5.24.0  |

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

- Supports upload of multiple csv files
- Use the "Upload CSV" button in the left drawer to load data.
- The application supports CSV files with a semicolon (;) delimiter.
- In the csv_logs folder are some sample csvs to test the funcationalty of the application

### Plotting

- Up to four interactive line plots can be displayed.
- Use the layout toggle in the left drawer to change the plot arrangement.
- Zoom synchronization by the x-axis can be enabled/disabled for each plot.

### Signal Management

- The "Signals Table" tab provides an interactive grid to manage signal visibility.
- Use checkboxes to show/hide signals on specific plots.
- The grid context menu offers quick selection/deselection options.

### Settings

- The left drawer contains various settings and actions:
  - CSV upload
  - Layout selection
  - Zoom synchronization for x-axis
  - Bulk selection/deselection actions

## Customization

- Modify the `customize_plot` function to change plot appearance.
- Adjust the `column_defs` in the signals table to alter the grid structure.

## Screenshots

![linechartview](/img/linechartview.png)

![signalstable](/img/signalstable.png)
