import winreg
import os
import ctypes
import sys
import subprocess

'''
1. Check this:
HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall
HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall
(no need) HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall
2. Find Cisco Anyconnect remove commands
3. Run them
4. Clear trash folders
5. Clear trash reg keys
'''


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except WindowsError:
        return False


# По пути, названию ключа, его номеру и названию значения вернуть значение
# Переписать виндовыми функциями конечно
def get_subkey_value_data(winreg_root_key, path, key, key_num, value_name):
    current_sub_key = winreg.EnumKey(
        key, key_num
    )
    sub_path = path + "\\" + current_sub_key
    try:
        sub_key = winreg.OpenKey(
            winreg_root_key, sub_path, 0, winreg.KEY_READ
        )
        value = None
        regtype = None
        value, regtype = winreg.QueryValueEx(
            sub_key, value_name
        )
        winreg.CloseKey(sub_key)
    except WindowsError:
        pass
    finally:
        return current_sub_key, value


def get_paths_to_delete(filename):
    with open(filename, "r") as path_file:
        paths_list = path_file.read().splitlines()
    path_file.close()
    return paths_list


def get_logged_on_user():
    windows_sessions = subprocess.check_output("qwinsta").decode("utf-8")
    values_list = windows_sessions.split()
    logged_on_user = ""
    for i in range(len(values_list)):
        try:
            if values_list[i][0] == '>':
                logged_on_user = values_list[i+1]
                break
        except IndexError:
            pass
    return logged_on_user


def get_sid_of_logged_on_user(logged_on_user):
    cmd_to_get_sid = (
                     "wmic useraccount where name='{}' get sid"
                     .format(logged_on_user)
    )
    windows_sid_information = (
        subprocess.check_output(cmd_to_get_sid).decode("utf-8")
    )
    values_list = windows_sid_information.split()
    sid_of_logged_on_user = values_list[1]
    return sid_of_logged_on_user


# Получение команд удаления всех модулей anyconnect, которые установлены
def get_anyconnect_uninstall_commands(winreg_root_key, reg_path):
    MSIEXEC_DEF_SUBSTRING = "MsiExec.exe /X"
    ANYCONNECT_DEF_SUBSTRING = "Cisco AnyConnect"
    ANYCONNECT_DEF_STRING = "Cisco AnyConnect Secure Mobility Client"
    core_module_uninstall = ""
    display_name_value_name = "DisplayName"
    uninstall_string_value_name = "UninstallString"
    remove_commands_list = []
    key_num = 0
    try:
        registry_key_with_uninstall_info = winreg.OpenKey(
            winreg_root_key, reg_path, 0, winreg.KEY_READ
        )
        while True:
            sub_key, display_name_data = get_subkey_value_data(
                winreg_root_key, reg_path, registry_key_with_uninstall_info,
                key_num, display_name_value_name
            )
            if display_name_data:
                if ANYCONNECT_DEF_SUBSTRING in display_name_data:
                    _, uninstall_string_data = get_subkey_value_data(
                        winreg_root_key, reg_path,
                        registry_key_with_uninstall_info,
                        key_num, uninstall_string_value_name
                    )
                    if uninstall_string_data:
                        if MSIEXEC_DEF_SUBSTRING in uninstall_string_data:
                            uninstall_string_data = uninstall_string_data + \
                                                    " /qn /norestart"
                            # Удаление основного модуля добавим в конец списка
                            if uninstall_string_data != ANYCONNECT_DEF_STRING:
                                remove_commands_list.append(
                                    uninstall_string_data
                                )
                            else:
                                core_module_uninstall = uninstall_string_data
            # Key_num нужен для уникальных сабкеев.
            # Явно лишняя вся эта история, надо убрать
            key_num += 1
        winreg.CloseKey(registry_key_with_uninstall_info)
    except WindowsError:
        pass
    finally:
        if core_module_uninstall != "":
            remove_commands_list.append(core_module_uninstall)
        return remove_commands_list


# Функция запускает msiexec /x всех модулей,
# которые видны в programs and features
def run_uninstall_commands(remove_commands_list):
    commands_count = len(remove_commands_list)
    os.system("net stop aciseagent")
    os.system("net stop nam")
    os.system("net stop namlm")
    os.system("net stop vpnagent")
    for i in range(commands_count):
        print(remove_commands_list[i])
        os.system(remove_commands_list[i])


def clear_trash(logged_on_user):
    path_list = get_paths_to_delete("paths-to-delete.txt")
    delete_command = "rmdir /s /q "
    for i in range(len(path_list)):
        if path_list[i].startswith(r"%userprofile%"):
            path_list[i] = path_list[i].replace(
                        r"%userprofile%",
                        "C:\\users\\{}".format(logged_on_user)
                        )
        os.system(delete_command + '"' + path_list[i] + '"')


def clear_registry(sid_of_logged_on_user):
    start_reg_path = "HKU\\{}".format(sid_of_logged_on_user)
    start_delete_command = "reg delete "
    end_delete_command = " /f"
    keys_list = get_paths_to_delete("keys-to-delete.txt")
    for i in range(len(keys_list)):
        if keys_list[i].startswith("HKCU"):
            keys_list[i] = keys_list[i].replace("HKCU", start_reg_path)
        os.system(
            start_delete_command +
            '"' + keys_list[i] + '"' +
            end_delete_command
        )


def uninstall_anyconnect():
    UNINSTALL_HKLM_PATH = "SOFTWARE\\Microsoft\\" \
                          "Windows\\CurrentVersion\\Uninstall"
    UNINSTALL_HKLM_PATH_X32_COMPATIBILITY = "SOFTWARE\\WOW6432Node\\" \
                                            "Microsoft\\Windows\\" \
                                            "CurrentVersion\\Uninstall"
    UNINSTALL_HKCU_PATH = "SOFTWARE\\Microsoft\\" \
                          "Windows\\CurrentVersion\\Uninstall"
    remove_commands_list = []
    remove_commands_list.extend(get_anyconnect_uninstall_commands(
        winreg.HKEY_LOCAL_MACHINE, UNINSTALL_HKLM_PATH
    ))
    remove_commands_list.extend(get_anyconnect_uninstall_commands(
        winreg.HKEY_LOCAL_MACHINE, UNINSTALL_HKLM_PATH_X32_COMPATIBILITY
    ))
    # Далее ожидается extend [], это пользовательская ветка администратора
    remove_commands_list.extend(get_anyconnect_uninstall_commands(
        winreg.HKEY_CURRENT_USER, UNINSTALL_HKCU_PATH
    ))
    run_uninstall_commands(remove_commands_list)


def main():
    if is_admin():
        uninstall_anyconnect()
        logged_on_user = get_logged_on_user()
        sid_of_logged_on_user = get_sid_of_logged_on_user(logged_on_user)
        clear_trash(logged_on_user)
        clear_registry(sid_of_logged_on_user)
        os.system("pause")
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1
        )


if __name__ == "__main__":
    main()
