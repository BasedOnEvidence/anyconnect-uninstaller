import winreg
import os
import shutil
import ctypes
import sys

'''
1. Check this:
HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall
HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall
(no need) HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall
2. Find Cisco Anyconnect remove commands
3. Run them
4. Clear trash manualy
'''


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except WindowsError:
        return False


def get_subkey_value_data(winreg_root_key, path, key, key_num, value_name):
    current_sub_key = winreg.EnumKey(
        key, key_num
    )
    sub_path = path + "\\" + current_sub_key
    sub_key = winreg.OpenKey(
        winreg_root_key, sub_path, 0, winreg.KEY_READ
    )
    try:
        value = None
        regtype = None
        value, regtype = winreg.QueryValueEx(
            sub_key, value_name
        )
    except WindowsError:
        pass
    finally:
        winreg.CloseKey(sub_key)
        return current_sub_key, value


def get_subkey_name_from_path(path):
    cur_str = path
    if "\\" in path:
        subkey_name = cur_str.split("\\")[-1]
    else:
        subkey_name = cur_str
    return subkey_name


def get_parent_key_path(path):
    cur_str = path
    suffix = get_subkey_name_from_path(cur_str)
    if suffix != "":
        suffix = "\\" + suffix
        cur_str = cur_str[:len(cur_str)-len(suffix)]
    else:
        cur_str = ""
    return cur_str


def split_keys_list(keys_list):
    HKCR_list = []
    HKLM_list = []
    HKU_list = []
    HKCR_index = keys_list.index("HKEY_CLASSES_ROOT")
    HKLM_index = keys_list.index("HKEY_LOCAL_MACHINE")
    HKU_index = keys_list.index("HKEY_USERS")
    for i in range(HKCR_index + 1, HKLM_index):
        HKCR_list.append(keys_list[i])
    for i in range(HKLM_index + 1, HKU_index):
        HKLM_list.append(keys_list[i])
    for i in range(HKU_index + 1, len(keys_list)):
        HKU_list.append(keys_list[i])
    return HKCR_list, HKLM_list, HKU_list


def get_paths_to_delete(filename):
    with open(filename, "r") as key_file:
        paths_list = key_file.read().splitlines()
    key_file.close()
    return paths_list


def get_user_folders():
    path = "C:/Users"
    for dirs, folder, files in os.walk(path):
        dir_list = folder
        break
    return dir_list


def delete_subkey(winreg_root_key, path):
    try:
        parent_key_path = get_parent_key_path(path)
        parent_key = winreg.OpenKey(
            winreg_root_key, parent_key_path, 0, winreg.KEY_ALL_ACCESS
        )
        subkey_name = get_subkey_name_from_path(path)
        winreg.DeleteKey(parent_key, subkey_name)
        winreg.CloseKey(parent_key)
    except WindowsError:
        pass


def delete_value(winreg_root_key, path, value_name):
    try:
        target_key = winreg.OpenKey(
            winreg.winreg_root_key, path, 0, winreg.KEY_ALL_ACCESS
        )
        winreg.DeleteValue(target_key, value_name)
        winreg.CloseKey(target_key)
    except WindowsError:
        pass


def get_subkeys_names(winreg_root_key, path):
    key_num = 0
    subkeys_list = []
    try:
        root_key = winreg.OpenKey(
            winreg_root_key, path, 0, winreg.KEY_READ
        )
        while True:
            current_sub_key = winreg.EnumKey(
                root_key, key_num
            )
            subkeys_list.append(current_sub_key)
            key_num += 1
    except WindowsError:
        pass
    finally:
        winreg.CloseKey(root_key)
        return subkeys_list


def filter_sids(sids_list):
    i = 0
    while i < len(sids_list):
        if 41 < len(sids_list[i]) < 50:
            i += 1
        else:
            del sids_list[i]


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
                            if uninstall_string_data != ANYCONNECT_DEF_STRING:
                                remove_commands_list.append(
                                    uninstall_string_data
                                )
                            else:
                                core_module_uninstall = uninstall_string_data
            key_num += 1
        winreg.CloseKey(registry_key_with_uninstall_info)
    except WindowsError:
        pass
    finally:
        if core_module_uninstall != "":
            remove_commands_list.append(core_module_uninstall)
        return remove_commands_list


def run_uninstall_commands(remove_commands_list):
    commands_count = len(remove_commands_list)
    os.system("net stop aciseagent")
    os.system("net stop nam")
    os.system("net stop namlm")
    os.system("net stop vpnagent")
    for i in range(commands_count):
        print(remove_commands_list[i])
        os.system(remove_commands_list[i])


def clear_trash():
    path_list = get_paths_to_delete("paths_to_delete.txt")
    dir_list = get_user_folders()
    for i in range(len(path_list)):
        if path_list[i].startswith("\\"):
            for j in range(len(dir_list)):
                dir_to_rm = "C:\\users\\" + dir_list[j] + path_list[i]
                shutil.rmtree(dir_to_rm, ignore_errors=True)
        else:
            try:
                shutil.rmtree(path_list[i], ignore_errors=True)
            except WindowsError:
                pass


def delete_subkeys_list(winreg_root_key, keys_list, user_sids=[]):
    if user_sids != []:
        for i in range(len(user_sids)):
            for j in range(len(keys_list)):
                path_to_delete = user_sids[i] + "\\" + keys_list[j]
                delete_subkey(winreg_root_key, path_to_delete)
    else:
        for i in range(len(keys_list)):
            delete_subkey(winreg_root_key, keys_list[i])


def clear_registry():
    user_sids = []
    user_sids.extend(get_subkeys_names(winreg.HKEY_USERS, ""))
    filter_sids(user_sids)
    keys_list = get_paths_to_delete("keys_to_delete.txt")
    HKCR_keys_list, HKLM_keys_list, HKU_keys_list = split_keys_list(keys_list)
    delete_subkeys_list(winreg.HKEY_CLASSES_ROOT, HKCR_keys_list)
    delete_subkeys_list(winreg.HKEY_LOCAL_MACHINE, HKLM_keys_list)
    delete_subkeys_list(winreg.HKEY_USERS, HKU_keys_list, user_sids)


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
    remove_commands_list.extend(get_anyconnect_uninstall_commands(
        winreg.HKEY_CURRENT_USER, UNINSTALL_HKCU_PATH
    ))
    run_uninstall_commands(remove_commands_list)


def main():
    if is_admin():
        uninstall_anyconnect()
        clear_registry()
        clear_trash()
        print("\nDone! Restart required.")
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )


if __name__ == "__main__":
    main()
