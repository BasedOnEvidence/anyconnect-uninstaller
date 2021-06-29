import subprocess

from uninstaller.logger import get_logger

logger = get_logger(__name__)


def make_list_from_cmd_output(command, splitter=None):
    try:
        out_str = subprocess.check_output(command).decode("utf-8")
        result_list = out_str.split(splitter)
    except (subprocess.CalledProcessError, WindowsError) as err:
        result_list = []
        logger.warning(
            'Unable to get output from command: {}. {}'.format(command, err)
        )
        pass
    return result_list
