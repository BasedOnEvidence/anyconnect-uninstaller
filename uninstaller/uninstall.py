import os
import time

from uninstaller.getsystemdata import (
    get_logged_on_user, get_sid_of_logged_on_user, get_uninstall_strings_list
)
from uninstaller.loader import get_paths_to_delete, get_resource_path

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


def reboot_system(restart_param):
    # reboot_status = False
    user_reboot_desire = restart_param
    if restart_param == 'ask':
        user_reboot_desire = input(
            "Do you want to reboot this machine? [Y/N]: "
        )
    if (user_reboot_desire == 'y' or
            user_reboot_desire == 'Y' or
            user_reboot_desire == 'yes'):
        os.system("shutdown -r -t 0")
    else:
        print("Reboot cancelled")
    time.sleep(1)


# Функция запускает msiexec /x всех модулей,
# которые видны в programs and features
def run_uninstall_commands(remove_commands_list):
    commands_count = len(remove_commands_list)
    os.system('net stop aciseagent')
    os.system('net stop nam')
    os.system('net stop namlm')
    os.system('net stop vpnagent')
    os.system('taskkill /F /IM vpnui.exe')
    os.system('taskkill /F /IM vpnagent.exe')
    for i in range(commands_count):
        print(remove_commands_list[i])
        os.system(remove_commands_list[i])


def clear_trash(logged_on_user):
    path_list = get_paths_to_delete('paths-to-delete.txt')
    delete_command = "rmdir /s /q "
    for i in range(len(path_list)):
        if path_list[i].startswith(r"%userprofile%"):
            path_list[i] = path_list[i].replace(
                        r"%userprofile%",
                        "C:\\users\\{}".format(logged_on_user)
                        )
        print("Deleting {}".format(path_list[i]))
        os.system(delete_command + '"' + path_list[i] + '"')


def clear_registry(sid_of_logged_on_user=""):
    start_reg_path = "HKU\\{}".format(sid_of_logged_on_user)
    start_delete_command = "reg delete "
    end_delete_command = " /f"
    keys_list = get_paths_to_delete('keys-to-delete.txt')
    for i in range(len(keys_list)):
        if keys_list[i].startswith("HKCU"):
            keys_list[i] = keys_list[i].replace("HKCU", start_reg_path)
        print("Deleting {}".format(keys_list[i]))
        os.system(
            start_delete_command +
            '"' + keys_list[i] + '"' +
            end_delete_command
        )


def uninstall_anyconnect(restart_param):
    remove_commands_list = get_uninstall_strings_list()
    run_uninstall_commands(remove_commands_list)
    executable_path = get_resource_path(
        'PurgeNotifyObjects.exe', 'executable'
    )
    os.system(executable_path + ' -confirmDelete')
    logged_on_user = get_logged_on_user()
    sid_of_logged_on_user = get_sid_of_logged_on_user(logged_on_user)
    print("Logged on user: {}. Sid: {}".format(logged_on_user,
                                               sid_of_logged_on_user))
    clear_trash(logged_on_user)
    clear_registry(sid_of_logged_on_user)
    reboot_system(restart_param)
