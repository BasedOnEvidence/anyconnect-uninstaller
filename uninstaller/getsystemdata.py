from uninstaller.logger import get_logger
from uninstaller.cmdhandler import make_list_from_cmd_output
from uninstaller.parser import (
    get_module_name,
    get_reg_paths,
    get_uninstall_string,
    filter_HKU_sids,
    get_profile_path
)
from uninstaller.constants import (
    SMC_MODULE_NAME,
    NAM_MODULE_NAME,
    MODULE_NAMES_LIST,
    ISTALLATION_INFO_PATHS_LIST,
    PROFILES_PATH
)


logger = get_logger(__name__)


def get_product_reg_paths_list(root_path):
    paths_list = []
    for search_str in MODULE_NAMES_LIST:
        search_cmd = (
            'reg query "' + root_path + '" /f "' + search_str + '" /s /d'
        )
        paths_list.extend(get_reg_paths(
            make_list_from_cmd_output(search_cmd, '\r\n')
        ))
        if paths_list != []:
            logger.info('Product reg paths found:\n{}'.format(
                '\n'.join(paths_list)
            ))
        else:
            logger.info('No product reg paths in {}'.format(
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


def get_reg_uninstall_info():
    uninstall_commands_list = []
    uninstall_paths_list = []
    for root_path in ISTALLATION_INFO_PATHS_LIST:
        uninstall_paths_list.extend(get_product_reg_paths_list(root_path))
    data = get_uninstall_data(uninstall_paths_list)
    is_SMC_exist = False
    is_NAM_exist = False
    for key in data:
        uninstall_string = data[key][1] + ' /qn /norestart'
        module_name = data[key][0]
        if module_name == SMC_MODULE_NAME:
            is_SMC_exist = True
            SMC_uninstall_string = uninstall_string
        elif module_name == NAM_MODULE_NAME:
            is_NAM_exist = True
            NAM_uninstall_string = uninstall_string
        else:
            uninstall_commands_list.append(uninstall_string)
            logger.info('Uninstall command {} added to uninstall list'.format(
                uninstall_string
            ))
    if is_SMC_exist:
        uninstall_commands_list.append(SMC_uninstall_string)
        logger.info('Uninstall cmd for SMC {} added to uninstall list'.format(
            SMC_uninstall_string
        ))
    if is_NAM_exist:
        uninstall_commands_list.insert(0, NAM_uninstall_string)
        logger.info('Uninstall cmd for NAM {} added to uninstall list'.format(
            NAM_uninstall_string
        ))
    return uninstall_commands_list


def get_system_sids():
    return filter_HKU_sids(get_reg_paths(
        make_list_from_cmd_output('reg query HKU', '\r\n')
    ))


def get_user_profile_path(sid):
    get_profiles_path_cmd = (
        'reg query "{}\\{}" /v ProfileImagePath'.format(PROFILES_PATH, sid)
    )
    return get_profile_path(make_list_from_cmd_output(get_profiles_path_cmd))


def make_reg_paths_list_to_remove(unfiltered_keys_list):
    keys_list = []
    keys_list.extend(get_product_reg_paths_list(
        'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\'
        'Installer\\UserData\\S-1-5-18\\Products'
    ))
    if keys_list != []:
        logger.warning('Bad anyconnect installation detected!!')
    else:
        logger.info('The program uninstalled anyconnect correctly!!')
    keys_list.extend(get_product_reg_paths_list('HKCR\\Installer\\Products'))
    keys_list.extend(get_product_reg_paths_list(
        'HKLM\\SOFTWARE\\Classes\\Installer\\Products'
    ))
    keys_list.extend(get_product_reg_paths_list(
        'HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\'
        'CurrentVersion\\Uninstall'
    ))
    sids_list = get_system_sids()
    for reg_path in unfiltered_keys_list:
        if reg_path.startswith('HKCU'):
            for sid in sids_list:
                new_reg_path = reg_path.replace('HKCU', 'HKU\\' + sid)
                keys_list.append(new_reg_path)
                logger.info(
                    'Reg path {} converted to {} and added to rm list'.format(
                        reg_path, new_reg_path
                    )
                )
        else:
            keys_list.append(reg_path)
    return keys_list


def make_paths_list_to_remove(unfiltered_paths_list):
    paths_list = []
    sids_list = get_system_sids()
    logger.info('Sids:\n{}'.format('\n'.join(sids_list)))
    for path in unfiltered_paths_list:
        if path.startswith(r"%userprofile%"):
            for sid in sids_list:
                user_profile_path = get_user_profile_path(sid)
                if user_profile_path:
                    new_path = path.replace(
                        r"%userprofile%", user_profile_path
                    )
                    paths_list.append(new_path)
                    logger.info(
                        'Path {} converted to {} and added to rm list'.format(
                            path, new_path
                        )
                    )
        else:
            paths_list.append(path)
    return paths_list
