import subprocess

from uninstaller.logger import get_logger

logger = get_logger(__name__)


def make_list_from_cmd_output(command, splitter=None):
    try:
        command = 'chcp 65001 | ' + command
        logger.info('Running: {}'.format(command))
        out_str = subprocess.check_output(command, shell=True).decode('utf-8')
        result_list = out_str.split(splitter)
    except (subprocess.CalledProcessError, WindowsError) as err:
        result_list = []
        logger.warning(
            'Unable to get output from command: {}. {}'.format(command, err)
        )
        pass
    except UnicodeEncodeError as err:
        logger.error(err)
    except Exception as err:
        logger.error(err)
    return result_list
