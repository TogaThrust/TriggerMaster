import sys
import os
import threading
import traceback
from multiprocessing.spawn import freeze_support
from typing import Type
import customtkinter as ctk
import pandas as pd
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox, Frame, Canvas, Scrollbar, filedialog as fd # treeview not implemented in CTk

from root.lib.config.gui_config import main_grid
from root.lib.config.help import help_page
from root.lib.Handlers.ErrorHandler import ErrorHandler
from root.lib.Handlers.FileHandler import FileHandler
from root.lib.Handlers.DateHandler import DateHandler
from root.lib.Handlers.LoggerGUI import Logger
from root.lib.Engine.CombinationsGenerator import CombinationsGenerator
from root.lib.util.dependencies import resource_path

ctk.set_appearance_mode("Dark")

class HelpPage(ctk.CTkFrame):
    def __init__(self, parent, window_width, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.labels = help_page
        # initiate main frame and canvas
        self.frame_holder = ctk.CTkFrame(self)
        self.frame_holder.pack(fill='both', expand=True)
        self.canvas = Canvas(self.frame_holder, bg="#2b2b2b", bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = Scrollbar(self.frame_holder, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=2, sticky="ns")
        self.frame_holder.rowconfigure(0, weight=1)
        self.frame_holder.columnconfigure(0, weight=1)
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        # initiate content frame
        self.window_width = self._get_window_width(window_width)
        self.content_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        # Contents
        self.label = ctk.CTkLabel(self.content_frame, text=self.labels[0]["text"], anchor="w",
                                  justify=ctk.LEFT, font=("Lato", 16))
        self.label.grid(row=0, column=0, sticky="nsew", padx=self.labels[0]["padx"], pady=self.labels[0]["pady"])
        self._add_images(resource_path("lib\\assets\\help\\"))

        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mouse_wheel(self, event):
        """Scroll using mouse wheel."""
        if event.delta:  # Windows and Linux
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:  # For macOS
            self.canvas.yview_scroll(int(-1 * event.delta), "units")

    def _get_window_width(self, window_width):
        """Get and print the current window width."""
        self.scrollbar.update()
        scrollbar_width = self.scrollbar.winfo_width() * 2
        return window_width - scrollbar_width

    def _add_images(self, image_directory):
        """ Adds images from a directory into a tab in the notebook. """
        for i, image_file in enumerate(os.listdir(image_directory)):
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_path = os.path.join(image_directory, image_file)

                # Open and process the image
                img = Image.open(resource_path(image_path))
                aspect_ratio = img.height / img.width
                new_height = int(self.window_width * aspect_ratio)
                img.thumbnail((self.window_width, new_height))  # Resize the image (optional)
                img_tk = ImageTk.PhotoImage(img)

                # Create a label for the image and center it
                label = ttk.Label(self.content_frame, image=img_tk)
                label.image = img_tk  # Keep a reference to avoid garbage collection
                label.grid(row=1+(i*2), column=0, sticky="nw", padx=(5,15), pady=(5,0))
                label2 = ctk.CTkLabel(self.content_frame, text=self.labels[i+1]["text"], anchor="w",
                                      justify=ctk.LEFT, font=("Lato", 14),
                                      wraplength=self.window_width)
                label2.grid(row=2+(i*2), column=0, sticky="nw",
                            padx=self.labels[i+1]["padx"], pady=self.labels[i+1]["pady"])

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, root, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = root
        self.ui_grid = main_grid
        self.font = ("Lato", 14)
        # Input frame and its widgets
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=self.ui_grid["input_frame"]["config"]["row"],
                              sticky=self.ui_grid["input_frame"]["config"]["sticky"],
                              padx=self.ui_grid["input_frame"]["config"]["padx"],
                              pady=self.ui_grid["input_frame"]["config"]["pady"])

        self.entry_box = ctk.CTkEntry(self.input_frame, font=self.font)
        self.entry_box.grid(row=self.ui_grid["input_frame"]["entry_box"]["row"],
                            column=self.ui_grid["input_frame"]["entry_box"]["column"],
                            columnspan=2,
                            sticky=self.ui_grid["input_frame"]["entry_box"]["sticky"],
                            padx=self.ui_grid["input_frame"]["entry_box"]["padx"],
                            pady=self.ui_grid["input_frame"]["entry_box"]["pady"])
        self.entry_box.insert(index=0, string="Choose a CSV file...")
        self.input_frame.grid_columnconfigure(index=0, weight=1)
        self.input_frame.grid_columnconfigure(index=1, weight=1)
        self.entry_box.configure(state=ctk.DISABLED)

        self.browse_button = (ctk.CTkButton(self.input_frame, font=self.font, command=self.browse_file,
                                            text= self.ui_grid["input_frame"]["browse_button"]["text"]))
        self.browse_button.grid(row=self.ui_grid["input_frame"]["browse_button"]["row"],
                                column=self.ui_grid["input_frame"]["browse_button"]["column"],
                                sticky=self.ui_grid["input_frame"]["browse_button"]["sticky"],
                                padx=self.ui_grid["input_frame"]["browse_button"]["padx"],
                                pady=self.ui_grid["input_frame"]["browse_button"]["pady"])

        # Date frame and its widgets
        self.date_frame = ctk.CTkFrame(self)
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

        self.date_entry_box = ctk.CTkEntry(self.date_frame, font=self.font)
        self.date_entry_box.grid(row=self.ui_grid["date_frame"]["date_entry_box"]["row"],
                                 column=self.ui_grid["date_frame"]["date_entry_box"]["column"],
                                 sticky=self.ui_grid["date_frame"]["date_entry_box"]["sticky"],
                                 padx=self.ui_grid["date_frame"]["date_entry_box"]["padx"],
                                 pady=self.ui_grid["date_frame"]["date_entry_box"]["pady"])
        self.date_entry_box.insert(index=0, string="mm/yyyy")
        self.date_frame.grid_columnconfigure(index=0, weight=1)
        self.date_frame.grid_columnconfigure(index=1, weight=1)

        self.date_start_label = ctk.CTkLabel(self.date_frame,
                                              text=self.ui_grid["date_frame"]["date_start_label"]["text"])
        self.date_start_label.grid(row=self.ui_grid["date_frame"]["date_start_label"]["row"],
                                   column=self.ui_grid["date_frame"]["date_start_label"]["column"],
                                    padx=self.ui_grid["date_frame"]["date_start_label"]["padx"],
                                    pady=self.ui_grid["date_frame"]["date_start_label"]["pady"],
                                    sticky=self.ui_grid["date_frame"]["date_start_label"]["sticky"])

        self.date_end_label = ctk.CTkLabel(self.date_frame,
                                           text=self.ui_grid["date_frame"]["date_end_label"]["text"])
        self.date_end_label.grid(row=self.ui_grid["date_frame"]["date_end_label"]["row"],
                                column=self.ui_grid["date_frame"]["date_end_label"]["column"],
                                padx=self.ui_grid["date_frame"]["date_end_label"]["padx"],
                                pady=self.ui_grid["date_frame"]["date_end_label"]["pady"],
                                sticky=self.ui_grid["date_frame"]["date_end_label"]["sticky"])

        self.calendar_start = DateEntry(self.date_frame, date_pattern="dd-mm-yyyy")
        self.calendar_start.grid(row=self.ui_grid["date_frame"]["calendar_start"]["row"],
                                 column=self.ui_grid["date_frame"]["calendar_start"]["column"],
                                 padx=self.ui_grid["date_frame"]["calendar_start"]["padx"],
                                 pady=self.ui_grid["date_frame"]["calendar_start"]["pady"],
                                 sticky=self.ui_grid["date_frame"]["calendar_start"]["sticky"])

        self.calendar_end = DateEntry(self.date_frame, date_pattern="dd-mm-yyyy")
        self.calendar_end.grid(row=self.ui_grid["date_frame"]["calendar_end"]["row"],
                               column=self.ui_grid["date_frame"]["calendar_end"]["column"],
                               padx=self.ui_grid["date_frame"]["calendar_end"]["padx"],
                               pady=self.ui_grid["date_frame"]["calendar_end"]["pady"],
                               sticky=self.ui_grid["date_frame"]["calendar_end"]["sticky"])

        self.date_frame.grid_columnconfigure(index=0, weight=1)
        self.date_frame.grid_columnconfigure(index=1, weight=1)

        # df_frame and its widgets
        self.df_frame = ctk.CTkFrame(self)
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
        self.output_frame = ctk.CTkFrame(self)
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

        self.output_frame.grid_columnconfigure(index=0, weight=1)
        self.output_frame.grid_columnconfigure(index=1, weight=1)
        self.output_frame.grid_columnconfigure(index=2, weight=1)

        # Log frame and its widgets
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=self.ui_grid["log_frame"]["config"]["row"],
                            sticky=self.ui_grid["log_frame"]["config"]["sticky"],
                            padx=self.ui_grid["log_frame"]["config"]["padx"],
                            pady=self.ui_grid["log_frame"]["config"]["pady"])

        self.log_label = ctk.CTkLabel(self.log_frame, text=self.ui_grid["log_frame"]["log_label"]["text"])
        self.log_label.grid(row=self.ui_grid["log_frame"]["log_label"]["row"],
                            columnspan=self.ui_grid["log_frame"]["log_label"]["columnspan"],
                            padx=self.ui_grid["log_frame"]["log_label"]["padx"],
                            pady=self.ui_grid["log_frame"]["log_label"]["pady"],
                            sticky=self.ui_grid["log_frame"]["log_label"]["sticky"])
        self.log_label.update()
        self.log_frame.configure(height=self.log_label.winfo_height())

        self.gif_image = Image.open(resource_path("lib/assets/loading.gif"))
        self.animation_enabled = False
        self.loading_label = ctk.CTkLabel(self.log_frame, text="")
        self.loading_label.grid(row=self.ui_grid["log_frame"]["loading_label"]["row"],
                                column=self.ui_grid["log_frame"]["loading_label"]["column"],
                                columnspan=self.ui_grid["log_frame"]["loading_label"]["columnspan"],
                                padx=self.ui_grid["log_frame"]["loading_label"]["padx"],
                                pady=self.ui_grid["log_frame"]["loading_label"]["pady"],
                                sticky=self.ui_grid["log_frame"]["loading_label"]["sticky"])
        self.log_frame.grid_columnconfigure(index=0, weight=1)
        self.log_frame.grid_columnconfigure(index=1, weight=1)
        self.log_frame.grid_propagate(False)
        self._cycle_frame(0)

        # invoke other classes
        self.logger = Logger(self.root, self.log_label)
        self.error_handler = ErrorHandler(self.logger)
        self.combinations_generator = CombinationsGenerator(self.logger, self.error_handler)
        self.file_handler = FileHandler(self.logger, self.error_handler)

    @ staticmethod
    def _make_transparent(img, bg_color=(255, 255, 255)):
        img = img.convert("RGBA")  # Ensure the image is in RGBA mode
        datas = img.getdata()
        new_data = []
        for item in datas: # Change all white (also shades of white)
            if item[:3] == bg_color:
                new_data.append((255, 255, 255, 0)) # Make it fully transparent
            else:
                new_data.append(item)
        img.putdata(new_data)
        return img

    def _cycle_frame(self, frame_index):
        if self.animation_enabled:
            try:
                self.gif_image.seek(frame_index)
                transparent_frame = self._make_transparent(self.gif_image)
                frame_image = ImageTk.PhotoImage(transparent_frame)
                self.loading_label.configure(image=frame_image)
                self.loading_label.image = frame_image # Store reference to avoid garbage collection
                self.log_frame.after(self.gif_image.info['duration'],
                                     self._cycle_frame, (frame_index + 1) % self.gif_image.n_frames)
            except EOFError:
                pass

    def toggle_animation(self):
        self.animation_enabled = not self.animation_enabled
        if self.animation_enabled:
            self._cycle_frame(0)
        else:
            self.loading_label.configure(image='')

    def display_df(self, df_to_display: pd.DataFrame =None, max_rows = 100) -> None:
        """Display the df input to the tree view."""
        if df_to_display is None:
            df_to_display = self.file_handler.df_raw
        self.df_tree.delete(*self.df_tree.get_children())
        self.df_tree["columns"] = list(df_to_display.columns)
        self.df_tree["show"] = "headings"  # Hide the first empty column
        for col in df_to_display.columns:
            self.df_tree.heading(col, text=col)
            self.df_tree.column(col, anchor=ctk.CENTER)
        for index, row in df_to_display.iterrows():
            if index == max_rows-1:
                break
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
        """Inputs the returned file path from 'fd.askopenfilename'."""
        self.entry_box.configure(state=ctk.NORMAL)
        self.entry_box.delete(first_index=0, last_index=ctk.END)
        self.entry_box.insert(index=0, string=file_path)
        self.entry_box.configure(state=ctk.DISABLED)
        return None

    def browse_file(self) -> Type[AttributeError | UnicodeDecodeError] | None:
        """Gets the select file path, try to read from CSV/Excel and set run status as good to go."""
        self.logger.clear_log()
        file_path = fd.askopenfilename(title="Select file",
                                       filetypes=(("Excel Files", "*.xlsx"),("CSV Files", "*.csv")))
        if not self.file_handler.valid_path(file_path):
            return AttributeError
        if not self.file_handler.convertible_file(file_path):
            return UnicodeDecodeError
        self.input_entry_box(file_path)
        self.display_df()
        self.run_button.configure(state=ctk.NORMAL)
        self.logger.log(log_str=f"File path: '{file_path}'", log_type="record")
        self.logger.log(log_str=f"CSV loaded with {self.file_handler.df_raw.shape[1]} columns, "
                                + f"{self.file_handler.df_raw.shape[0]} rows.", log_type="record")
        return None

    def toggle_all(self, state) -> None:
        """Toggles all Widgets that should be disabled when backend is running."""
        self.toggle_animation()
        if state == "DISABLED":
            state = ctk.DISABLED
        elif state == "NORMAL":
            state = ctk.NORMAL
        self.run_button.configure(state=state)
        self.browse_button.configure(state=state)
        self.date_entry_box.configure(state=state)
        self.calendar_start.configure(state=state)
        self.calendar_end.configure(state=state)
        return None

    def generate_dates(self) -> list:
        """Generates a list of dates from start date and end date selected. Outputs date format set by user."""
        # I understand that creating an object instance just to run some methods only to destroy it after is autistic
        # but what are you gonna to do abt it.
        date_handler = DateHandler(self.calendar_start.get(), self.calendar_end.get())
        dates = date_handler.generate_dates_between(self.date_entry_box.get().strip())
        del date_handler
        return dates

    def run(self) -> str | None:
        """Try to handle most errors identified before process is run.
            Starts a separate thread for backend to maintain frontend usability"""
        if not self.file_handler.df_cleanable():
            return None
        self.toggle_all("DISABLED")
        self.combinations_generator.write_path = self.file_handler.get_new_file_path(self.entry_box.get())
        # Create new thread to handle back end processing.
        threading.excepthook = self._thread_excepthook
        process_thread = threading.Thread(name="Main Instance", daemon=True,
                                          target=self.combinations_generator.start_generator,
                                          args=(self.file_handler.df_cleaned, self.file_handler.df_raw.columns,
                                                self.generate_dates(), self.toggle_all, self.display_df))
        process_thread.start()
        self.logger.log(log_str="Process to create new combinations has started.", log_type="record")
        return None

    def view_log(self) -> None:
        """Logs mainly for user. Pop-ups a window with info."""
        if self.logger.get_logs() == "":
            self.logger.log(log_str="Run program to view log.", log_type="record")
        messagebox.showinfo(title="Log", message=self.logger.get_logs())
        print(f"Event Log printed\n" + self.logger.get_logs())
        return None

    def close(self):
        """Closes program."""
        # I am so sorry Mr. Daemon Thread. Not experienced enough to flag exit path.
        self.root.destroy()
        sys.exit()

    def _thread_excepthook(self, args):
        """Rewrite thread excepthook method to catch unhandled exceptions."""
        error_message = ''.join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
        messagebox.showerror(title="Unhandled Exception", message=f"An error occurred: \n{error_message}\n")
        self.root.destroy()
        sys.exit()

class TriggerMaster:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(f"Trigger Master V1")
        self.root.resizable(width=False, height=False)

        # < a href = "https://www.flaticon.com/free-icons/cute" title = "cute icons" >
        # Cute icons created by Adorableninana - Flaticon < / a >
        self.root.iconbitmap(resource_path('lib\\assets\\icon.ico')) # Icon

        # Image
        target_height = 40
        self.pil_image = Image.open(resource_path("lib\\assets\\logo.png"))
        original_width, original_height = self.pil_image.size
        scale = target_height / original_height
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        self.resized_image = self.pil_image.resize((new_width, new_height))
        self.image = ImageTk.PhotoImage(self.resized_image)
        self.image_label = ctk.CTkLabel(self.root,text="", image=self.image)
        self.image_label.pack(padx=0, pady=(20,5))

        # initiate notebook
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.layout("TNotebook", [])
        self.style.configure("TNotebook", background="#242424")
        self.style.configure("TNotebook.Tab", background="#242424", font=("Lato", 10), foreground="white")
        self.style.map("TNotebook.Tab",
                       background=[("selected", "#242424"), ("!selected", "#2b2b2b")],
                       expand=[("selected", [1, 1, 1, 0]), ("!selected", [1, 1, 1, 0])],
                       focuscolor=[("selected", "#242424"), ("!selected", "#2b2b2b")],
                       lightcolor=[("selected", "#2b2b2b"), ("!selected", "#2b2b2b")],
                       bordercolor=[("selected", "#2b2b2b"), ("!selected", "#2b2b2b")]
                       )
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.main_tab = Frame(self.notebook, background="#242424")
        self.help_tab = Frame(self.notebook, background="#242424")
        self.about_tab = Frame(self.notebook, background="#242424")
        self.notebook.add(self.main_tab, text="Home")
        self.notebook.add(self.help_tab, text="Help")
        self.notebook.add(self.about_tab, text="About")
        self.notebook.pack(fill="both", pady=(10,0))

        # Home page
        self.home_page = HomePage(self.main_tab, self.root)
        self.home_page.pack(fill="both", expand=True)

        # Help Page
        self.root.update()
        self.help_page = HelpPage(self.help_tab, self.root.winfo_width())
        self.help_page.pack(fill="both", expand=True)

        # About Page
        self.about_label = ctk.CTkLabel(self.about_tab, anchor="w", justify=ctk.LEFT,
                                        text="\nVersion: V1\nAuthor: Luke Wang"
                                             + "\nHelp email: luke.wang@shearwaterasia.com"
                                             + "\nAttribution: Icon by @Adorableninana - Flaticon. For Commercial Use.")
        self.about_label.pack(side="top", anchor="w", padx=5)
        self.credit_label = ctk.CTkLabel(self.about_tab,
                                         text="All Rights Reserved.")
        self.credit_label.pack(side="bottom")

        # main loop, only to the end pls
        self.root.report_callback_exception = self.report_callback_exception
        self.root.mainloop()

    def report_callback_exception(self, exc, val, tb):
        """Rewrite tkinter callback exception method to catch unhandled exceptions."""
        error_message = ''.join(traceback.format_exception(exc, val, tb))
        messagebox.showerror(title="Unhandled Exception", message=f"An error occurred: \n{error_message}\n")
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    freeze_support() # multiprocessing goes crazy without this line.
    main_program=TriggerMaster()