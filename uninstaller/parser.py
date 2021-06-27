from uninstaller.constants import MODULE_NAMES_LIST


def get_reg_paths(list):
    reg_paths = []
    for item in list:
        if 'HKEY' in item:
            reg_paths.append(item)
    return reg_paths


def get_module_name(reg_data):
    try:
        for name in MODULE_NAMES_LIST:
            if name in reg_data[-1]:
                return name
    except IndexError:
        pass
    return None


def get_uninstall_string(reg_data):
    MSIEXEC_LIST = ['MsiExec.exe', 'msiexec.exe', 'MSIEXEC.exe', 'MSIEXEC.EXE']
    try:
        for str in MSIEXEC_LIST:
            if str in reg_data[-1]:
                return reg_data[-1].rstrip('\r\n')
    except IndexError:
        pass
    return None


def get_active_username(qwinsta_data):
    username = ''
    try:
        for i in range(len(qwinsta_data)):
            if qwinsta_data[i][0] == '>':
                username = qwinsta_data[i+1]
                break
    except IndexError:
        pass
    return username


def get_sid_of_user(reg_data, user):
    pass
