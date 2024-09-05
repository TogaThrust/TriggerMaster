import os
import sys

import pandas
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox

# todo create button "run" and code out the main function
# todo create new function to export the df to a new output csv
def validate_csv(file_path, have_headers) -> pandas.DataFrame or None:
    if not os.path.exists(file_path):
        messagebox.showinfo(title="Invalid File Path", message="File does not exist!")
        return None
    try:
        header = None
        if have_headers:
            header = 'infer'
        pd_validate = pd.read_csv(file_path, header=header, encoding='utf-8')
        return pd_validate
    except:
        messagebox.showinfo(title="Error",
                            message="Unknown Error Occurred: Program is having trouble reading your file.")

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trigger Duplicator")
        self.root.resizable(False, False)
        # characteristics of widgets
        self.UI_grid = {"entry_box":                {"row": 1,
                                                     "column": 0,
                                                     "sticky": tk.NW,
                                                     "width": 50,
                                                     "padx": 10,
                                                     "pady": 0},

                        "browse_button":            {"text": "Browse",
                                                     "width": 10,
                                                     "row": 1,
                                                     "column": 1,
                                                     "sticky": tk.NE,
                                                     "padx": 10,
                                                     "pady": 0},

                        "check_headers":            {"text": "My file has headers",
                                                     "row": 2,
                                                     "padx": 5,
                                                     "sticky": tk.W},

                        "frame":                    {"row": 3 ,
                                                     "column": 0,
                                                     "sticky": tk.N,
                                                     "width": 400,
                                                     "height": 300,
                                                     "padx": 10,
                                                     "pady": 0},

                        "tree":                     {"row": 0 ,
                                                     "column": 0,
                                                     "width": 50,
                                                     "height": 300,
                                                     "sticky": tk.NSEW},

                        "vertical_stroll_bar":      {"row": 0 ,
                                                     "column": 1,
                                                     "sticky": tk.NS},

                        "horizontal_stroll_bar":    {"row": 1 ,
                                                     "column": 0,
                                                     "sticky": tk.EW},

                        "retrieve_button":          {"text": "Retrieve CSV",
                                                     "width": 10,
                                                     "row": 4 ,
                                                     "column": 0,
                                                     "sticky": tk.NW,
                                                     "padx": 10,
                                                     "pady": 10},

                        "cancel_button":            {"text": "Exit",
                                                     "width": 10,
                                                     "row": 4 ,
                                                     "column": 1,
                                                     "sticky": tk.S,
                                                     "padx": 10,
                                                     "pady": 10}
                        }

        # Widgets on initialisation
        self.entry_box = tk.Entry(self.root, width=self.UI_grid["entry_box"]["width"])
        self.entry_box.grid(row=self.UI_grid["entry_box"]["row"],
                            column=self.UI_grid["entry_box"]["column"],
                            sticky=self.UI_grid["entry_box"]["sticky"],
                            padx=self.UI_grid["entry_box"]["padx"],
                            pady=self.UI_grid["entry_box"]["pady"])
        self.entry_box.insert(0, "Choose a CSV file...")

        self.browse_button = (tk.Button(self.root,
                                        text=self.UI_grid["browse_button"]["text"],
                                        width=self.UI_grid["browse_button"]["width"],
                                        command=self.get_file_path))
        self.browse_button.grid(row=self.UI_grid["browse_button"]["row"],
                                column=self.UI_grid["browse_button"]["column"],
                                sticky=self.UI_grid["browse_button"]["sticky"],
                                padx=self.UI_grid["browse_button"]["padx"],
                                pady=self.UI_grid["browse_button"]["pady"])

        self.check_headers_state = tk.IntVar()
        self.check_headers = tk.Checkbutton(self.root,
                                            variable=self.check_headers_state,
                                            text=self.UI_grid["check_headers"]["text"])
        self.check_headers.grid(row=self.UI_grid["check_headers"]["row"],
                                padx=self.UI_grid["check_headers"]["padx"],
                                sticky=self.UI_grid["check_headers"]["sticky"])
        self.check_headers.toggle()

        self.retrieve_button = (tk.Button(self.root,
                                          text=self.UI_grid["retrieve_button"]["text"],
                                          command=self.run,
                                          width=self.UI_grid["retrieve_button"]["width"]))
        self.retrieve_button.grid(row=self.UI_grid["retrieve_button"]["row"],
                                  column=self.UI_grid["retrieve_button"]["column"],
                                  sticky=self.UI_grid["retrieve_button"]["sticky"],
                                  padx=self.UI_grid["retrieve_button"]["padx"],
                                  pady=self.UI_grid["retrieve_button"]["pady"])

        self.cancel_button = (tk.Button(self.root,
                                     text=self.UI_grid["cancel_button"]["text"],
                                     command=self.close,
                                     width=self.UI_grid["cancel_button"]["width"]))
        self.cancel_button.grid(row=self.UI_grid["cancel_button"]["row"],
                                column=self.UI_grid["cancel_button"]["column"],
                                sticky=self.UI_grid["cancel_button"]["sticky"],
                                padx=self.UI_grid["cancel_button"]["padx"],
                                pady=self.UI_grid["cancel_button"]["pady"])

        self.df_frame = ttk.Frame(self.root,
                                  width=self.UI_grid["frame"]["width"],
                                  height=self.UI_grid["frame"]["height"])
        self.df_frame.grid(row=self.UI_grid["frame"]["row"],
                           column=self.UI_grid["frame"]["column"],
                           sticky=self.UI_grid["frame"]["sticky"])


        self.df_tree = ttk.Treeview(self.df_frame)
        self.vertical_stroll_bar = ttk.Scrollbar(self.df_frame, orient="vertical", command=self.df_tree.yview)
        self.horizontal_stroll_bar = ttk.Scrollbar(self.df_frame, orient="horizontal", command=self.df_tree.xview)
        self.df_tree.configure(yscrollcommand=self.vertical_stroll_bar.set,
                               xscrollcommand=self.horizontal_stroll_bar.set)
        # main event loop: please only add to the end
        self.root.mainloop()

    def get_file_path(self):
        file_path = fd.askopenfilename(title="Select file", filetypes=(("CSV Files", "*.csv"),))
        self.entry_box.delete(0, tk.END)
        self.entry_box.insert(0, file_path)

    def display_df(self):
        file_path = self.entry_box.get()
        have_headers = False
        if self.check_headers_state.get() == 0:
            have_headers = False
            print(f"no headers, get value {self.check_headers_state.get()}") # todo remove log
        elif self.check_headers_state.get() == 1:
            have_headers = True
            print(f"have headers, get value {self.check_headers_state.get()}") # todo remove log
        self.df_tree.delete(*self.df_tree.get_children())
        df_to_display = validate_csv(file_path, have_headers)
        self.df_tree["columns"] = list(df_to_display.columns)
        self.df_tree["show"] = "headings"  # Hide the first empty column
        for col in df_to_display.columns:
            self.df_tree.heading(col, text=col)
            self.df_tree.column(col, anchor=tk.CENTER)
        for index, row in df_to_display.iterrows():
            self.df_tree.insert("", "end", values=list(row))
        print("csv loaded") # todo remove log

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
        self.df_frame.grid_propagate(False)

    def run(self, event=None):
        self.display_df()

    def close(self, event=None):
        self.root.destroy()
        sys.exit()

    def key_binds(self):
        self.root.bind('<Return>', self.run)
        self.root.bind('<Escape>', self.close)

if __name__ == "__main__":
    GUI()
