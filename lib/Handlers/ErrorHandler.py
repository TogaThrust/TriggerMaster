from tkinter import messagebox


class ErrorHandler:
    def __init__(self):
        self.error_messages = {"Invalid File Path": ["Invalid File Path", "File does not exist!"],

                               "UnicodeDecodeError": ["Read Error", "Program is having trouble reading your file."
                                                      + " Ensure CSV is saved as UTF-8 (*CSV) file."],

                               "AttributeError": ["Object Error", "Unable to perform critical operations on file."],

                               "LimitWarning": ["Limit Warning", "Data exceeds output limit. Run anyway?"],

                               "RuntimeError": ["Runtime Error",
                                                "Program encountered an error in writing data into CSV."
                                                + " Actually this is an unfixable error."
                                                + " Try having no adjacent NA values in your input file."],
                               }

    def raise_question_box(self, error_type: str) -> str:
        user_selection = messagebox.askquestion(title=self.error_messages[error_type][0],
                                                message=self.error_messages[error_type][1],
                                                icon=messagebox.WARNING, type=messagebox.OKCANCEL)
        return user_selection

    def raise_error_box(self, error_type: str, log_str: str | None) -> str:
        messagebox.showerror(title=self.error_messages[error_type][0],
                             message=self.error_messages[error_type][1])
        if log_str is None:
            log_str = self.error_messages[error_type][1]
        return log_str