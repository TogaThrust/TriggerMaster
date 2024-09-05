# system
import os
import sys
from datetime import datetime

# standard libraries
import pandas as pd
import numpy as np
import itertools

# tkinter
import customtkinter as ctk
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("theme.json") # todo create custom theme
from tkcalendar import DateEntry
from tkinter import ttk # treeview not implemented in CTk
from tkinter import filedialog as fd
from tkinter import messagebox

# Other files
import global_var

class GUI:
    def __init__(self):
        self.chunk_size = 2
        self.df_validated = None
        self.log = ""
        self.output_limit = 100_000_000
        self.UI_grid = global_var.UI_grid
        self.error_messages = global_var.error_messages
        # UI main
        self.root = ctk.CTk()
        self.root.title("Trigger Duplicator")
        self.root.geometry("400x500") # fixme explore using pack to limit expansion
        # Widgets on initialisation
        self.input_frame = ctk.CTkFrame(self.root, width=self.UI_grid["input_frame"]["width"])
        self.input_frame.grid(row=self.UI_grid["input_frame"]["row"],
                              sticky=self.UI_grid["input_frame"]["sticky"])

        self.date_frame = ctk.CTkFrame(self.root, width=self.UI_grid["date_frame"]["width"])
        self.date_frame.grid(row=self.UI_grid["date_frame"]["row"],
                              sticky=self.UI_grid["date_frame"]["sticky"])

        self.entry_box = ctk.CTkEntry(self.input_frame, width=self.UI_grid["entry_box"]["width"])
        self.entry_box.grid(row=self.UI_grid["entry_box"]["row"],
                            column=self.UI_grid["entry_box"]["column"],
                            sticky=self.UI_grid["entry_box"]["sticky"],
                            padx=self.UI_grid["entry_box"]["padx"],
                            pady=self.UI_grid["entry_box"]["pady"])
        self.entry_box.insert(0, "Choose a CSV file...")

        self.date_label = ctk.CTkLabel(self.date_frame,
                                  height=self.UI_grid["date_label"]["height"],
                                  text=self.UI_grid["date_label"]["text"])
        self.date_label.grid(row=self.UI_grid["date_label"]["row"],
                             padx=self.UI_grid["date_label"]["padx"],
                             pady=self.UI_grid["date_label"]["pady"],
                             sticky=self.UI_grid["date_label"]["sticky"])

        self.date_entry_box = ctk.CTkEntry(self.date_frame, width=self.UI_grid["date_entry_box"]["width"])
        self.date_entry_box.grid(row=self.UI_grid["date_entry_box"]["row"],
                            column=self.UI_grid["date_entry_box"]["column"],
                            sticky=self.UI_grid["date_entry_box"]["sticky"],
                            padx=self.UI_grid["date_entry_box"]["padx"],
                            pady=self.UI_grid["date_entry_box"]["pady"])

        self.browse_button = (ctk.CTkButton(self.input_frame,
                                        text=self.UI_grid["browse_button"]["text"],
                                        width=self.UI_grid["browse_button"]["width"],
                                        command=self.browse_file))
        self.browse_button.grid(row=self.UI_grid["browse_button"]["row"],
                                column=self.UI_grid["browse_button"]["column"],
                                sticky=self.UI_grid["browse_button"]["sticky"],
                                padx=self.UI_grid["browse_button"]["padx"],
                                pady=self.UI_grid["browse_button"]["pady"])

        self.have_headers = ctk.IntVar()
        self.check_headers = ctk.CTkCheckBox(self.input_frame,
                                             variable=self.have_headers,
                                             text=self.UI_grid["check_headers"]["text"])
        self.check_headers.grid(row=self.UI_grid["check_headers"]["row"],
                                column=self.UI_grid["check_headers"]["column"],
                                padx=self.UI_grid["check_headers"]["padx"],
                                pady=self.UI_grid["check_headers"]["pady"],
                                sticky=self.UI_grid["check_headers"]["sticky"])
        self.check_headers.toggle()

        self.have_name_and_code = ctk.IntVar()
        self.check_code_and_name = ctk.CTkCheckBox(self.input_frame,
                                                  variable=self.have_name_and_code,
                                                  text=self.UI_grid["check_code_and_name"]["text"])
        self.check_code_and_name.grid(row=self.UI_grid["check_code_and_name"]["row"],
                                      column=self.UI_grid["check_code_and_name"]["column"],
                                      padx=self.UI_grid["check_code_and_name"]["padx"],
                                      pady=self.UI_grid["check_code_and_name"]["pady"],
                                      sticky=self.UI_grid["check_code_and_name"]["sticky"])
        self.check_code_and_name.toggle()

        calendar = DateEntry(self.date_frame, date_pattern="yyyy-mm-dd") # todo Important. Date selector

        self.output_frame = ctk.CTkFrame(self.root, width=self.UI_grid["output_frame"]["width"])
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

        self.df_frame = ctk.CTkFrame(self.root)
        self.df_frame.grid(row=self.UI_grid["df_frame"]["row"],
                           sticky=self.UI_grid["df_frame"]["sticky"])

        self.df_tree = ttk.Treeview(self.df_frame)
        self.vertical_stroll_bar = ctk.CTkScrollbar(self.df_frame, orientation="vertical", command=self.df_tree.yview)
        self.horizontal_stroll_bar = ctk.CTkScrollbar(self.df_frame, orientation="horizontal", command=self.df_tree.xview)
        self.df_tree.configure(yscrollcommand=self.vertical_stroll_bar.set,
                               xscrollcommand=self.horizontal_stroll_bar.set)

        self.log_label = ctk.CTkLabel(self.root,
                                  wraplength=400, # fixme the text wrapping issue, its already bugging the system when I switched to CTk
                                  justify="left",
                                  height=self.UI_grid["log_label"]["height"],
                                  text=self.UI_grid["log_label"]["text"])
        self.log_label.grid(row=self.UI_grid["log_label"]["row"],
                            padx=self.UI_grid["log_label"]["padx"],
                            sticky=self.UI_grid["log_label"]["sticky"])
        self.root.mainloop() # main loop, only to the end pls

    def validate_csv(self, file_path):
        if not os.path.exists(file_path):
            messagebox.showerror(title=self.error_messages["Invalid File Path"][0],
                                 message=self.error_messages["Invalid File Path"][1])
            self.logger(f"Invalid File Path: '{file_path}'")
            self.run_button.configure(state=ctk.DISABLED)
            return None
        try:
            header = None
            if self.have_headers.get():
                header = 'infer'
            df_validated = pd.read_csv(file_path, dtype=str, header=header, encoding='utf-8')
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

        self.df_validated = self.validate_csv(file_path)
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
        self.df_frame.grid_rowconfigure(0, weight=1)
        self.df_frame.grid_columnconfigure(0, weight=1)
        self.df_frame.configure(width=self.UI_grid["df_frame"]["width"], height=self.UI_grid["df_frame"]["height"])

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

    def combine_columns(self, df_to_combine):
        concatenated_columns = []
        for i in range(0, len(df_to_combine.columns), 2):
            # Concatenate two columns
            if i + 1 < len(df_to_combine.columns):
                combined = df_to_combine.iloc[:, i].fillna('') + '%%' + df_to_combine.iloc[:, i + 1].fillna('')
            else:
                combined = df_to_combine.iloc[:, i].fillna('')  # Handle odd number of columns
            concatenated_columns.append(combined)
        print(concatenated_columns)
        df_combined = pd.concat(concatenated_columns, axis=1)
        self.display_df(df_combined)
        return df_combined

    @staticmethod
    def split_columns(df_to_split):
        result_df = pd.DataFrame()
        for col in df_to_split.columns:
            split_cols = df_to_split[col].str.split('%%', expand=True)
            split_cols.columns = [f"{col}_{i+1}" for i in range(split_cols.shape[1])]
            result_df = pd.concat([result_df, split_cols], axis=1)
        return result_df

    def permutate_and_combine(self, df_input):
        self.log = ""
        df_cleaned = pd.DataFrame()
        try: # Raise exception when df is empty.
            df_cleaned = self.clean_df(df_input)
        except AttributeError:
            messagebox.showerror(title=self.error_messages["AttributeError"][0],
                                 message=self.error_messages["AttributeError"][1])
        if self.have_name_and_code.get():
            df_cleaned = self.combine_columns(df_cleaned)
        df_cleaned = df_cleaned.replace('%%', np.nan, regex=False)
        combinations_generator = itertools.product(*[df_cleaned[col] for col in df_cleaned.columns])
        if self.exceeds_output_limit(df_cleaned): # Raise exception when data to process is too large.
            self.logger(self.error_messages["LimitError"][1])
            messagebox.showwarning(title=self.error_messages["LimitError"][0],
                                   message=self.error_messages["LimitError"][1])
            return
        df_output = pd.DataFrame(combinations_generator, columns=df_cleaned.columns)
        if self.have_name_and_code.get():
            df_output = self.split_columns(df_output)
            df_output.columns = self.df_validated.columns
        df_output = df_output.dropna()
        self.display_df(df_output)
        self.save(df_output)
        self.logger(f"Processed {df_output.shape[0]} combinations.")
        self.run_button.configure(state=ctk.DISABLED)

    def save(self, df_to_save, check=True):
        file_path = self.entry_box.get()
        temp_path_list = file_path.split(".")
        new_file_path = temp_path_list[0] + "_output" + ".csv"
        if check and os.path.exists(new_file_path): # fixme file names checked for duplicates not very profound
            temp_path_list = new_file_path.split(".")
            new_file_path = temp_path_list[0] + "(1)" + ".csv"
        df_to_save.to_csv(new_file_path, index=False)
        self.logger(f"Data exported to '{new_file_path}'.")

    def logger(self, log_str):
        self.log_label.configure(text=log_str)
        print(log_str)
        self.log += "[" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "] " + log_str + "\n"

    def view_log(self):
        messagebox.showinfo(title="Log", message=self.log)
        print(self.log)

    def close(self):
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    GUI()