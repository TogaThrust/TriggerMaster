# system
import os
import sys
import threading
from datetime import datetime
from typing import Type

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

from global_var import version

# CTk config
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("theme.json") # todo create custom theme, also maybe a house font

# Other files
import global_var

class ErrorHandler:
    def __init__(self, gui):
        self.error_messages = global_var.error_messages
        self.gui = gui

    def raise_question_box(self, error_type: str) -> str:
        user_selection = messagebox.askquestion(title=self.error_messages[error_type][0],
                                                message=self.error_messages[error_type][1],
                                                icon=messagebox.WARNING, type=messagebox.OKCANCEL)
        return user_selection

    def raise_error_box(self, error_type: str, log_str: str | None) -> None:
        messagebox.showerror(title=self.error_messages[error_type][0],
                             message=self.error_messages[error_type][1])
        if log_str is None:
            log_str = self.error_messages[error_type][1]
        self.gui.logger(log_str=log_str)
        return None

class FileHandler:
    def __init__(self, gui):
        self.df_raw = None
        self.df_cleaned = None
        self.gui = gui

    def validate_file_path(self, file_path: str, have_headers: bool | int) -> None:
        if not os.path.exists(path=file_path):
            error_handler.raise_error_box(error_type="Invalid File Path", log_str=f"Invalid File Path: '{file_path}'")
            self.gui.run_button.configure(state=ctk.DISABLED)
            return None
        try:
            header = None
            if have_headers:
                header = 'infer'
            df_validated = pd.read_csv(file_path, dtype=str, header=header, encoding='utf-8')
        except UnicodeDecodeError:
            error_handler.raise_question_box(error_type="UnicodeDecodeError")
            self.gui.run_button.configure(state=ctk.DISABLED)
            return None
        self.gui.logger(f"File path: '{file_path}'")
        self.gui.run_button.configure(state=ctk.NORMAL)
        self.gui.entry_box.configure(state=ctk.DISABLED)
        self.df_raw = df_validated.copy()
        return None

    def clean_raw_df(self) -> Type[AttributeError] | None:
        # df_to_clean = pd.DataFrame()
        try:  # Raise exception when df is empty.
            df_to_clean = self.df_raw.apply(lambda col: col.dropna().reset_index(drop=True))
            self.gui.logger(f"Removed NaN rows.")
            max_len = df_to_clean.apply(len).max()
            df_to_clean = df_to_clean.apply(lambda col: col.reindex(range(max_len)))
        except AttributeError:
            error_handler.raise_error_box(error_type="AttributeError", log_str=None)
            return AttributeError
        if self.gui.have_name_and_code.get():
            df_to_clean = combinations_generator.combine_columns(df_to_clean)
        self.df_cleaned = df_to_clean.replace('%%', np.nan, regex=False)
        return None

    @staticmethod
    def get_new_file_path(entry_box_path: str) -> str:
        temp_path_list = entry_box_path.split(".")
        new_file_path = temp_path_list[0] + "_output" + ".csv"
        while os.path.exists(new_file_path):  # fixme file names checked for duplicates not very profound
            temp_path_list = new_file_path.split(".")
            new_file_path = temp_path_list[0] + "(1)" + ".csv"
        return new_file_path

class CombinationsGenerator:
    def __init__(self, gui):
        self.gui = gui
        self.process_thread = None
        self.stop_event = threading.Event()
        self.expected_output = 0
        self.total_processed = 0
        self.write_path = ""

    @staticmethod
    def get_expected_output(df: pd.DataFrame) -> int:
        number_in_column = df.notna().sum()
        expected_combinations = number_in_column.prod()
        return expected_combinations

    # Raise exception when data to process is too large.
    def limit_check(self, df: pd.DataFrame, warning_limit: int = 1_000_000) -> tuple[int, str | None]:
        expected_outputs = self.get_expected_output(df)
        if expected_outputs > warning_limit:
            return expected_outputs, error_handler.raise_question_box(error_type="LimitWarning")
        return expected_outputs, None

    @ staticmethod
    def combine_columns(df: pd.DataFrame) -> pd.DataFrame:
        concatenated_columns = []
        for i in range(0, len(df.columns), 2):
            # Concatenate two columns
            if i + 1 < len(df.columns):
                combined = df.iloc[:, i].fillna('') + '%%' + df.iloc[:, i + 1].fillna('')
            else:
                combined = df.iloc[:, i].fillna('')  # Handle odd number of columns
            concatenated_columns.append(combined)
        df_combined = pd.concat(concatenated_columns, axis=1)
        return df_combined

    @ staticmethod
    def split_columns(df: pd.DataFrame) -> pd.DataFrame | AttributeError:
        df_split = pd.DataFrame()
        try:
            for col in df.columns:
                split_cols = df[col].str.split('%%', expand=True)
                split_cols.columns = [f"{col}_{i + 1}" for i in range(split_cols.shape[1])]
                df_split = pd.concat([df_split, split_cols], axis=1)
        except AttributeError:
            return AttributeError
        return df_split

    @ staticmethod
    def chunk_generator(df: pd.DataFrame, chunk_size: int) -> list | None:
        generator = itertools.product(*[df.df_cleaned[col] for col in df.df_cleaned.columns])
        chunk = []
        for i, combination in enumerate(generator):
            chunk.append(combination)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk
        return None

    def write_chunk(self, chunk: list, file_path: str, write_header: bool) -> None | str:
        df_output = pd.DataFrame(chunk, columns=file_handler.df_cleaned.columns)
        df_output.dropna(inplace=True)
        if df_output.empty:
            return
        if self.gui.have_name_and_code.get():
            df_output = CombinationsGenerator.split_columns(df_output)
            if df_output == AttributeError:
                return "RuntimeError"
            df_output.columns = file_handler.df_raw.columns
        # fixme chinese char breaks when writing from df to csv
        file_lock = threading.Lock()
        with file_lock:
            df_output.to_csv(file_path, index=False, header=write_header, mode='a')
        self.total_processed += df_output.shape[0]
        percent_complete = round((self.total_processed / self.expected_output) * 100, 2)
        self.gui.log_label.configure(text=f"Loading... {percent_complete}% complete.")
        if percent_complete == 100: # stop the main process cleanly
            self.stop_event.set()
            if self.process_thread.is_alive():
                self.process_thread.join()
        return

    # fixme find out where the extra data coming from, and how to exit the main program when finished.
    def thread_handler(self, df: pd.DataFrame , chunk_size: int = 100_000) -> None:
        self.gui.logger(log_str=f"Process to create new combinations has started.")
        self.total_processed = 0
        max_threads = 4
        threads = []
        for i, chunk in enumerate(self.chunk_generator(df, chunk_size=chunk_size)):
            print(f"chunk size: {len(chunk)}") # todo remove debug line
            write_header = (i == 0)
            thread = threading.Thread(target=self.write_chunk, args=(chunk, write_header), daemon=True)
            threads.append(thread)
            self.stop_event.clear()
            thread.start()
            if len(threads) >= max_threads:
                for t in threads:
                    t.join()  # Wait for current threads to finish
                threads = []  # Clear the list for the next batch
        for t in threads:
            t.join()
        self.gui.logger(f"Generated {combinations_generator.total_processed} combinations.")
        self.gui.logger(f"Data exported to '{combinations_generator.write_path}'.")
        self.gui.run_button.configure(state=ctk.DISABLED)
        return None

class GUI:
    def __init__(self):
        # objects callable
        self.error_handler = None
        self.combinations_generator = None
        self.file_handler = None

        # libraries
        self.error_messages = global_var.error_messages
        self.UI_grid = global_var.UI_grid
        self.log = ""

        # UI main
        self.root = ctk.CTk()
        self.root.title(f"Trigger Master {version}")
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

        # Output frame and its widgets
        self.output_frame = ctk.CTkFrame(self.root)
        self.output_frame.grid(row=self.UI_grid["output_frame"]["config"]["row"],
                               sticky=self.UI_grid["output_frame"]["config"]["sticky"],
                               padx=self.UI_grid["output_frame"]["config"]["padx"],
                               pady=self.UI_grid["output_frame"]["config"]["pady"])

        self.run_button = (ctk.CTkButton(self.output_frame,
                                         text=self.UI_grid["output_frame"]["run_button"]["text"],
                                         command=self.main_task))
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

        # Log frame and its widgets
        self.log_frame = ctk.CTkFrame(self.root)
        self.log_frame.grid(row=self.UI_grid["log_frame"]["config"]["row"],
                            sticky=self.UI_grid["log_frame"]["config"]["sticky"],
                            padx=self.UI_grid["log_frame"]["config"]["padx"],
                            pady=self.UI_grid["log_frame"]["config"]["pady"])

        self.log_label = ctk.CTkLabel(self.log_frame, text=self.UI_grid["log_frame"]["log_label"]["text"])
        self.log_label.grid(row=self.UI_grid["log_frame"]["log_label"]["row"],
                            padx=self.UI_grid["log_frame"]["log_label"]["padx"],
                            sticky=self.UI_grid["log_frame"]["log_label"]["sticky"])
        self.log_frame.configure(height=self.log_label.winfo_reqheight())
        self.log_frame.grid_propagate(False)

        # main loop, only to the end pls
        self.root.mainloop()

    def set_file_handler(self, main_file_handler):
        self.file_handler = main_file_handler

    def set_combinations_generator(self, main_combinations_generator):
        self.combinations_generator = main_combinations_generator

    def display_df(self, df_to_display=None):
        if df_to_display is None:
            df_to_display = self.file_handler.df_raw
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

    def main_task(self): # Basically other important functions other than main task.
        self.log = ""
        self.file_handler.clean_raw_df()
        expected_combinations, error_str = self.combinations_generator.limit_check(df=self.file_handler.df_cleaned)
        if error_str:
            self.logger(self.error_messages["LimitWarning"][2])
            if error_str == "cancel":
                return error_str
        self.logger(f"{self.combinations_generator.expected_output} rows expected.")
        self.combinations_generator.write_path = FileHandler.get_new_file_path(self.entry_box.get())
        # Create new thread to handle back end processing.
        process_thread = threading.Thread(target=self.combinations_generator.thread_handler, daemon=True)
        process_thread.start()
        return None

    def logger(self, log_str: str):
        self.log_label.configure(text=log_str)
        print(log_str)
        self.log += "[" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "] " + log_str + "\n"

    def browse_file(self):
        file_path = fd.askopenfilename(title="Select file", filetypes=(("CSV Files", "*.csv"),))
        self.entry_box.configure(state=ctk.NORMAL)
        self.entry_box.delete(0, ctk.END)
        self.entry_box.insert(0, file_path)
        self.file_handler.validate_file_path(file_path, self.have_headers.get())
        self.display_df()
        self.logger(f"CSV loaded: {file_path}")

    def view_log(self):
        if self.log == "":
            self.log = "Run program to view log."
        messagebox.showinfo(title="Log", message=self.log)
        print(self.log)

    def close(self):
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    main_gui = GUI()
    error_handler = ErrorHandler(main_gui)
    combinations_generator = CombinationsGenerator(main_gui)
    file_handler = FileHandler(main_gui)
    main_gui.set_file_handler(file_handler)
    main_gui.set_combinations_generator(combinations_generator)