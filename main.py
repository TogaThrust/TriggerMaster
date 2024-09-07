import sys
import threading
from typing import Type
import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox, PhotoImage, filedialog as fd # treeview not implemented in CTk
from lib.gui_config import ui_grid, custom_font
from lib.Handlers.ErrorHandler import ErrorHandler
from lib.Handlers.FileHandler import FileHandler
from lib.Handlers.LoggerGUI import Logger
from lib.Engine.CombinationsGenerator import CombinationsGenerator

ctk.set_appearance_mode("Dark")

class GUI:
    def __init__(self):
        self.ui_grid = ui_grid
        self.font = custom_font
        self.root = ctk.CTk()
        self.root.title(f"Trigger Master")
        self.root.resizable(width=False, height=False)

        # Input frame and its widgets
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.grid(row=self.ui_grid["input_frame"]["config"]["row"],
                              sticky=self.ui_grid["input_frame"]["config"]["sticky"],
                              padx=self.ui_grid["input_frame"]["config"]["padx"],
                              pady=self.ui_grid["input_frame"]["config"]["pady"])

        self.image = PhotoImage(file="path_to_your_image.png")  # Adjust the path to your image file
        self.image_label = ctk.CTkLabel(self.root, image=self.image)
        self.image_label.pack(padx=10, pady=10)

        self.entry_box = ctk.CTkEntry(self.input_frame, font=self.font)
        self.entry_box.grid(row=self.ui_grid["input_frame"]["entry_box"]["row"],
                            column=self.ui_grid["input_frame"]["entry_box"]["column"],
                            sticky=self.ui_grid["input_frame"]["entry_box"]["sticky"],
                            padx=self.ui_grid["input_frame"]["entry_box"]["padx"],
                            pady=self.ui_grid["input_frame"]["entry_box"]["pady"])
        self.entry_box.insert(index=0, string="Choose a CSV file...")
        self.entry_box.configure(state=ctk.DISABLED)

        self.browse_button = (ctk.CTkButton(self.input_frame, font=self.font, command=self.browse_file,
                                            text= self.ui_grid["input_frame"]["browse_button"]["text"]))
        self.browse_button.grid(row=self.ui_grid["input_frame"]["browse_button"]["row"],
                                column=self.ui_grid["input_frame"]["browse_button"]["column"],
                                sticky=self.ui_grid["input_frame"]["browse_button"]["sticky"],
                                padx=self.ui_grid["input_frame"]["browse_button"]["padx"],
                                pady=self.ui_grid["input_frame"]["browse_button"]["pady"])

        self.have_headers = ctk.IntVar()
        self.check_headers = ctk.CTkCheckBox(self.input_frame, variable=self.have_headers, font=self.font,
                                             text=self.ui_grid["input_frame"]["check_headers"]["text"])
        self.check_headers.grid(row=self.ui_grid["input_frame"]["check_headers"]["row"],
                                padx=self.ui_grid["input_frame"]["check_headers"]["padx"],
                                pady=self.ui_grid["input_frame"]["check_headers"]["pady"],
                                sticky=self.ui_grid["input_frame"]["check_headers"]["sticky"])
        self.check_headers.toggle()

        self.have_name_and_code = ctk.IntVar()
        self.check_code_and_name = ctk.CTkCheckBox(self.input_frame,
                                                   variable=self.have_name_and_code, font=self.font,
                                                   text=self.ui_grid["input_frame"]["check_code_and_name"]["text"])
        # Actually there might be no reason to implement this feature as end product will be in upload format.
        # self.check_code_and_name.grid(row=self.ui_grid["input_frame"]["check_code_and_name"]["row"],
        #                               padx=self.ui_grid["input_frame"]["check_code_and_name"]["padx"],
        #                               pady=self.ui_grid["input_frame"]["check_code_and_name"]["pady"],
        #                               sticky=self.ui_grid["input_frame"]["check_code_and_name"]["sticky"])
        self.check_code_and_name.toggle()
        # todo first row accounts
        # Date frame and its widgets
        self.date_frame = ctk.CTkFrame(self.root)
        # todo date function
        # self.date_frame.grid(row=self.ui_grid["date_frame"]["config"]["row"],
        #                      sticky=self.ui_grid["date_frame"]["config"]["sticky"],
        #                      padx=self.ui_grid["date_frame"]["config"]["padx"],
        #                      pady=self.ui_grid["date_frame"]["config"]["pady"])

        self.date_format_label = ctk.CTkLabel(self.date_frame,
                                              text=self.ui_grid["date_frame"]["date_format_label"]["text"])
        self.date_format_label.grid(row=self.ui_grid["date_frame"]["date_format_label"]["row"],
                                    column=self.ui_grid["date_frame"]["date_format_label"]["column"],
                                    padx=self.ui_grid["date_frame"]["date_format_label"]["padx"],
                                    pady=self.ui_grid["date_frame"]["date_format_label"]["pady"],
                                    sticky=self.ui_grid["date_frame"]["date_format_label"]["sticky"])

        self.date_entry_box = ctk.CTkEntry(self.date_frame, font=self.font)
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

        self.calendar_start = DateEntry(self.date_frame, date_pattern="yyyy-mm-dd")
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

        self.run_button = (ctk.CTkButton(self.output_frame, font=self.font, command=self.run,
                                         text=self.ui_grid["output_frame"]["run_button"]["text"]))
        self.run_button.grid(row=self.ui_grid["output_frame"]["run_button"]["row"],
                             column=self.ui_grid["output_frame"]["run_button"]["column"],
                             sticky=self.ui_grid["output_frame"]["run_button"]["sticky"],
                             padx=self.ui_grid["output_frame"]["run_button"]["padx"],
                             pady=self.ui_grid["output_frame"]["run_button"]["pady"])
        self.run_button.configure(state=ctk.DISABLED)

        self.view_log_button = (ctk.CTkButton(self.output_frame, font=self.font, command=self.view_log,
                                              text=self.ui_grid["output_frame"]["view_log_button"]["text"]))
        self.view_log_button.grid(row=self.ui_grid["output_frame"]["view_log_button"]["row"],
                                  column=self.ui_grid["output_frame"]["view_log_button"]["column"],
                                  sticky=self.ui_grid["output_frame"]["view_log_button"]["sticky"],
                                  padx=self.ui_grid["output_frame"]["view_log_button"]["padx"],
                                  pady=self.ui_grid["output_frame"]["view_log_button"]["pady"])

        self.cancel_button = (ctk.CTkButton(self.output_frame, font=self.font, command=self.close,
                                            text=self.ui_grid["output_frame"]["cancel_button"]["text"]))
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

        # invoke other classes
        self.logger = Logger(self.root, self.log_label)
        self.error_handler = ErrorHandler(self.logger)
        self.combinations_generator = CombinationsGenerator(self.logger, self.error_handler)
        self.file_handler = FileHandler(self.logger, self.error_handler)

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
            self.df_tree.insert(parent="", index="end", values=list(row))
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
        self.df_frame.grid_rowconfigure(index=0, weight=1)
        self.df_frame.grid_columnconfigure(index=0, weight=1)
        return None

    def input_entry_box(self, file_path: str) -> None:
        self.entry_box.configure(state=ctk.NORMAL)
        self.entry_box.delete(first_index=0, last_index=ctk.END)
        self.entry_box.insert(index=0, string=file_path)
        self.entry_box.configure(state=ctk.DISABLED)
        return None

    def browse_file(self) -> Type[AttributeError | UnicodeDecodeError] | None:
        self.logger.clear_log()
        file_path = fd.askopenfilename(title="Select file", filetypes=(("CSV Files", "*.csv"),))
        if not self.file_handler.valid_path(file_path):
            return AttributeError
        if not self.file_handler.convertible_csv(file_path, self.have_headers.get()):
            return UnicodeDecodeError
        self.input_entry_box(file_path)
        self.display_df()
        self.run_button.configure(state=ctk.NORMAL)
        self.logger.log(log_str=f"File path: '{file_path}'", log_type="record")
        self.logger.log(log_str=f"CSV loaded with {self.file_handler.df_raw.shape[1]} columns, "
                                + f"{self.file_handler.df_raw.shape[0]} rows.", log_type="record")
        return None

    def disable_all(self) -> None:
        self.run_button.configure(state=ctk.DISABLED)
        self.browse_button.configure(state=ctk.DISABLED)
        self.check_headers.configure(state=ctk.DISABLED)
        self.check_code_and_name.configure(state=ctk.DISABLED)
        self.date_entry_box.configure(state=ctk.DISABLED)
        self.calendar_start.configure(state=ctk.DISABLED)
        self.calendar_end.configure(state=ctk.DISABLED)
        return None

    def enable_all(self) -> None:
        self.run_button.configure(state=ctk.NORMAL)
        self.browse_button.configure(state=ctk.NORMAL)
        self.check_headers.configure(state=ctk.NORMAL)
        self.check_code_and_name.configure(state=ctk.NORMAL)
        self.date_entry_box.configure(state=ctk.NORMAL)
        self.calendar_start.configure(state=ctk.NORMAL)
        self.calendar_end.configure(state=ctk.NORMAL)
        return None

    def run(self) -> str | None:
        self.disable_all()
        self.file_handler.clean_raw_df(self.have_name_and_code.get())
        error_str = self.combinations_generator.limit_check(df=self.file_handler.df_cleaned)
        if error_str:
            self.logger.log(log_str="Data exceeds output limit."
                                    + "Recommended to reduce number of dimensions or rows of data.",
                            log_type="update and record")
            if error_str == "cancel":
                return error_str
        self.logger.log(log_str=f"{self.combinations_generator.expected_output} rows expected.",
                        log_type="record")
        self.combinations_generator.write_path = self.file_handler.get_new_file_path(self.entry_box.get())
        # Create new thread to handle back end processing.
        process_thread = threading.Thread(target=self.combinations_generator.thread_handler,
                                          daemon=True, name="Main Instance",
                                          args=(self.file_handler.df_cleaned, self.file_handler.df_raw.columns,
                                                self.have_name_and_code.get(), self.enable_all))
        process_thread.start()
        self.logger.log(log_str="Process to create new combinations has started.", log_type="record")
        return None

    def view_log(self) -> None:
        if self.logger.get_logs() == "":
            self.logger.log(log_str="Run program to view log.", log_type="record")
        messagebox.showinfo(title="Log", message=self.logger.get_logs())
        print(f"Event Log printed\n" + self.logger.get_logs())
        return None

    def close(self):
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    gui=GUI()