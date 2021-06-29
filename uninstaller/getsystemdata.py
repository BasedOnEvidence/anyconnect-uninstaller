from uninstaller.logger import get_logger
from uninstaller.cmdhandler import make_list_from_cmd_output
from uninstaller.parser import (
    get_module_name,
    get_reg_paths,
    get_uninstall_string,
    get_active_username,
    get_sid_of_user
)
from uninstaller.constants import SMC_MODULE_NAME

ISTALLATION_INFO_PATH_LIST = [
    ('HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\'
     'Installer\\UserData\\S-1-5-18\\Products'),
    'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
    ('HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\'
     'Windows\\CurrentVersion\\Uninstall'),
    'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
]
PROFILES_PATH = ('HKLM\\SOFTWARE\\Microsoft\\Windows NT\\'
                 'CurrentVersion\\ProfileList')
SEARCHSTR = 'Anyconnect'

logger = get_logger(__name__)


def get_uninstall_data():
    uninstall_data = {}
    for global_path in ISTALLATION_INFO_PATH_LIST:
        search_cmd = (
            'reg query "' + global_path + '" /f ' + SEARCHSTR + ' /s /d'
        )
        paths_list = get_reg_paths(
            make_list_from_cmd_output(search_cmd, '\r\n')
        )
        for path in paths_list:
            get_name_cmd = 'reg query "' + path + '" /v DisplayName'
            get_uninst_cmd = 'reg query "' + path + '" /v UninstallString'
            module_name = get_module_name(
                make_list_from_cmd_output(get_name_cmd, '  ')
            )
            uninstall_string = get_uninstall_string(
                make_list_from_cmd_output(get_uninst_cmd, '  ')
            )
            if module_name and uninstall_string:
                if uninstall_string not in [
                    uninstall_data[key][1] for key in uninstall_data
                ]:
                    uninstall_data[path] = [module_name, uninstall_string]
                    logger.info('Path {} added to data'.format(path))
    return uninstall_data


def get_logged_on_user():
    try:
        qwinsta_data = make_list_from_cmd_output('qwinsta')
        logged_on_user = get_active_username(qwinsta_data)
    except WindowsError as err:
        logger.warning(
            'Unable to get username of logged on user!. {}'.format(err)
        )
        logged_on_user = ''
        pass
    return logged_on_user


def get_sid_of_logged_on_user(logged_on_user):
    if logged_on_user == '':
        return ''
    get_profiles_path_list_cmd = 'reg query "' + PROFILES_PATH + '"'
    raw_data = make_list_from_cmd_output(get_profiles_path_list_cmd, '\r\n')
    paths_list = get_reg_paths(raw_data)
    paths_list.pop(0)  # Delete root path from this list
    try:
        for path in paths_list:
            current_key_list = make_list_from_cmd_output(
                'reg query \"{}\" /v ProfileImagePath '.format(path), '\r\n'
            )
            sid_of_logged_on_user = get_sid_of_user(
                current_key_list, path, logged_on_user
            )
            if sid_of_logged_on_user != '':
                break
    except WindowsError as err:
        logger.warning('Unable to get sid of logged on user!. {}'.format(err))
        sid_of_logged_on_user = ''
        pass
    return sid_of_logged_on_user


def get_uninstall_strings_list():
    uninstall_strings_list = []
    data = get_uninstall_data()
    is_SMC_exist = False
    for key in data:
        uninstall_string = data[key][1] + ' /qn /norestart'
        module_name = data[key][0]
        if module_name == SMC_MODULE_NAME:
            is_SMC_exist = True
            SMC_uninstall_string = uninstall_string
        else:
            uninstall_strings_list.append(uninstall_string)
            logger.info('Uninstall command {} added to uninstall list'.format(
                uninstall_string
            ))
    if is_SMC_exist:
        uninstall_strings_list.append(SMC_uninstall_string)
        logger.info('Uninstall command {} added to uninstall list'.format(
            SMC_uninstall_string
        ))
    return uninstall_strings_list
