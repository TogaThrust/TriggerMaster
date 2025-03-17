from tkinter import messagebox

class ErrorHandler:
    def __init__(self, logger):
        self.logger = logger
        self.error_messages = {"Invalid File Path": ["Invalid File Path", "File does not exist!"],

                               "UnicodeDecodeError": ["Read Error", "Program is having trouble reading your file."
                                                      + " Ensure CSV is saved as UTF-8 (*CSV) file."],

                               "AttributeError": ["Object Error", "Unable to perform critical operations on file."],

                               "RuntimeError": ["Runtime Error",
                                                "Program encountered an error in writing data into CSV."
                                                + " Invalid number of columns or invalid data type."],

                               "EmptyDataError": ["Empty Data Error", "Reader fails to fetch "
                                                  + "readable data from the CSV file."],

                               "InvalidDateFormat": ["Invalid Date Format", "Input a different date format."],

                               "LimitWarning": ["Limit Warning", "Data is very large, "
                                                + "might lead to longer processing time. Run anyway?"],

                               "DateIdentifierWarning": ["Date Identifier Warning",
                                                         "Program cannot detect last 2 date columns. Continue anyway?"]
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
        self.logger.log(log_str, log_type="instance record")
        return error_type