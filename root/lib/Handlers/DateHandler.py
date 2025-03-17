from datetime import datetime, timedelta
import re

class DateHandler:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def _babel_to_python_date_format(babel_format):
        # Unfortunately python uses its own date syntax, and most business ppl only understands babel.
        # So we have to deal with this. Implemented this as a class for scalability?
        babel_python_map = {
            'yyyy': '%Y',  # Full year
            'yy': '%y',  # Two-digit year
            'MMM': '%b',  # Abbreviated month name (Jan, Feb, etc.)
            'MM': '%m',  # Zero-padded numeric month
            'M': '%m',  # Non-padded numeric month
            'dd': '%d',  # Zero-padded day
            'd': '%d'  # Non-padded day
        }
        case_sensitive_map = {
            'mmm': 'MMM',
            'mm': 'MM',
            'm': 'M',
            'dd': 'dd',
            'd': 'd',
            'yyyy': 'yyyy',
            'yy': 'yy'
        }
        babel_format = babel_format.strip().replace(" ", "").lower()
        for key, value in case_sensitive_map.items():
            babel_format = babel_format.replace(key, value)
        tokens_sorted_by_length = sorted(babel_python_map.keys(), key=len, reverse=True)
        pattern = re.compile('|'.join(re.escape(token) for token in tokens_sorted_by_length))
        def replace_token(match):
            token = match.group(0)
            return babel_python_map.get(token, token)  # Replace using the map or leave unchanged if not found
        python_format = re.sub(pattern, replace_token, babel_format)
        return python_format

    def generate_dates_between(self, output_format:str, input_format: str = "%d-%m-%Y") -> list:
        """If user input is with DD, generate dates in the stated format, if not we will just generate the months."""
        start_date = datetime.strptime(self.start_date, input_format)
        end_date = datetime.strptime(self.end_date, input_format)
        # Check if the output format is month-based (e.g., 'mm/yyyy') or day-based (e.g., 'dd/mm/yyyy')
        output_format = self._babel_to_python_date_format(output_format)
        if "%d" in output_format:
            current_date = start_date
            result = []
            while current_date <= end_date:
                result.append(current_date.strftime(output_format))
                current_date += timedelta(days=1)
            return result
        else:
            current_date = start_date
            result = []
            while current_date <= end_date:
                result.append(current_date.strftime(output_format))
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            return result