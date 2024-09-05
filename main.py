import sys
import pandas as pd
from tkinter import *
from tkinter import filedialog as fd

def get_file_path(file_entry) -> str:
    global file_path
    file_path = fd.askopenfilename(title="Select file", filetypes=(("CSV Files", "*.csv"),))
    file_entry.delete(0, END)
    file_entry.insert(0, file_path)

# Tkinter functions
def run_and_close(event=None):
    #call function
    print(file_path)
    close()

def close(event=None):
    master.withdraw()
    sys.exit()

# Tkinter interface
master = Tk()

master.title("Trigger Duplicator")

entry_box = Entry(master, text="", width=50)
entry_box.grid(row=0, column=1, sticky=W, padx=5)

Label(master, text="Choose file path").grid(row=0, column=0, sticky=W)

Button(master, text="Browse...", width=10, command=lambda: get_file_path(entry_box)).grid(row=0, column=2, sticky=W)
Button(master, text="Ok", command=run_and_close, width=10).grid(row=3, column=1, sticky=E, padx=5)
Button(master, text="Cancel", command=close, width=10).grid(row=3, column=2, sticky=W)

master.bind('<Return>', run_and_close)
master.bind('<Escape>', close)

master.mainloop()
