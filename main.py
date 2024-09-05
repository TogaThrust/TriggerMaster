import os
import sys
from datetime import datetime

# standard libraries
import pandas as pd
import itertools

# tkinter
import customtkinter as ctk
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("theme.json") # todo create custom theme
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox


# noinspection PyTypeChecker
class GUI:
    def __init__(self):
        self.chunk_size = 2
        self.df_validated = None
        self.log = ""
        self.output_limit = 100000000
        # UI main
        self.root = ctk.CTk()
        self.root.title("Trigger Duplicator")
        self.root.resizable(False, False)
        # characteristics of widgets
        self.UI_grid = {"entry_box":                {"row": 0,
                                                     "column": 0,
                                                     "sticky": ctk.NW,
                                                     "width": 300,
                                                     "padx": 10,
                                                     "pady": 0},

                        "browse_button":            {"text": "Browse",
                                                     "width": 10,
                                                     "row": 0,
                                                     "column": 1,
                                                     "sticky": ctk.NW,
                                                     "padx": 10,
                                                     "pady": 0},

                        "check_headers":            {"text": "My file has headers",
                                                     "row": 1,
                                                     "column": 0,
                                                     "padx": 10,
                                                     "pady": 5,
                                                     "sticky": ctk.W},

                        "check_code_and_name":      {"text": "Data includes both Code and Name",
                                                     "row": 2,
                                                     "column": 0,
                                                     "padx": 10,
                                                     "pady": 5,
                                                     "sticky": ctk.W},

                        "input_frame":              {"row": 0 ,
                                                     "sticky": ctk.N,
                                                     "width": 400,
                                                     "padx": 0,
                                                     "pady": 0},

                        "df_frame":                 {"row": 1,
                                                     "sticky": ctk.N,
                                                     "width": 400,
                                                     "height": 300,
                                                     "padx": 0,
                                                     "pady": 0},

                        "output_frame":             {"row": 3,
                                                     "sticky": ctk.W,
                                                     "width": 400,
                                                     "padx": 0,
                                                     "pady": 0},

                        "tree":                     {"row": 0 ,
                                                     "column": 0,
                                                     "width": 50,
                                                     "height": 300,
                                                     "sticky": ctk.NSEW},

                        "vertical_stroll_bar":      {"row": 0 ,
                                                     "column": 1,
                                                     "sticky": ctk.NS},

                        "horizontal_stroll_bar":    {"row": 1 ,
                                                     "column": 0,
                                                     "sticky": ctk.EW},

                        "log_label":                {"text":"Press Start",
                                                     "row": 2 ,
                                                     "column": 0,
                                                     "padx": 10,
                                                     "height": 2,
                                                     "sticky": ctk.NW},

                        "run_button":               {"text": "Start",
                                                     "width": 10,
                                                     "row": 1,
                                                     "column": 0,
                                                     "sticky": ctk.W,
                                                     "padx": 10,
                                                     "pady": 10},

                        "view_log_button":      {"text": "View Log",
                                                     "width": 10,
                                                     "row": 1,
                                                     "column": 1,
                                                     "sticky": ctk.W,
                                                     "padx": 10,
                                                     "pady": 10},

                        "cancel_button":            {"text": "Exit",
                                                     "width": 10,
                                                     "row": 1,
                                                     "column": 2,
                                                     "sticky": ctk.E,
                                                     "padx": 10,
                                                     "pady": 10}
                        }

        self.error_messages = {
            "Invalid File Path":    ["Invalid File Path","File does not exist!"],
            "UnicodeDecodeError":   ["Read Error", "Program is having trouble reading your file. Ensure CSV is saved as UTF-8 (*CSV) file."],
            "AttributeError":       ["Object Error","Unable to perform critical operations on file."],
            "LimitError":           ["Limit Error", "Data exceeds output limit. Please reduce number of dimensions or rows of data."]
        }

        # Widgets on initialisation
        self.input_frame = ttk.Frame(self.root, width=self.UI_grid["input_frame"]["width"])
        self.input_frame.grid(row=self.UI_grid["input_frame"]["row"],
                              sticky=self.UI_grid["input_frame"]["sticky"])

        self.entry_box = ctk.CTkEntry(self.input_frame, width=self.UI_grid["entry_box"]["width"])
        self.entry_box.grid(row=self.UI_grid["entry_box"]["row"],
                            column=self.UI_grid["entry_box"]["column"],
                            sticky=self.UI_grid["entry_box"]["sticky"],
                            padx=self.UI_grid["entry_box"]["padx"],
                            pady=self.UI_grid["entry_box"]["pady"])
        self.entry_box.insert(0, "Choose a CSV file...")

        self.browse_button = (ctk.CTkButton(self.input_frame,
                                        text=self.UI_grid["browse_button"]["text"],
                                        width=self.UI_grid["browse_button"]["width"],
                                        command=self.browse_file))
        self.browse_button.grid(row=self.UI_grid["browse_button"]["row"],
                                column=self.UI_grid["browse_button"]["column"],
                                sticky=self.UI_grid["browse_button"]["sticky"],
                                padx=self.UI_grid["browse_button"]["padx"],
                                pady=self.UI_grid["browse_button"]["pady"])

        self.check_headers_state = ctk.IntVar()
        self.check_headers = ctk.CTkCheckBox(self.input_frame,
                                             variable=self.check_headers_state,
                                             text=self.UI_grid["check_headers"]["text"])
        self.check_headers.grid(row=self.UI_grid["check_headers"]["row"],
                                column=self.UI_grid["check_headers"]["column"],
                                padx=self.UI_grid["check_headers"]["padx"],
                                pady=self.UI_grid["check_headers"]["pady"],
                                sticky=self.UI_grid["check_headers"]["sticky"])
        self.check_headers.toggle()

        self.check_code_and_name = ctk.IntVar() # todo Important. need include this logic too
        self.check_code_and_name = ctk.CTkCheckBox(self.input_frame,
                                                  variable=self.check_code_and_name,
                                                  text=self.UI_grid["check_code_and_name"]["text"])
        self.check_code_and_name.grid(row=self.UI_grid["check_code_and_name"]["row"],
                                      column=self.UI_grid["check_code_and_name"]["column"],
                                      padx=self.UI_grid["check_code_and_name"]["padx"],
                                      pady=self.UI_grid["check_code_and_name"]["pady"],
                                      sticky=self.UI_grid["check_code_and_name"]["sticky"])
        self.check_code_and_name.toggle()
        # todo Important. Date selector
        self.output_frame = ttk.Frame(self.root, width=self.UI_grid["output_frame"]["width"])
        self.output_frame.grid(row=self.UI_grid["output_frame"]["row"],
                               sticky=self.UI_grid["output_frame"]["sticky"])

        self.run_button = (ctk.CTkButton(self.output_frame,
                                     text=self.UI_grid["run_button"]["text"],
                                     command=lambda: self.permutate_and_combine(df_input=self.df_validated),
                                     width=self.UI_grid["run_button"]["width"]))
        self.run_button.grid(row=self.UI_grid["run_button"]["row"],
                             column=self.UI_grid["run_button"]["column"],
                             sticky=self.UI_grid["run_button"]["sticky"],
                             padx=self.UI_grid["run_button"]["padx"],
                             pady=self.UI_grid["run_button"]["pady"])
        self.run_button.configure(state=ctk.DISABLED)

        self.view_log_button = (ctk.CTkButton(self.output_frame,
                                              text=self.UI_grid["view_log_button"]["text"],
                                              command=self.view_log,
                                              width=self.UI_grid["view_log_button"]["width"]))
        self.view_log_button.grid(row=self.UI_grid["view_log_button"]["row"],
                                  column=self.UI_grid["view_log_button"]["column"],
                                  sticky=self.UI_grid["view_log_button"]["sticky"],
                                  padx=self.UI_grid["view_log_button"]["padx"],
                                  pady=self.UI_grid["view_log_button"]["pady"])

        self.cancel_button = (ctk.CTkButton(self.output_frame,
                                        text=self.UI_grid["cancel_button"]["text"],
                                        command=self.close,
                                        width=self.UI_grid["cancel_button"]["width"]))
        self.cancel_button.grid(row=self.UI_grid["cancel_button"]["row"],
                                column=self.UI_grid["cancel_button"]["column"],
                                sticky=self.UI_grid["cancel_button"]["sticky"],
                                padx=self.UI_grid["cancel_button"]["padx"],
                                pady=self.UI_grid["cancel_button"]["pady"])

        self.df_frame = ttk.Frame(self.root,
                                  width=self.UI_grid["df_frame"]["width"],
                                  height=self.UI_grid["df_frame"]["height"])
        self.df_frame.grid(row=self.UI_grid["df_frame"]["row"],
                           sticky=self.UI_grid["df_frame"]["sticky"])

        self.df_tree = ttk.Treeview(self.df_frame)
        self.vertical_stroll_bar = ttk.Scrollbar(self.df_frame, orient="vertical", command=self.df_tree.yview)
        self.horizontal_stroll_bar = ttk.Scrollbar(self.df_frame, orient="horizontal", command=self.df_tree.xview)
        self.df_tree.configure(yscrollcommand=self.vertical_stroll_bar.set,
                               xscrollcommand=self.horizontal_stroll_bar.set)

        self.log_label = ctk.CTkLabel(self.root,
                                  wraplength=400, # todo fix the text wrapping issue, its already bugging the system when I switched to CTk
                                  justify="left",
                                  height=self.UI_grid["log_label"]["height"],
                                  text=self.UI_grid["log_label"]["text"])
        self.log_label.grid(row=self.UI_grid["log_label"]["row"],
                            padx=self.UI_grid["log_label"]["padx"],
                            sticky=self.UI_grid["log_label"]["sticky"])

        # main loop, only to the end pls
        self.root.mainloop()

    def validate_csv(self, file_path, have_headers=True):
        if not os.path.exists(file_path):
            messagebox.showerror(title=self.error_messages["Invalid File Path"][0],
                                 message=self.error_messages["Invalid File Path"][1])
            self.logger(f"Invalid File Path: '{file_path}'")
            self.run_button.configure(state=ctk.DISABLED)
            return None
        try:
            header = None
            if have_headers:
                header = 'infer'
            df_validated = pd.read_csv(file_path, header=header, encoding='utf-8')
        except UnicodeDecodeError:
            messagebox.showerror(title=self.error_messages["UnicodeDecodeError"][0],
                                 message=self.error_messages["UnicodeDecodeError"][1])
            self.logger(self.error_messages["UnicodeDecodeError"][1])
            self.run_button.configure(state=ctk.DISABLED)
            return
        self.logger(f"File path: '{file_path}'")
        self.run_button.configure(state=ctk.NORMAL)
        self.entry_box.configure(state=ctk.DISABLED)
        return df_validated

    def browse_file(self):
        file_path = fd.askopenfilename(title="Select file", filetypes=(("CSV Files", "*.csv"),))
        self.entry_box.configure(state=ctk.NORMAL)
        self.entry_box.delete(0, ctk.END)
        self.entry_box.insert(0, file_path)
        have_headers = True
        if self.check_headers_state.get() == 0:
            have_headers = False
        elif self.check_headers_state.get() == 1:
            have_headers = True
        self.df_validated = self.validate_csv(file_path, have_headers)
        self.display_df(self.df_validated)

    def display_df(self, df_to_display=None):
        if df_to_display is None:
            df_to_display = self.df_validated
        self.df_tree.delete(*self.df_tree.get_children())
        self.df_tree["columns"] = list(df_to_display.columns)
        self.df_tree["show"] = "headings"  # Hide the first empty column
        for col in df_to_display.columns:
            self.df_tree.heading(col, text=col)
            self.df_tree.column(col, anchor=ctk.CENTER)
        for index, row in df_to_display.iterrows():
            self.df_tree.insert("", "end", values=list(row))
        self.logger("CSV loaded.")
        # display table
        self.df_tree.grid(row=self.UI_grid["tree"]["row"],
                          column=self.UI_grid["tree"]["column"],
                          sticky=self.UI_grid["tree"]["sticky"])
        self.vertical_stroll_bar.grid(row=self.UI_grid["vertical_stroll_bar"]["row"],
                                      column=self.UI_grid["vertical_stroll_bar"]["column"],
                                      sticky=self.UI_grid["vertical_stroll_bar"]["sticky"])
        self.horizontal_stroll_bar.grid(row=self.UI_grid["horizontal_stroll_bar"]["row"],
                                        column=self.UI_grid["horizontal_stroll_bar"]["column"],
                                        sticky=self.UI_grid["horizontal_stroll_bar"]["sticky"])
        self.root.pack_propagate(False) # todo fix the propagation properties

    def clean_df(self, df_to_clean):
        df_cleaned = df_to_clean.apply(lambda col: col.dropna().reset_index(drop=True))
        self.logger(f"Removed NaN rows.")
        max_len = df_cleaned.apply(len).max()
        df_cleaned = df_cleaned.apply(lambda col: col.reindex(range(max_len)))
        return df_cleaned

    def get_expected_output(self, df_to_read):
        number_in_column = df_to_read.notna().sum()
        expected_combinations = number_in_column.prod()
        self.logger(f"{expected_combinations} rows expected.")
        return expected_combinations

    def exceeds_output_limit(self, df_to_read):
        if self.get_expected_output(df_to_read) > self.output_limit:
            return True
        return False

    def permutate_and_combine(self, df_input):
        self.log = ""
        df_cleaned = pd.DataFrame()
        try:
            df_cleaned = self.clean_df(df_input)
        except AttributeError:
            messagebox.showerror(title=self.error_messages["AttributeError"][0],
                                 message=self.error_messages["AttributeError"][1])
        if self.exceeds_output_limit(df_cleaned):
            self.logger(self.error_messages["LimitError"][1])
            messagebox.showwarning(title=self.error_messages["LimitError"][0],
                                   message=self.error_messages["LimitError"][1])
            return
        combinations_generator = itertools.product(*[df_cleaned[col] for col in df_cleaned.columns])
        df_output = pd.DataFrame(combinations_generator, columns=df_cleaned.columns)
        df_output = df_output.dropna()
        self.display_df(df_output)
        self.save(df_output)
        self.logger(f"Processed {df_output.shape[0]} combinations.")
        self.run_button.configure(state=ctk.DISABLED)

    def save(self, df_to_save, check=True):
        file_path = self.entry_box.get()
        temp_path_list = file_path.split(".")
        new_file_path = temp_path_list[0] + "_output" + ".csv"
        if check and os.path.exists(new_file_path): # todo file names can be checked for duplicates
            temp_path_list = new_file_path.split(".")
            new_file_path = temp_path_list[0] + "(1)" + ".csv"
        df_to_save.to_csv(new_file_path, index=False)
        self.logger(f"Data exported to '{new_file_path}'.")

    def logger(self, log_str):
        self.log_label.configure(text=log_str)
        print(log_str)
        self.log += "\n [" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "] " +log_str

    def view_log(self):
        messagebox.showinfo(title="Log", message=self.log)
        print(self.log)

    def close(self):
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    GUI()