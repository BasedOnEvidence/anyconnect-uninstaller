import subprocess
import sys

from uninstaller.logger import get_logger

logger = get_logger(__name__)


def make_list_from_cmd_output(command, splitter=None):
    try:
        out_str = subprocess.check_output(command).decode(sys.stdout.encoding)
        result_list = out_str.split(splitter)
    except (subprocess.CalledProcessError, WindowsError) as err:
        result_list = []
        logger.warning(
            'Unable to get output from command: {}. {}'.format(command, err)
        )
        pass
    except UnicodeEncodeError as err:
        logger.error(err)
    return result_list
