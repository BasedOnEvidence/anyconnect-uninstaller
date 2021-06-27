from uninstaller.cmdhandler import make_list_from_cmd_output
from uninstaller.parser import (
    get_module_name, get_reg_paths, get_uninstall_string, get_active_username
)
from uninstaller.constants import SMC_MODULE_NAME

ISTALLATION_INFO_PATH_LIST = [
    'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
    ('HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\'
     'Windows\\CurrentVersion\\Uninstall'),
    ('HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\'
     'Installer\\UserData\\S-1-5-18\\Products'),
    'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
]
PROFILES_PATH = ('HKLM\\SOFTWARE\\Microsoft\\Windows NT\\'
                 'CurrentVersion\\ProfileList')
SEARCHSTR = 'Anyconnect'


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
    return uninstall_data


def get_logged_on_user():
    qwinsta_data = make_list_from_cmd_output('qwinsta')
    return get_active_username(qwinsta_data)


def get_sid_of_logged_on_user(logged_on_user):
    get_profiles_path_list_cmd = 'reg query "' + PROFILES_PATH + '"'
    raw_data = make_list_from_cmd_output(get_profiles_path_list_cmd, '\r\n')
    paths_list = get_reg_paths(raw_data)
    try:
        for i in range(1, len(paths_list)):
            current_key_list = make_list_from_cmd_output(
                "reg query \"{}\" /v ProfileImagePath ".format(paths_list[i]),
                "\r\n"
            )
            # Берем 3-ий элемент с конца, сплитим эту строку по пробелам
            # Из полученного списка берем последний элемент-строку
            # И делаем ее в нижнем регистре
            if current_key_list[-3].split()[-1].lower() == (
                    ("C:\\Users\\"+logged_on_user).lower()):
                # Сплитим путь по обратному слешу, в самом конце пути лежит сид
                sid_of_logged_on_user = paths_list[i].split("\\")[-1]
                break
    except WindowsError:
        sid_of_logged_on_user = ''
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
    if is_SMC_exist:
        uninstall_strings_list.append(SMC_uninstall_string)
    return uninstall_strings_list
