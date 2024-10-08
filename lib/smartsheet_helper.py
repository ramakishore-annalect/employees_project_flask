import smartsheet
import json
import requests
import logging
from pathlib import Path


class SmartsheetJSONUpdater:
    def __init__(self, access_token, log_level=logging.INFO):
        self.smart = smartsheet.Smartsheet(access_token)
        self.smart.errors_as_exceptions(True)

        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def get_or_create_folder(self, folder_name):
        """Get or create a folder in Smartsheet."""
        self.logger.info(f"Checking if folder '{folder_name}' exists")
        folders = self.smart.Home.list_folders().data
        for folder in folders:
            if folder.name == folder_name:
                self.logger.info(
                    f"Folder '{folder_name}' already exists. ID: {folder.id}"
                )
                return folder.id

        self.logger.info(f"Folder '{folder_name}' not found. Creating new folder.")
        response = self.smart.Home.create_folder(folder_name)
        self.logger.info(f"Folder '{folder_name}' created. ID: {response.result.id}")
        return response.result.id

    def get_or_create_sheet(self, folder_id, sheet_name, columns):
        """Get or create a sheet in the specified folder."""
        self.logger.info(f"Checking if sheet '{sheet_name}' exists in folder")
        folder = self.smart.Folders.get_folder(folder_id)
        for sheet in folder.sheets:
            if sheet.name == sheet_name:
                self.logger.info(f"Sheet '{sheet_name}' already exists. ID: {sheet.id}")
                return sheet.id

        self.logger.info(f"Sheet '{sheet_name}' not found. Creating new sheet.")
        column_specs = [
            {"title": col, "type": "TEXT_NUMBER", "primary": i == 0}
            for i, col in enumerate(columns)
        ]
        sheet_spec = smartsheet.models.Sheet(
            {"name": sheet_name, "columns": column_specs}
        )
        response = self.smart.Folders.create_sheet_in_folder(folder_id, sheet_spec)
        self.logger.info(f"Sheet '{sheet_name}' created. ID: {response.result.id}")
        return response.result.id

    def update_sheet(self, sheet_id, data_array):
        """Update the Smartsheet with the given data array."""
        self.logger.info(f"Updating sheet with ID: {sheet_id}")
        sheet = self.smart.Sheets.get_sheet(sheet_id)

        rows = []
        for data in data_array:
            new_row = smartsheet.models.Row()
            new_row.to_bottom = True
            for column in sheet.columns:
                cell_value = data.get(column.title, "")
                new_row.cells.append({"column_id": column.id, "value": str(cell_value)})
            rows.append(new_row)

        # Add rows in batches of 500 (Smartsheet limit)
        batch_size = 500
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            response = self.smart.Sheets.add_rows(sheet_id, batch)
            self.logger.info(
                f"Added batch of {len(batch)} rows to sheet. Result: {response.result}"
            )

        self.logger.info(f"Total {len(rows)} rows added to sheet.")

    def update_from_json(self, json_data, folder_name, sheet_name):
        """Update Smartsheet from a JSON file containing an object or an array of objects."""
        self.logger.info("Starting Smartsheet update process")

        try:

            print(f"Reading JSON file or dictionary: {json_data}")
            # with open(json_path, "r") as json_file:
            #    json_data = json.load(json_file)

            # Check if the JSON is a single object or has a 'data' key with an array
            if isinstance(json_data, dict):
                if "data" in json_data and isinstance(json_data["data"], list):
                    data_array = json_data["data"]
                else:
                    data_array = [json_data]  # Wrap single object in a list
            elif isinstance(json_data, list):
                data_array = json_data
            else:
                raise ValueError(
                    "Invalid JSON structure. Expected an object or an array of objects."
                )

            if not data_array:
                raise ValueError("No data found in JSON")

            # Get or create folder
            folder_id = self.get_or_create_folder(folder_name)

            # Get or create sheet
            columns = list(
                data_array[0].keys()
            )  # Assume all objects have the same structure
            sheet_id = self.get_or_create_sheet(folder_id, sheet_name, columns)

            # Update sheet with data
            self.update_sheet(sheet_id, data_array)

            self.logger.info("Smartsheet update process completed successfully")

        except smartsheet.exceptions.SmartsheetException as e:
            self.logger.error(f"Smartsheet API error: {e}")
            self.logger.error(f"Smartsheet API error details: {e.message}")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON Decode Error: {e}")
            self.logger.error(f"Error occurred at line {e.lineno}, column {e.colno}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.logger.error("Full traceback:", exc_info=True)


class SmartsheetEventProcessor:
    def __init__(self, api_token, sheet_id):
        self.api_token = api_token
        self.base_url = "https://api.smartsheet.com/2.0"
        self.sheet_id = sheet_id
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def get_row_details(self, row_id):
        """Fetch details for a specific row in the sheet."""
        url = f"{self.base_url}/sheets/{self.sheet_id}/rows/{row_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get row details: {response.status_code}, {response.text}")
            return None

    def get_column_details(self, column_id):
        """Fetch details for a specific column in the sheet."""
        url = f"{self.base_url}/sheets/{self.sheet_id}/columns/{column_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Failed to get column details: {response.status_code}, {response.text}"
            )
            return None

    def get_cell_value(self, row_details, column_id):
        """Fetch the updated cell value from the row details based on the column ID."""
        for cell in row_details.get("cells", []):
            if cell.get("columnId") == column_id:
                return cell.get("value")
        return None

    def get_updated_values(self, events):
        """Fetch updated values from the events and return as a dictionary with column names as keys."""
        updated_values = {}

        for event in events:
            if event["objectType"] == "cell" and event["eventType"] in [
                "updated",
                "created",
            ]:
                row_id = event["rowId"]
                column_id = event["columnId"]

                # Fetch row details
                row_details = self.get_row_details(row_id)
                if not row_details:
                    continue

                # Fetch column details (to get the column name)
                column_details = self.get_column_details(column_id)
                if not column_details:
                    continue
                column_name = column_details.get("title")

                # Fetch the updated or created cell value from the row
                updated_value = self.get_cell_value(row_details, column_id)

                # Add to the dictionary
                if column_name and updated_value is not None:
                    updated_values[column_name] = updated_value

        return updated_values
