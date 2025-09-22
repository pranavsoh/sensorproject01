import sys
import traceback

def error_message_detail(error, error_detail):
    """
    Build a short error message using the current exception info from error_detail.
    error_detail is typically the sys module (passed as sys).
    """
    _, _, exc_tb = error_detail.exc_info()

    if exc_tb is None:
        return f"Error occurred: {error}"

    file_name = exc_tb.tb_frame.f_code.co_filename
    line_no = exc_tb.tb_lineno

    error_message = (
        "Error occurred in python script name [{0}] line number [{1}] error message [{2}]"
        .format(file_name, line_no, error)
    )
    return error_message


class CustomException(Exception):
    def init(self, error_message, error_detail):
        super().init(error_message)
        self.error_message = error_message_detail(error_message, error_detail)

    def str(self):
        return self.error_message