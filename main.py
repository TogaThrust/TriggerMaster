import os
import sys

import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
import itertools


# todo 4. CTK with better UI, and alignment
# todo 5. Date selector
class GUI:
    def __init__(self):
        self.df_validated = None
        # UI main
        self.root = tk.Tk()
        self.root.title("Trigger Duplicator")
        self.root.resizable(False, False)
        # characteristics of widgets
        self.UI_grid = {"entry_box": {"row": 1,
                                      "column": 0,
                                      "sticky": tk.NW,
                                      "width": 50,
                                      "padx": 10,
                                      "pady": 0},

                        "browse_button": {"text": "Browse",
                                          "width": 10,
                                          "row": 1,
                                          "column": 1,
                                          "sticky": tk.NE,
                                          "padx": 10,
                                          "pady": 0},

                        "check_headers": {"text": "My file has headers",
                                          "row": 2,
                                          "padx": 5,
                                          "sticky": tk.W},

                        "frame": {"row": 3,
                                  "column": 0,
                                  "sticky": tk.N,
                                  "width": 400,
                                  "height": 300,
                                  "padx": 10,
                                  "pady": 0},

                        "tree": {"row": 0,
                                 "column": 0,
                                 "width": 50,
                                 "height": 300,
                                 "sticky": tk.NSEW},

                        "vertical_stroll_bar": {"row": 0,
                                                "column": 1,
                                                "sticky": tk.NS},

                        "horizontal_stroll_bar": {"row": 1,
                                                  "column": 0,
                                                  "sticky": tk.EW},

                        "log_label": {"text": "Press Start",
                                      "row": 4,
                                      "column": 0,
                                      "padx": 10,
                                      "sticky": tk.NW},

                        "run_button": {"text": "Start",
                                       "width": 10,
                                       "row": 5,
                                       "column": 0,
                                       "sticky": tk.NW,
                                       "padx": 10,
                                       "pady": 10},

                        "cancel_button": {"text": "Exit",
                                          "width": 10,
                                          "row": 5,
                                          "column": 2,
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
                                        command=self.browse_file))
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

        self.log_label = tk.Label(self.root, text=self.UI_grid["log_label"]["text"])
        self.log_label.grid(row=self.UI_grid["log_label"]["row"],
                            padx=self.UI_grid["log_label"]["padx"],
                            sticky=self.UI_grid["log_label"]["sticky"])

        self.run_button = (tk.Button(self.root,
                                     text=self.UI_grid["run_button"]["text"],
                                     command=lambda: self.permutate_and_combine(df_input=self.df_validated),
                                     width=self.UI_grid["run_button"]["width"]))
        self.run_button.grid(row=self.UI_grid["run_button"]["row"],
                             column=self.UI_grid["run_button"]["column"],
                             sticky=self.UI_grid["run_button"]["sticky"],
                             padx=self.UI_grid["run_button"]["padx"],
                             pady=self.UI_grid["run_button"]["pady"])
        self.run_button.config(state=tk.DISABLED)

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

    def validate_csv(self, file_path, have_headers=True):
        if not os.path.exists(file_path):
            messagebox.showerror(title="Invalid File Path", message="File does not exist!")
            self.log_label.config(text=f"Invalid File Path: {file_path}")
            return None
        try:
            header = None
            if have_headers:
                header = 'infer'
            df_validated = pd.read_csv(file_path, header=header, encoding='utf-8')
        except UnicodeDecodeError:
            messagebox.showerror(title="Error",
                                 message="Unknown Error Occurred: Program is having trouble reading your file.")
            return
        self.run_button.config(state=tk.NORMAL)
        self.entry_box.config(state=tk.DISABLED)
        return df_validated

    def browse_file(self):
        file_path = fd.askopenfilename(title="Select file", filetypes=(("CSV Files", "*.csv"),))
        self.entry_box.config(state=tk.NORMAL)
        self.entry_box.delete(0, tk.END)
        self.entry_box.insert(0, file_path)
        have_headers = True
        if self.check_headers_state.get() == 0:
            have_headers = False
        elif self.check_headers_state.get() == 1:
            have_headers = True
        self.df_validated = self.validate_csv(file_path, have_headers)
        self.logger(f"File path: {file_path}")
        self.display_df(self.df_validated)

    def display_df(self, df_to_display=None):
        if df_to_display is None:
            df_to_display = self.df_validated
        self.df_tree.delete(*self.df_tree.get_children())
        self.df_tree["columns"] = list(df_to_display.columns)
        self.df_tree["show"] = "headings"  # Hide the first empty column
        for col in df_to_display.columns:
            self.df_tree.heading(col, text=col)
            self.df_tree.column(col, anchor=tk.CENTER)
        for index, row in df_to_display.iterrows():
            self.df_tree.insert("", "end", values=list(row))
        self.logger("CSV loaded")  # todo remove log
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

    def permutate_and_combine(self, df_input):
        try:
            df_cleaned = df_input.apply(lambda col: col.dropna().reset_index(drop=True))
            max_len = df_cleaned.apply(len).max()
            df_cleaned = df_cleaned.apply(lambda col: col.reindex(range(max_len)))
            combinations = list(itertools.product(*[df_cleaned[col] for col in df_cleaned.columns]))
            df_output = pd.DataFrame(combinations, columns=df_cleaned.columns)
            df_output = df_output.dropna()
            self.display_df(df_output)
            self.save(df_output)
        except AttributeError:
            messagebox.showerror(title="Error",
                                 message="Unable to perform operation on file.")
        self.run_button.config(state=tk.DISABLED)

    def save(self, df_to_save):
        file_path = self.entry_box.get()
        temp_path_list = file_path.split(".")
        new_file_path = temp_path_list[0] + "_output" + ".csv"
        if os.path.exists(new_file_path):
            temp_path_list = new_file_path.split(".")
            new_file_path = temp_path_list[0] + "(1)" + ".csv"
        df_to_save.to_csv(new_file_path, index=False)
        self.logger(f"DataFrame exported to {new_file_path}")

    def logger(self, log_str):
        self.log_label.config(text=log_str)

    def close(self):
        self.root.destroy()
        sys.exit()


if __name__ == "__main__":
    GUI()