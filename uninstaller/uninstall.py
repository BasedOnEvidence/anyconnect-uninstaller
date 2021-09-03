import subprocess
import os

from uninstaller.getsystemdata import (
    get_reg_uninstall_info,
    make_reg_paths_list_to_remove,
    make_paths_list_to_remove
)
from uninstaller.loader import get_paths_to_delete, get_resource_path
from uninstaller.logger import get_logger


logger = get_logger(__name__)


def run_uninstall_commands(remove_commands_list):
    logger.info(
        subprocess.run('taskkill /F /IM vpnui.exe',  capture_output=True)
    )
    logger.info(
        subprocess.run('taskkill /F /IM vpnagent.exe',  capture_output=True)
    )
    logger.info(subprocess.run('net stop aciseagent',  capture_output=True))
    logger.info(subprocess.run('net stop namlm',  capture_output=True))
    logger.info(subprocess.run('net stop nam',  capture_output=True))
    logger.info(subprocess.run('net stop vpnagent',  capture_output=True))
    for cmd in remove_commands_list:
        logger.info(subprocess.run(cmd,  capture_output=True))


def clear_trash():
    path_list = make_paths_list_to_remove(
        get_paths_to_delete('paths-to-delete.txt')
    )
    start_delete_command = 'rmdir /s /q '
    for path in path_list:
        delete_command = start_delete_command + '"' + path + '"'
        logger.info('{}'.format(delete_command))
        try:
            os.system(delete_command)
        except WindowsError as err:
            logger.warning('Unable to delete {}. {}'.format(
                path, err
            ))
            pass


def clear_registry():
    start_delete_command = 'reg delete '
    end_delete_command = ' /f'
    keys_list = make_reg_paths_list_to_remove(
        get_paths_to_delete('keys-to-delete.txt')
    )
    for key in keys_list:
        logger.info(subprocess.run(
            start_delete_command +
            '"' + key + '"' +
            end_delete_command,
            capture_output=True
        ))


def uninstall_anyconnect():
    logger.info('Program started')
    uninstall_commands_list = get_reg_uninstall_info()
    run_uninstall_commands(uninstall_commands_list)
    executable_path = get_resource_path(
        'PurgeNotifyObjects.exe', 'executable'
    )
    logger.info('Running PurgeNotifyObjects.exe')
    try:
        logger.info(subprocess.run(
            executable_path + ' -confirmDelete',  capture_output=True
        ))
    except WindowsError as err:
        logger.warning(err)
        pass
    clear_trash()
    clear_registry()
    logger.info('All operations completed')
