from datetime import datetime

class Logger(object):
    def __init__(self, gui_instance, log_label):
        self.logs = []
        self.gui_instance = gui_instance
        self.log_label = log_label

    def log(self, log_str: str, log_type: str) -> None:
        """This handles any cases where log is called within a child thread."""
        if log_type == "update":
            self._update_log_label(log_str)
        elif log_type == "instance update":
            self.gui_instance.after(0, self._update_log_label, log_str)
        elif log_type == "record":
            self._record_to_logs(log_str)
        elif log_type == "instance record":
            self.gui_instance.after(0, self._record_to_logs, log_str)
        else:
            raise ValueError("Invalid log type.")
        return None

    def _update_log_label(self, status_str: str) -> None:
        self.log_label.configure(text=status_str)
        return None

    def _record_to_logs(self, log_str: str) -> None:
        self.logs.append("[" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "] " + log_str)
        self._update_log_label(log_str)
        return None

    def get_logs(self) -> str:
        total_logs = ""
        for log_msg in self.logs:
            total_logs += (log_msg + "\n")
        return total_logs

    def clear_log(self) -> None:
        self.logs = []
        return None