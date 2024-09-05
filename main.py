# system
import os
import sys
from datetime import datetime
import threading

# standard libraries
import pandas as pd
import numpy as np
import itertools

# tkinter
import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import ttk # treeview not implemented in CTk
from tkinter import filedialog as fd
from tkinter import messagebox

# CTk config
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("theme.json") # todo create custom theme, also maybe a house font

# Other files
import global_var

class GUI:
    def __init__(self):
        # Var declarations
        self.df_validated = None
        self.log = ""
        self.warning_limit = 1_000_000
        self.error_messages = global_var.error_messages
        self.UI_grid = global_var.UI_grid
        self.num_threads = os.cpu_count()
        # UI main
        self.root = ctk.CTk()
        self.root.title("Trigger Duplicator")
        self.root.resizable(False, False)

        # Input frame and its widgets
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.grid(row=self.UI_grid["input_frame"]["config"]["row"],
                              sticky=self.UI_grid["input_frame"]["config"]["sticky"],
                              padx=self.UI_grid["input_frame"]["config"]["padx"],
                              pady=self.UI_grid["input_frame"]["config"]["pady"])

        self.entry_box = ctk.CTkEntry(self.input_frame)
        self.entry_box.grid(row=self.UI_grid["input_frame"]["entry_box"]["row"],
                            column=self.UI_grid["input_frame"]["entry_box"]["column"],
                            sticky=self.UI_grid["input_frame"]["entry_box"]["sticky"],
                            padx=self.UI_grid["input_frame"]["entry_box"]["padx"],
                            pady=self.UI_grid["input_frame"]["entry_box"]["pady"])
        self.entry_box.insert(0, "Choose a CSV file...")

        self.browse_button = (ctk.CTkButton(self.input_frame,
                                            text=self.UI_grid["input_frame"]["browse_button"]["text"],
                                            command=self.browse_file))
        self.browse_button.grid(row=self.UI_grid["input_frame"]["browse_button"]["row"],
                                column=self.UI_grid["input_frame"]["browse_button"]["column"],
                                sticky=self.UI_grid["input_frame"]["browse_button"]["sticky"],
                                padx=self.UI_grid["input_frame"]["browse_button"]["padx"],
                                pady=self.UI_grid["input_frame"]["browse_button"]["pady"])

        self.have_headers = ctk.IntVar()
        self.check_headers = ctk.CTkCheckBox(self.input_frame,
                                             variable=self.have_headers,
                                             text=self.UI_grid["input_frame"]["check_headers"]["text"])
        self.check_headers.grid(row=self.UI_grid["input_frame"]["check_headers"]["row"],
                                padx=self.UI_grid["input_frame"]["check_headers"]["padx"],
                                pady=self.UI_grid["input_frame"]["check_headers"]["pady"],
                                sticky=self.UI_grid["input_frame"]["check_headers"]["sticky"])
        self.check_headers.toggle()

        self.have_name_and_code = ctk.IntVar()
        self.check_code_and_name = ctk.CTkCheckBox(self.input_frame,
                                                  variable=self.have_name_and_code,
                                                  text=self.UI_grid["input_frame"]["check_code_and_name"]["text"])
        self.check_code_and_name.grid(row=self.UI_grid["input_frame"]["check_code_and_name"]["row"],
                                      padx=self.UI_grid["input_frame"]["check_code_and_name"]["padx"],
                                      pady=self.UI_grid["input_frame"]["check_code_and_name"]["pady"],
                                      sticky=self.UI_grid["input_frame"]["check_code_and_name"]["sticky"])
        self.check_code_and_name.toggle()

        # Date frame and its widgets
        self.date_frame = ctk.CTkFrame(self.root)
        self.date_frame.grid(row=self.UI_grid["date_frame"]["config"]["row"],
                             sticky=self.UI_grid["date_frame"]["config"]["sticky"],
                             padx=self.UI_grid["date_frame"]["config"]["padx"],
                             pady=self.UI_grid["date_frame"]["config"]["pady"])

        self.date_format_label = ctk.CTkLabel(self.date_frame,
                                              text=self.UI_grid["date_frame"]["date_format_label"]["text"])
        self.date_format_label.grid(row=self.UI_grid["date_frame"]["date_format_label"]["row"],
                                    column=self.UI_grid["date_frame"]["date_format_label"]["column"],
                                    padx=self.UI_grid["date_frame"]["date_format_label"]["padx"],
                                    pady=self.UI_grid["date_frame"]["date_format_label"]["pady"],
                                    sticky=self.UI_grid["date_frame"]["date_format_label"]["sticky"])

        self.date_entry_box = ctk.CTkEntry(self.date_frame)
        self.date_entry_box.grid(row=self.UI_grid["date_frame"]["date_entry_box"]["row"],
                                 column=self.UI_grid["date_frame"]["date_entry_box"]["column"],
                                 sticky=self.UI_grid["date_frame"]["date_entry_box"]["sticky"],
                                 padx=self.UI_grid["date_frame"]["date_entry_box"]["padx"],
                                 pady=self.UI_grid["date_frame"]["date_entry_box"]["pady"])

        self.date_start_label = ctk.CTkLabel(self.date_frame,
                                              text=self.UI_grid["date_frame"]["date_start_label"]["text"])
        self.date_start_label.grid(row=self.UI_grid["date_frame"]["date_start_label"]["row"],
                                   column=self.UI_grid["date_frame"]["date_start_label"]["column"],
                                    padx=self.UI_grid["date_frame"]["date_start_label"]["padx"],
                                    pady=self.UI_grid["date_frame"]["date_start_label"]["pady"],
                                    sticky=self.UI_grid["date_frame"]["date_start_label"]["sticky"])

        self.calendar_start = DateEntry(self.date_frame, date_pattern="yyyy-mm-dd")  # todo date function
        self.calendar_start.grid(row=self.UI_grid["date_frame"]["calendar_start"]["row"],
                                 column=self.UI_grid["date_frame"]["calendar_start"]["column"],
                                 padx=self.UI_grid["date_frame"]["calendar_start"]["padx"],
                                 pady=self.UI_grid["date_frame"]["calendar_start"]["pady"],
                                 sticky=self.UI_grid["date_frame"]["calendar_start"]["sticky"])

        self.date_end_label = ctk.CTkLabel(self.date_frame,
                                           text=self.UI_grid["date_frame"]["date_end_label"]["text"])
        self.date_end_label.grid(row=self.UI_grid["date_frame"]["date_end_label"]["row"],
                                column=self.UI_grid["date_frame"]["date_end_label"]["column"],
                                padx=self.UI_grid["date_frame"]["date_end_label"]["padx"],
                                pady=self.UI_grid["date_frame"]["date_end_label"]["pady"],
                                sticky=self.UI_grid["date_frame"]["date_end_label"]["sticky"])

        self.calendar_end = DateEntry(self.date_frame, date_pattern="yyyy-mm-dd")
        self.calendar_end.grid(row=self.UI_grid["date_frame"]["calendar_end"]["row"],
                               column=self.UI_grid["date_frame"]["calendar_end"]["column"],
                               padx=self.UI_grid["date_frame"]["calendar_end"]["padx"],
                               pady=self.UI_grid["date_frame"]["calendar_end"]["pady"],
                               sticky=self.UI_grid["date_frame"]["calendar_end"]["sticky"])

        # df_frame and its widgets
        self.df_frame = ctk.CTkFrame(self.root)
        self.df_frame.grid(row=self.UI_grid["df_frame"]["config"]["row"],
                           sticky=self.UI_grid["df_frame"]["config"]["sticky"],
                           padx=self.UI_grid["df_frame"]["config"]["padx"],
                           pady=self.UI_grid["df_frame"]["config"]["pady"])
        self.df_frame.grid_propagate(False)

        self.df_tree = ttk.Treeview(self.df_frame)
        self.vertical_stroll_bar = ctk.CTkScrollbar(self.df_frame, orientation="vertical",
                                                    command=self.df_tree.yview)
        self.horizontal_stroll_bar = ctk.CTkScrollbar(self.df_frame, orientation="horizontal",
                                                      command=self.df_tree.xview)
        self.df_tree.configure(yscrollcommand=self.vertical_stroll_bar.set,
                               xscrollcommand=self.horizontal_stroll_bar.set)

        # fixme the text wrapping issue, its already bugging the system when I switched to CTk
        self.log_label = ctk.CTkLabel(self.df_frame, wraplength=400, justify="left",
                                      text=self.UI_grid["df_frame"]["log_label"]["text"])
        self.log_label.grid(row=self.UI_grid["df_frame"]["log_label"]["row"],
                            padx=self.UI_grid["df_frame"]["log_label"]["padx"],
                            sticky=self.UI_grid["df_frame"]["log_label"]["sticky"])

        # Output frame and its widgets
        self.output_frame = ctk.CTkFrame(self.root)
        self.output_frame.grid(row=self.UI_grid["output_frame"]["config"]["row"],
                               sticky=self.UI_grid["output_frame"]["config"]["sticky"],
                               padx=self.UI_grid["output_frame"]["config"]["padx"],
                               pady=self.UI_grid["output_frame"]["config"]["pady"])

        self.run_button = (ctk.CTkButton(self.output_frame,
                                         text=self.UI_grid["output_frame"]["run_button"]["text"],
                                         command=lambda: self.main_task_wrapper(df_input=self.df_validated)))
        self.run_button.grid(row=self.UI_grid["output_frame"]["run_button"]["row"],
                             column=self.UI_grid["output_frame"]["run_button"]["column"],
                             sticky=self.UI_grid["output_frame"]["run_button"]["sticky"],
                             padx=self.UI_grid["output_frame"]["run_button"]["padx"],
                             pady=self.UI_grid["output_frame"]["run_button"]["pady"])
        self.run_button.configure(state=ctk.DISABLED)

        self.view_log_button = (ctk.CTkButton(self.output_frame,
                                              text=self.UI_grid["output_frame"]["view_log_button"]["text"],
                                              command=self.view_log))
        self.view_log_button.grid(row=self.UI_grid["output_frame"]["view_log_button"]["row"],
                                  column=self.UI_grid["output_frame"]["view_log_button"]["column"],
                                  sticky=self.UI_grid["output_frame"]["view_log_button"]["sticky"],
                                  padx=self.UI_grid["output_frame"]["view_log_button"]["padx"],
                                  pady=self.UI_grid["output_frame"]["view_log_button"]["pady"])

        self.cancel_button = (ctk.CTkButton(self.output_frame,
                                            text=self.UI_grid["output_frame"]["cancel_button"]["text"],
                                            command=self.close))
        self.cancel_button.grid(row=self.UI_grid["output_frame"]["cancel_button"]["row"],
                                column=self.UI_grid["output_frame"]["cancel_button"]["column"],
                                sticky=self.UI_grid["output_frame"]["cancel_button"]["sticky"],
                                padx=self.UI_grid["output_frame"]["cancel_button"]["padx"],
                                pady=self.UI_grid["output_frame"]["cancel_button"]["pady"])

        # main loop, only to the end pls
        self.root.mainloop()

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
        self.logger("CSV loaded.")

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
        # display table
        self.df_tree.grid(row=self.UI_grid["df_frame"]["tree"]["row"],
                          column=self.UI_grid["df_frame"]["tree"]["column"],
                          sticky=self.UI_grid["df_frame"]["tree"]["sticky"],
                          padx=self.UI_grid["df_frame"]["tree"]["padx"],
                          pady=self.UI_grid["df_frame"]["tree"]["pady"])
        self.vertical_stroll_bar.grid(row=self.UI_grid["df_frame"]["vertical_stroll_bar"]["row"],
                                      column=self.UI_grid["df_frame"]["vertical_stroll_bar"]["column"],
                                      sticky=self.UI_grid["df_frame"]["vertical_stroll_bar"]["sticky"])
        self.horizontal_stroll_bar.grid(row=self.UI_grid["df_frame"]["horizontal_stroll_bar"]["row"],
                                        column=self.UI_grid["df_frame"]["horizontal_stroll_bar"]["column"],
                                        sticky=self.UI_grid["df_frame"]["horizontal_stroll_bar"]["sticky"])
        self.df_frame.grid_rowconfigure(0, weight=1)
        self.df_frame.grid_columnconfigure(0, weight=1)

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
        if self.get_expected_output(df_to_read) > self.warning_limit:
            return True
        return False

    @ staticmethod
    def combine_columns(df_to_combine):
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
        return df_combined

    def split_columns(self, df_to_split):
        result_df = pd.DataFrame()
        try:
            for col in df_to_split.columns:
                split_cols = df_to_split[col].str.split('%%', expand=True)
                split_cols.columns = [f"{col}_{i + 1}" for i in range(split_cols.shape[1])]
                result_df = pd.concat([result_df, split_cols], axis=1)
        except AttributeError:
            messagebox.showerror(title=self.error_messages["RuntimeError"][0],
                                 message=self.error_messages["RuntimeError"][1])
            self.logger(self.error_messages["RuntimeError"][1])
        return result_df

    def show_loading_info(self, process_thread): # todo loading screen?
        pass

    @staticmethod
    def chunked_generator(generator, chunk_size):
        chunk = []
        for i, combination in enumerate(generator):
            chunk.append(combination)
            if (i + 1) % chunk_size == 0:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

    def permutate_and_combine(self, target_df, chunk_size=100_000): # The actual main task that is called
        file_path = self.get_new_file_path()
        combinations_generator = itertools.product(*[target_df[col] for col in target_df.columns])
        self.logger(f"Process started.")
        total_processed = 0
        df_output = pd.DataFrame()
        for i, chunk in enumerate(self.chunked_generator(generator=combinations_generator, chunk_size=chunk_size)):
            write_header = (i == 0)
            df_output = pd.DataFrame(chunk, columns=target_df.columns)
            df_output.dropna(inplace=True)
            if df_output.empty:
                continue
            if self.have_name_and_code.get():
                df_output = self.split_columns(df_output)
                df_output.columns = self.df_validated.columns
            df_output = df_output.dropna()
            self.save(df_output, file_path, write_header)
            total_processed += df_output.shape[0]
            self.log_label.configure(text=f"Generated {total_processed} combinations.")
        self.display_df(df_output)
        self.logger(f"Processed total of {total_processed} combinations.")
        self.logger(f"Data exported to '{file_path}'.")
        self.run_button.configure(state=ctk.DISABLED)

    def main_task_wrapper(self, df_input): # Basically other important functions other than main task.
        self.log = ""
        df_cleaned = pd.DataFrame()
        try:  # Raise exception when df is empty.
            df_cleaned = self.clean_df(df_input)
        except AttributeError:
            messagebox.showerror(title=self.error_messages["AttributeError"][0],
                                 message=self.error_messages["AttributeError"][1])
        if self.have_name_and_code.get():
            df_cleaned = self.combine_columns(df_cleaned)
        df_cleaned = df_cleaned.replace('%%', np.nan, regex=False)
        print(df_cleaned)
        if self.exceeds_output_limit(df_cleaned):  # Raise exception when data to process is too large.
            self.logger(self.error_messages["LimitWarning"][2])
            selected_button = messagebox.askquestion(title=self.error_messages["LimitWarning"][0],
                                                     message=self.error_messages["LimitWarning"][1],
                                                     icon=messagebox.WARNING, type=messagebox.OKCANCEL)
            if selected_button == "cancel":
                self.logger("User cancelled.")
                return
        process_thread = threading.Thread(target=lambda: self.permutate_and_combine(df_cleaned))
        process_thread.start()
        self.show_loading_info(process_thread)

    def get_new_file_path(self):
        file_path = self.entry_box.get()
        temp_path_list = file_path.split(".")
        new_file_path = temp_path_list[0] + "_output" + ".csv"
        while os.path.exists(new_file_path):  # fixme file names checked for duplicates not very profound
            temp_path_list = new_file_path.split(".")
            new_file_path = temp_path_list[0] + "(1)" + ".csv"
        return new_file_path

    @staticmethod
    def save(df_to_save, file_path, headers):
        df_to_save.to_csv(file_path, index=False, header=headers, mode='a', encoding='utf-8')

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