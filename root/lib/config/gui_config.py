main_grid = {
    "input_frame": {
        "config": {"row": 1, "sticky": "ew", "padx": 5, "pady": (5,0)},
        "entry_box": {"row": 0, "column": 0, "sticky": "ew", "padx": 5, "pady": (5,5)},
        "browse_button": {"text": "Browse", "row": 0, "column": 2, "sticky": "ew", "padx": 5, "pady": (5,5)},
        "check_headers": {"text": "First row is headers.", "row": 1, "column": 0,
                          "sticky": "w", "padx": 5, "pady": (5,5)},
        "check_code_and_name": {"text": "Data includes both Code and Name",
                                "row": 2, "sticky": "w", "padx": 10, "pady": (5,5)},
    },

    "date_frame": {
        "config": {"row": 2, "sticky": "ew", "padx": 5, "pady": (5, 0)},
        "date_format_label": {"text": "Date format:", "row": 0, "column": 0, "sticky": "w",
                              "padx": 5, "pady": (5,0)},
        "date_entry_box": {"row": 0, "column": 1, "sticky": "ew", "padx": 5, "pady": (5,0)},
        "format_date_button" : {"text": "Confirm", "row": 0, "column": 2, "sticky": "ew", "padx": 5, "pady": (5,0)},
        "date_start_label": {"text": "Select start date:", "row": 1, "column": 0, "sticky": "w",
                             "padx": 5, "pady": (5,0)},
        "calendar_start": {"row": 1, "column": 1, "sticky": "w", "padx": 5, "pady": (5,0)},
        "date_end_label": {"text": "Select end date:", "row": 2, "column": 0, "sticky": "w",
                           "padx": 5, "pady": (5,5)},
        "calendar_end": {"row": 2, "column": 1, "sticky": "w", "padx": 5, "pady": (5,5)}
    },

    "df_frame": {
        "config": {"row": 3, "height": 300, "sticky": "ew", "padx": 5, "pady": (5, 0)},
        "tree": {"row": 0, "column": 0, "sticky": "ew", "padx": 5, "pady": (5, 5)},
        "vertical_stroll_bar": {"row": 0, "column": 1, "sticky": "ns"},
        "horizontal_stroll_bar": {"row": 1, "column": 0, "sticky": "ew"}
    },

    "output_frame": {
        "config": {"row": 4, "sticky": "ew", "padx": 5, "pady": (5, 0)},
        "run_button": {"text": "Start",
                       "row": 0, "column": 0, "sticky": "ew", "padx": 5, "pady": (5, 5)},
        "view_log_button": {"text": "View Log",
                            "row": 0, "column": 1, "sticky": "ew", "padx": 5, "pady": (5, 5)},
        "cancel_button": {"text": "Exit",
                          "row": 0, "column": 2, "sticky": "ew", "padx": 5, "pady": (5, 5)}
    },

    "log_frame": {
        "config": {"row": 5, "sticky": "ew", "padx": 5, "pady": (5, 5)},
        "log_label": {"text": "Press Start",
                      "row": 0, "column": 0, "columnspan": 2, "sticky": "nw", "padx": 5, "pady": (5,0)},
        "loading_label": {"row": 0, "column": 2, "columnspan": 1, "sticky": "ew", "padx": 5, "pady": (5,5)}
    }
}