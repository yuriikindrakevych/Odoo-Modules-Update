# Google Sheet Importer

This module provides functionality to dynamically map Google Sheets columns to Odoo models, import data with cron jobs, and avoid duplicates while adhering to field constraints.

## Features
- Map Google Sheets columns to Odoo models dynamically.
- Set mandatory fields, avoid duplicates, and manage data integrity.
- Schedule imports using Odoo's ir.cron functionality.

## Installation
Install the module via the Odoo Apps interface or manually by placing it in your addons directory and updating the apps list.

## Usage
1. Configure your Google Sheets credentials.
2. Set up mapping rules between sheet columns and Odoo models.
3. Schedule data imports via cron jobs.

## License
This module is licensed under the Odoo App Store guidelines.

## Screenshots
![Mapping Configuration](static/description/mapping_configuration.png)
![Scheduled Imports](static/description/scheduled_imports.png)
