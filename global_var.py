UI_grid = {"entry_box": {"row": 0, "column": 0, "width": 300, "sticky": "nw", "padx": 10, "pady": 0},

           "date_entry_box": {"row": 0, "column": 1, "width": 300, "sticky": "w", "padx": 10, "pady": 0},

           "date_label": {"text": "Date format:",
                         "row": 0, "column": 0, "height": 2, "sticky": "nw", "padx": 10, "pady": 10},

           "calendar_start": {"row": 1, "column": 0, "height": 2, "sticky": "nw", "padx": 10, "pady": 10},

           "calendar_end": {"row": 1, "column": 1, "height": 2, "sticky": "nw", "padx": 10, "pady": 10},

           "browse_button": {"text": "Browse",
                             "row": 0, "column": 1, "width": 10, "sticky": "nw", "padx": 10, "pady": 0},

           "check_headers": {"text": "My file has headers",
                             "row": 1, "column": 0, "sticky": "w", "padx": 10, "pady": 5},

           "check_code_and_name": {"text": "Data includes both Code and Name",
                                   "row": 2, "column": 0, "sticky": "w", "padx": 10, "pady": 5},

           "input_frame": {"row": 0, "width": 400, "sticky": "w", "padx": 0, "pady": 0},

           "date_frame": {"row": 1, "width": 400, "sticky": "w", "padx": 0, "pady": 0},

           "df_frame": {"row": 2, "width": 400, "height": 300, "sticky": "n", "padx": 0, "pady": 0},

           "output_frame": {"row": 4, "width": 400, "sticky": "s", "padx": 0, "pady": 0},

           "tree": {"row": 0, "column": 0, "width": 400, "height": 300, "sticky": "w"},

           "vertical_stroll_bar": {"row": 0, "column": 1, "sticky": "ns"},

            "horizontal_stroll_bar": {"row": 1, "column": 0, "sticky": "ew"},

            "log_label": {"text": "Press Start",
                          "row": 3, "column": 0, "height": 2, "sticky": "nw", "padx": 10},

            "run_button": {"text": "Start",
                           "row": 0, "column": 0, "width": 10, "sticky": "w", "padx": 10, "pady": 10},

            "view_log_button": {"text": "View Log",
                                "row": 0, "column": 1, "width": 10, "sticky": "w", "padx": 10, "pady": 10},

            "cancel_button": {"text": "Exit",
                              "row": 0, "column": 2, "width": 10, "sticky": "e", "padx": 10,"pady": 10}
            }

error_messages = {"Invalid File Path": ["Invalid File Path", "File does not exist!"],

                  "UnicodeDecodeError": ["Read Error",
                                         "Program is having trouble reading your file." +
                                         "Ensure CSV is saved as UTF-8 (*CSV) file."],

                  "AttributeError": ["Object Error", "Unable to perform critical operations on file."],

                  "LimitError": ["Limit Error", "Data exceeds output limit." +
                                 "Please reduce number of dimensions or rows of data."]
                  }