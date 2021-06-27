import subprocess


def make_list_from_cmd_output(command, splitter=None):
    try:
        out_str = subprocess.check_output(command).decode("utf-8")
        result_list = out_str.split(splitter)
    except (subprocess.CalledProcessError, WindowsError):
        result_list = []
    return result_list
