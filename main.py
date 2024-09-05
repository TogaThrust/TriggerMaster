# system
import sys
from datetime import datetime
import threading
from typing import Type

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
from lib.gui_config import ui_grid
from lib.Handlers.ErrorHandler import ErrorHandler
from lib.Handlers.FileHandler import FileHandler
from lib.Engine.CombinationsGenerator import CombinationsGenerator

class GUI:
    def __init__(self):
        self.combinations_generator = CombinationsGenerator(ErrorHandler(self.logger))
        self.file_handler = FileHandler(ErrorHandler(self.logger))
        # libraries
        self.ui_grid = ui_grid
        self.log = ""

        # UI main
        self.root = ctk.CTk()
        self.root.title(f"Trigger Master")
        self.root.resizable(False, False)

        # Input frame and its widgets
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.grid(row=self.ui_grid["input_frame"]["config"]["row"],
                              sticky=self.ui_grid["input_frame"]["config"]["sticky"],
                              padx=self.ui_grid["input_frame"]["config"]["padx"],
                              pady=self.ui_grid["input_frame"]["config"]["pady"])

        self.entry_box = ctk.CTkEntry(self.input_frame)
        self.entry_box.grid(row=self.ui_grid["input_frame"]["entry_box"]["row"],
                            column=self.ui_grid["input_frame"]["entry_box"]["column"],
                            sticky=self.ui_grid["input_frame"]["entry_box"]["sticky"],
                            padx=self.ui_grid["input_frame"]["entry_box"]["padx"],
                            pady=self.ui_grid["input_frame"]["entry_box"]["pady"])
        self.entry_box.insert(0, "Choose a CSV file...")

        self.browse_button = (ctk.CTkButton(self.input_frame,
                                            text=self.ui_grid["input_frame"]["browse_button"]["text"],
                                            command=self.browse_file))
        self.browse_button.grid(row=self.ui_grid["input_frame"]["browse_button"]["row"],
                                column=self.ui_grid["input_frame"]["browse_button"]["column"],
                                sticky=self.ui_grid["input_frame"]["browse_button"]["sticky"],
                                padx=self.ui_grid["input_frame"]["browse_button"]["padx"],
                                pady=self.ui_grid["input_frame"]["browse_button"]["pady"])

        self.have_headers = ctk.IntVar()
        self.check_headers = ctk.CTkCheckBox(self.input_frame,
                                             variable=self.have_headers,
                                             text=self.ui_grid["input_frame"]["check_headers"]["text"])
        self.check_headers.grid(row=self.ui_grid["input_frame"]["check_headers"]["row"],
                                padx=self.ui_grid["input_frame"]["check_headers"]["padx"],
                                pady=self.ui_grid["input_frame"]["check_headers"]["pady"],
                                sticky=self.ui_grid["input_frame"]["check_headers"]["sticky"])
        self.check_headers.toggle()

        self.have_name_and_code = ctk.IntVar()
        self.check_code_and_name = ctk.CTkCheckBox(self.input_frame,
                                                  variable=self.have_name_and_code,
                                                  text=self.ui_grid["input_frame"]["check_code_and_name"]["text"])
        self.check_code_and_name.grid(row=self.ui_grid["input_frame"]["check_code_and_name"]["row"],
                                      padx=self.ui_grid["input_frame"]["check_code_and_name"]["padx"],
                                      pady=self.ui_grid["input_frame"]["check_code_and_name"]["pady"],
                                      sticky=self.ui_grid["input_frame"]["check_code_and_name"]["sticky"])
        self.check_code_and_name.toggle()

        # Date frame and its widgets
        self.date_frame = ctk.CTkFrame(self.root)
        self.date_frame.grid(row=self.ui_grid["date_frame"]["config"]["row"],
                             sticky=self.ui_grid["date_frame"]["config"]["sticky"],
                             padx=self.ui_grid["date_frame"]["config"]["padx"],
                             pady=self.ui_grid["date_frame"]["config"]["pady"])

        self.date_format_label = ctk.CTkLabel(self.date_frame,
                                              text=self.ui_grid["date_frame"]["date_format_label"]["text"])
        self.date_format_label.grid(row=self.ui_grid["date_frame"]["date_format_label"]["row"],
                                    column=self.ui_grid["date_frame"]["date_format_label"]["column"],
                                    padx=self.ui_grid["date_frame"]["date_format_label"]["padx"],
                                    pady=self.ui_grid["date_frame"]["date_format_label"]["pady"],
                                    sticky=self.ui_grid["date_frame"]["date_format_label"]["sticky"])

        self.date_entry_box = ctk.CTkEntry(self.date_frame)
        self.date_entry_box.grid(row=self.ui_grid["date_frame"]["date_entry_box"]["row"],
                                 column=self.ui_grid["date_frame"]["date_entry_box"]["column"],
                                 sticky=self.ui_grid["date_frame"]["date_entry_box"]["sticky"],
                                 padx=self.ui_grid["date_frame"]["date_entry_box"]["padx"],
                                 pady=self.ui_grid["date_frame"]["date_entry_box"]["pady"])

        self.date_start_label = ctk.CTkLabel(self.date_frame,
                                              text=self.ui_grid["date_frame"]["date_start_label"]["text"])
        self.date_start_label.grid(row=self.ui_grid["date_frame"]["date_start_label"]["row"],
                                   column=self.ui_grid["date_frame"]["date_start_label"]["column"],
                                    padx=self.ui_grid["date_frame"]["date_start_label"]["padx"],
                                    pady=self.ui_grid["date_frame"]["date_start_label"]["pady"],
                                    sticky=self.ui_grid["date_frame"]["date_start_label"]["sticky"])

        self.calendar_start = DateEntry(self.date_frame, date_pattern="yyyy-mm-dd")  # todo date function
        self.calendar_start.grid(row=self.ui_grid["date_frame"]["calendar_start"]["row"],
                                 column=self.ui_grid["date_frame"]["calendar_start"]["column"],
                                 padx=self.ui_grid["date_frame"]["calendar_start"]["padx"],
                                 pady=self.ui_grid["date_frame"]["calendar_start"]["pady"],
                                 sticky=self.ui_grid["date_frame"]["calendar_start"]["sticky"])

        self.date_end_label = ctk.CTkLabel(self.date_frame,
                                           text=self.ui_grid["date_frame"]["date_end_label"]["text"])
        self.date_end_label.grid(row=self.ui_grid["date_frame"]["date_end_label"]["row"],
                                column=self.ui_grid["date_frame"]["date_end_label"]["column"],
                                padx=self.ui_grid["date_frame"]["date_end_label"]["padx"],
                                pady=self.ui_grid["date_frame"]["date_end_label"]["pady"],
                                sticky=self.ui_grid["date_frame"]["date_end_label"]["sticky"])

        self.calendar_end = DateEntry(self.date_frame, date_pattern="yyyy-mm-dd")
        self.calendar_end.grid(row=self.ui_grid["date_frame"]["calendar_end"]["row"],
                               column=self.ui_grid["date_frame"]["calendar_end"]["column"],
                               padx=self.ui_grid["date_frame"]["calendar_end"]["padx"],
                               pady=self.ui_grid["date_frame"]["calendar_end"]["pady"],
                               sticky=self.ui_grid["date_frame"]["calendar_end"]["sticky"])

        # df_frame and its widgets
        self.df_frame = ctk.CTkFrame(self.root)
        self.df_frame.grid(row=self.ui_grid["df_frame"]["config"]["row"],
                           sticky=self.ui_grid["df_frame"]["config"]["sticky"],
                           padx=self.ui_grid["df_frame"]["config"]["padx"],
                           pady=self.ui_grid["df_frame"]["config"]["pady"])
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
        self.output_frame.grid(row=self.ui_grid["output_frame"]["config"]["row"],
                               sticky=self.ui_grid["output_frame"]["config"]["sticky"],
                               padx=self.ui_grid["output_frame"]["config"]["padx"],
                               pady=self.ui_grid["output_frame"]["config"]["pady"])

        self.run_button = (ctk.CTkButton(self.output_frame,
                                         text=self.ui_grid["output_frame"]["run_button"]["text"],
                                         command=self.main_task))
        self.run_button.grid(row=self.ui_grid["output_frame"]["run_button"]["row"],
                             column=self.ui_grid["output_frame"]["run_button"]["column"],
                             sticky=self.ui_grid["output_frame"]["run_button"]["sticky"],
                             padx=self.ui_grid["output_frame"]["run_button"]["padx"],
                             pady=self.ui_grid["output_frame"]["run_button"]["pady"])
        self.run_button.configure(state=ctk.DISABLED)

        self.view_log_button = (ctk.CTkButton(self.output_frame,
                                              text=self.ui_grid["output_frame"]["view_log_button"]["text"],
                                              command=self.view_log))
        self.view_log_button.grid(row=self.ui_grid["output_frame"]["view_log_button"]["row"],
                                  column=self.ui_grid["output_frame"]["view_log_button"]["column"],
                                  sticky=self.ui_grid["output_frame"]["view_log_button"]["sticky"],
                                  padx=self.ui_grid["output_frame"]["view_log_button"]["padx"],
                                  pady=self.ui_grid["output_frame"]["view_log_button"]["pady"])

        self.cancel_button = (ctk.CTkButton(self.output_frame,
                                            text=self.ui_grid["output_frame"]["cancel_button"]["text"],
                                            command=self.close))
        self.cancel_button.grid(row=self.ui_grid["output_frame"]["cancel_button"]["row"],
                                column=self.ui_grid["output_frame"]["cancel_button"]["column"],
                                sticky=self.ui_grid["output_frame"]["cancel_button"]["sticky"],
                                padx=self.ui_grid["output_frame"]["cancel_button"]["padx"],
                                pady=self.ui_grid["output_frame"]["cancel_button"]["pady"])

        # Log frame and its widgets
        self.log_frame = ctk.CTkFrame(self.root)
        self.log_frame.grid(row=self.ui_grid["log_frame"]["config"]["row"],
                            sticky=self.ui_grid["log_frame"]["config"]["sticky"],
                            padx=self.ui_grid["log_frame"]["config"]["padx"],
                            pady=self.ui_grid["log_frame"]["config"]["pady"])

        self.log_label = ctk.CTkLabel(self.log_frame, text=self.ui_grid["log_frame"]["log_label"]["text"])
        self.log_label.grid(row=self.ui_grid["log_frame"]["log_label"]["row"],
                            padx=self.ui_grid["log_frame"]["log_label"]["padx"],
                            sticky=self.ui_grid["log_frame"]["log_label"]["sticky"])
        self.log_frame.configure(height=self.log_label.winfo_reqheight())
        self.log_frame.grid_propagate(False)

        # main loop, only to the end pls
        self.root.mainloop()

    def display_df(self, df_to_display=None) -> None:
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
        self.df_tree.grid(row=self.ui_grid["df_frame"]["tree"]["row"],
                          column=self.ui_grid["df_frame"]["tree"]["column"],
                          sticky=self.ui_grid["df_frame"]["tree"]["sticky"],
                          padx=self.ui_grid["df_frame"]["tree"]["padx"],
                          pady=self.ui_grid["df_frame"]["tree"]["pady"])
        self.vertical_stroll_bar.grid(row=self.ui_grid["df_frame"]["vertical_stroll_bar"]["row"],
                                      column=self.ui_grid["df_frame"]["vertical_stroll_bar"]["column"],
                                      sticky=self.ui_grid["df_frame"]["vertical_stroll_bar"]["sticky"])
        self.horizontal_stroll_bar.grid(row=self.ui_grid["df_frame"]["horizontal_stroll_bar"]["row"],
                                        column=self.ui_grid["df_frame"]["horizontal_stroll_bar"]["column"],
                                        sticky=self.ui_grid["df_frame"]["horizontal_stroll_bar"]["sticky"])
        self.df_frame.grid_rowconfigure(0, weight=1)
        self.df_frame.grid_columnconfigure(0, weight=1)
        return None

    def main_task(self) -> str | bool:
        self.file_handler.clean_raw_df(self.have_name_and_code.get())
        error_str = self.combinations_generator.limit_check(df=self.file_handler.df_cleaned)
        if error_str:
            self.logger("Data exceeds output limit. Recommended to reduce number of dimensions or rows of data.")
            if error_str == "cancel":
                return error_str
        self.logger(f"{self.combinations_generator.expected_output} rows expected.")
        self.combinations_generator.write_path = FileHandler.get_new_file_path(self.entry_box.get())
        # Create new thread to handle back end processing.
        process_thread = threading.Thread(target=self.combinations_generator.thread_handler,
                                                                args=(self.file_handler.df_cleaned,
                                                                      self.file_handler.df_raw.columns,
                                                                      self.have_name_and_code.get(),
                                                                      self.combinations_generator.write_path),
                                                                daemon=True)
        process_thread.start()
        self.logger("Process to create new combinations has started.")
        return True

    def logger(self, log_str: str, is_update=False) -> None:
        if is_update:
            self.root.after(0, self._update_status_label, log_str)
        else:
            self.root.after(0, self._log_to_widget, log_str)
        return None

    def _log_to_widget(self, log_str: str) -> None:
        self.log_label.configure(text=log_str)
        print(log_str)
        self.log += "[" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "] " + log_str + "\n"
        return None

    def _update_status_label(self, status_str):
        self.log_label.configure(text=status_str)

    def browse_file(self) -> Type[AttributeError] | bool:
        file_path = fd.askopenfilename(title="Select file", filetypes=(("CSV Files", "*.csv"),))
        self.entry_box.configure(state=ctk.NORMAL)
        self.entry_box.delete(0, ctk.END)
        self.entry_box.insert(0, file_path)
        error_str = self.file_handler.validate_file_path(file_path, self.have_headers.get())
        if error_str:
            self.logger(error_str)
            self.run_button.configure(state=ctk.DISABLED)
            return AttributeError
        self.logger(f"File path: '{file_path}'")
        self.run_button.configure(state=ctk.NORMAL)
        self.entry_box.configure(state=ctk.DISABLED)
        self.display_df()
        self.logger(f"CSV loaded: {file_path}")
        return True

    def view_log(self) -> None:
        if self.log == "":
            self.log = "Run program to view log."
        messagebox.showinfo(title="Log", message=self.log)
        print(self.log)
        return None

    def close(self):
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    gui=GUI()