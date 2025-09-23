import sys

def error_message_detail(error, error_detail: sys):
    """
    Build a detailed error message safely.
    """
    try:
        # get the traceback info
        _, _, exc_tb = error_detail.exc_info()
        if exc_tb is None:
            return f"Error occurred: {error}"

        file_name = exc_tb.tb_frame.f_code.co_filename
        line_no = exc_tb.tb_lineno

        return (
            f"Error occurred in python script [{file_name}] "
            f"at line number [{line_no}] "
            f"with error message [{error}]"
        )

    except Exception as e:
        # fallback: never throw an exception here
        return f"Error occurred: {error}. (Additional error in error handler: {e})"

class CustomException(Exception):
    def init(self, error_message, error_detail: sys):
        super().init(error_message)
        # safely build the error message
        self.error_message = error_message_detail(error_message, error_detail)

    def str(self):
        return self.error_message