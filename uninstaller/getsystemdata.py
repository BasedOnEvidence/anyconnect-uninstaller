import os

from uninstaller.logger import get_logger
from uninstaller.cmdhandler import make_list_from_cmd_output
from uninstaller.parser import (
    get_module_name,
    get_reg_paths,
    get_uninstall_string,
    get_active_username,
    get_sid_of_user,
    filter_HKU_sids
)
from uninstaller.constants import SMC_MODULE_NAME

ISTALLATION_INFO_PATHS_LIST = [
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


def get_product_reg_paths_list(root_path, levels_to_up=0):
    paths_list = []
    search_cmd = (
        'reg query "' + root_path + '" /f ' + SEARCHSTR + ' /s /d'
    )
    paths_list.extend(get_reg_paths(
        make_list_from_cmd_output(search_cmd, '\r\n')
    ))
    for _ in range(levels_to_up):
        for path_index in range(len(paths_list)):
            new_path, _ = os.path.split(paths_list[path_index])
            new_path = new_path.lstrip('\\')
            paths_list[path_index] = new_path
    if paths_list != []:
        logger.info('Product''s reg paths found:\n{}'.format(
            '\n'.join(paths_list)
        ))
    else:
        logger.info('No product''s reg paths in {}'.format(
            root_path
        ))
    return paths_list


def get_uninstall_data(uninstall_paths_list):
    uninstall_data = {}
    uniq_uninstall_strings = []
    for path in uninstall_paths_list:
        get_name_cmd = 'reg query "' + path + '" /v DisplayName'
        get_uninst_cmd = 'reg query "' + path + '" /v UninstallString'
        module_name = get_module_name(
            make_list_from_cmd_output(get_name_cmd, '  ')
        )
        uninstall_string = get_uninstall_string(
            make_list_from_cmd_output(get_uninst_cmd, '  ')
        )
        if (
            module_name and uninstall_string and
            uninstall_string not in uniq_uninstall_strings
        ):
            uniq_uninstall_strings.append(uninstall_string)
            uninstall_data[path] = [module_name, uninstall_string]
            logger.info(
                'Path {} with module name {} '
                'and uninstall cmd {} added to data'.format(
                    path, module_name, uninstall_string
                )
            )
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


def get_reg_uninstall_info():
    uninstall_commands_list = []
    uninstall_paths_list = []
    for root_path in ISTALLATION_INFO_PATHS_LIST:
        uninstall_paths_list.extend(get_product_reg_paths_list(root_path))
    data = get_uninstall_data(uninstall_paths_list)
    is_SMC_exist = False
    for key in data:
        uninstall_string = data[key][1] + ' /qn /norestart'
        module_name = data[key][0]
        if module_name == SMC_MODULE_NAME:
            is_SMC_exist = True
            SMC_uninstall_string = uninstall_string
        else:
            uninstall_commands_list.append(uninstall_string)
            logger.info('Uninstall command {} added to uninstall list'.format(
                uninstall_string
            ))
    if is_SMC_exist:
        uninstall_commands_list.append(SMC_uninstall_string)
        logger.info('Uninstall command {} added to uninstall list'.format(
            SMC_uninstall_string
        ))
    return uninstall_commands_list


def make_reg_paths_list_to_remove(unfiltered_keys_list):
    keys_list = []
    keys_list.extend(get_product_reg_paths_list(
        'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\'
        'Installer\\UserData\\S-1-5-18\\Products',
        levels_to_up=1
    ))
    if keys_list != []:
        logger.warning('Bad anyconnect installation detected!')
    else:
        logger.info('The program uninstalled the product correctly')
    keys_list.extend(get_product_reg_paths_list('HKCR\\Installer\\Products'))
    keys_list.extend(get_product_reg_paths_list(
        'HKLM\\SOFTWARE\\Classes\\Installer\\Products'
    ))
    keys_list.extend(get_product_reg_paths_list(
        'HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\'
        'CurrentVersion\\Uninstall'
    ))

    HKU_root_paths = filter_HKU_sids(get_reg_paths(
        make_list_from_cmd_output('reg query HKU', '\r\n')
    ))
    for reg_path in unfiltered_keys_list:
        if reg_path.startswith('HKCU'):
            for sid_path in HKU_root_paths:
                new_reg_path = reg_path.replace('HKCU', sid_path)
                logger.info('Reg path {} converted to {}'.format(
                    reg_path, new_reg_path
                ))
                keys_list.append(new_reg_path)
        else:
            keys_list.append(reg_path)
    return keys_list
