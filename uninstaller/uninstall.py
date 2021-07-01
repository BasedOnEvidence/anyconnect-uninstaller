import subprocess
import os

from uninstaller.getsystemdata import (
    get_logged_on_user, get_sid_of_logged_on_user, get_uninstall_strings_list
)
from uninstaller.loader import get_paths_to_delete, get_resource_path
from uninstaller.logger import get_logger

# 1. Check this:
# HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
# HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall
# (no need) HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall
# (no need) HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\
#           Installer\UserData\S-1-5-18\Products\
# 2. Find Cisco Anyconnect remove commands
# 3. Run them
# 4. Clear trash folders
# 5. Clear trash reg keys

logger = get_logger(__name__)


# Функция запускает msiexec /x всех модулей,
# которые видны в programs and features
def run_uninstall_commands(remove_commands_list):
    logger.info(
        subprocess.run('taskkill /F /IM vpnui.exe',  capture_output=True)
    )
    logger.info(
        subprocess.run('taskkill /F /IM vpnagent.exe',  capture_output=True)
    )
    logger.info(subprocess.run('net stop aciseagent',  capture_output=True))
    logger.info(subprocess.run('net stop nam',  capture_output=True))
    logger.info(subprocess.run('net stop namlm',  capture_output=True))
    logger.info(subprocess.run('net stop vpnagent',  capture_output=True))
    for cmd in remove_commands_list:
        logger.info(subprocess.run(cmd,  capture_output=True))


def clear_trash(logged_on_user):
    path_list = get_paths_to_delete('paths-to-delete.txt')
    start_delete_command = 'rmdir /s /q '
    for i in range(len(path_list)):
        if path_list[i].startswith(r"%userprofile%"):
            if logged_on_user != '':
                path_list[i] = path_list[i].replace(
                            r"%userprofile%",
                            'C:\\users\\{}'.format(logged_on_user)
                            )
            else:
                path_list.pop[i]
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


def clear_registry(sid_of_logged_on_user=''):
    if sid_of_logged_on_user != '':
        start_reg_path = 'HKU\\{}'.format(sid_of_logged_on_user)
    else:
        start_reg_path = ''
    start_delete_command = 'reg delete '
    end_delete_command = ' /f'
    keys_list = get_paths_to_delete('keys-to-delete.txt')
    for key in keys_list:
        if key.startswith('HKCU') and start_reg_path != '':
            key = key.replace('HKCU', start_reg_path)
        logger.debug('Deleting {}'.format(key))
        logger.info(subprocess.run(
            start_delete_command +
            '"' + key + '"' +
            end_delete_command,
            capture_output=True
        ))


def uninstall_anyconnect():
    remove_commands_list = get_uninstall_strings_list()
    run_uninstall_commands(remove_commands_list)
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
    logger.info('Getting logged on user info')
    logged_on_user = get_logged_on_user()
    sid_of_logged_on_user = get_sid_of_logged_on_user(logged_on_user)
    logger.info('Logged on user: {}. Sid: {}'.format(
        logged_on_user,
        sid_of_logged_on_user
        ))
    clear_trash(logged_on_user)
    clear_registry(sid_of_logged_on_user)
    logger.info('All operations completed')
