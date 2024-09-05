version = "v0.1"
UI_grid = {
    "input_frame": {
        "config": {"row": 0, "sticky": "ew", "padx": 5, "pady": (5,0)},
        "entry_box": {"row": 0, "column": 0, "sticky": "ew", "padx": 5, "pady": (5,0)},
        "browse_button": {"text": "Browse",
                          "row": 0, "column": 4, "sticky": "e", "padx": 5, "pady": (5,0)},
        "check_headers": {"text": "My file has headers", "row": 1, "column": 0,
                          "sticky": "w", "padx": 10, "pady": (5,0)},
        "check_code_and_name": {"text": "Data includes both Code and Name", "row": 2,
                                "sticky": "w", "padx": 10, "pady": (5,5)},
    },

    "date_frame": {
        "config": {"row": 1, "sticky": "ew", "padx": 5, "pady": (5, 0)},
        "date_format_label": {"text": "Date format:", "row": 0, "column": 0, "sticky": "w",
                              "padx": 5, "pady": (5,0)},
        "date_entry_box": {"row": 0, "column": 1, "sticky": "ew", "padx": 5, "pady": (5,0)},
        "date_start_label": {"text": "Select start date:", "row": 1, "column": 0, "sticky": "w",
                             "padx": 5, "pady": (5,0)},
        "calendar_start": {"row": 1, "column": 1, "sticky": "w", "padx": 5, "pady": (5,0)},
        "date_end_label": {"text": "Select end date:", "row": 2, "column": 0, "sticky": "w",
                           "padx": 5, "pady": (5,5)},
        "calendar_end": {"row": 2, "column": 1, "sticky": "w", "padx": 5, "pady": (5,5)}
    },

    "df_frame": {
        "config": {"row": 2, "height": 300, "sticky": "ew", "padx": 5, "pady": (5, 0)},
        "tree": {"row": 0, "column": 0, "sticky": "ew", "padx": 5, "pady": (5, 5)},
        "vertical_stroll_bar": {"row": 0, "column": 1, "sticky": "ns"},
        "horizontal_stroll_bar": {"row": 1, "column": 0, "sticky": "ew"}
    },

    "output_frame": {
        "config": {"row": 3, "sticky": "ew", "padx": 5, "pady": (5, 0)},
        "run_button": {"text": "Start",
                       "row": 0, "column": 0, "sticky": "w", "padx": 5, "pady": (5, 5)},
        "view_log_button": {"text": "View Log",
                            "row": 0, "column": 1, "sticky": "w", "padx": 5, "pady": (5, 5)},
        "cancel_button": {"text": "Exit",
                          "row": 0, "column": 2, "sticky": "e", "padx": 5, "pady": (5, 5)}
    },

    "log_frame": {
        "config": {"row": 4, "sticky": "ew", "padx": 5, "pady": (5, 5)},
        "log_label": {"text": "Press Start", "row": 0, "column": 0, "sticky": "w", "padx": (5, 5)}
    }
}

error_messages = {"Invalid File Path": ["Invalid File Path", "File does not exist!"],

                  "UnicodeDecodeError": ["Read Error", "Program is having trouble reading your file." +
                                         " Ensure CSV is saved as UTF-8 (*CSV) file."],

                  "AttributeError": ["Object Error", "Unable to perform critical operations on file."],

                  "LimitWarning": ["Limit Warning", "Data exceeds output limit. Run anyway?",
                                   "Data exceeds output limit." +
                                   " Recommended to reduce number of dimensions or rows of data."],

                  "RuntimeError": ["Runtime Error", "Program encountered an error in writing data into CSV." +
                                   " Actually this is an unfixable error." +
                                   " Try having no adjacent NA values in your input file."],
                  }