from uninstaller.getsystemdata import (
    get_sid_of_logged_on_user,
    get_logged_on_user,
    get_uninstall_data,
)
from uninstaller.parser import (
    get_reg_paths,
    get_module_name,
    get_uninstall_string
)
from uninstaller.cmdhandler import make_list_from_cmd_output
from uninstaller.constants import MODULE_NAMES_LIST


ADMIN_SID = 'S-1-5-21-2611278916-3226575234-1263985935-1001'
ADMIN_LOGIN = 'admin'
REG_PATHS_LIST = [
    'HKEY_LOCAL_MACHINE\\804CCF31B0990624C87DCD25F07F44EB\\InstallProperties',
    'HKEY_LOCAL_MACHINE\\9B1783E08C081B245939C525BE1227AF\\InstallProperties',
    'HKEY_LOCAL_MACHINE\\A2F9005C5215F9E498AA68083AD26AAA\\InstallProperties',
    'HKEY_LOCAL_MACHINE\\A8F916041A76B2445829A1EA2F7B1F95\\InstallProperties',
    'HKEY_LOCAL_MACHINE\\BBED51B69BA2DD24E8FC28FEF812CC96\\InstallProperties'
]


def get_resource_path(file_name):
    return 'tests/fixtures/{}'.format(file_name)


def read(file_name):
    path = get_resource_path(file_name)
    with open(path, 'r') as fixture:
        return fixture.read()


def test_cmd_handler():
    assert 'REG' == make_list_from_cmd_output('reg /?')[0]


def test_user_data():
    assert ADMIN_LOGIN == get_logged_on_user()
    assert ADMIN_SID == get_sid_of_logged_on_user(ADMIN_LOGIN)


def test_uninstall_data():
    reg_uninstall_paths_list = read('reg-uninstall-paths.txt').split('\n')
    uninstall_data = get_uninstall_data(reg_uninstall_paths_list)
    for key in uninstall_data:
        module_name = uninstall_data[key][0]
        assert module_name in MODULE_NAMES_LIST
    assert len(uninstall_data) < 7


def test_parser():
    reg_uninstall_paths_list = read('reg-uninstall-paths.txt').split('\n')
    assert reg_uninstall_paths_list == get_reg_paths(
        reg_uninstall_paths_list
    )
    assert REG_PATHS_LIST == get_reg_paths(
        read('raw-reg-paths.txt').split('\n')
    )
    assert 'Cisco AnyConnect Secure Mobility Client' == (
        get_module_name(read('reg-display-name.txt').split('  '))
    )
    assert 'MsiExec.exe /X{6B15DEBB-2AB9-1111-8ECF-82EF8F21CC69}' == (
        get_uninstall_string(read('reg-uninstall-string.txt').split('  '))
    )
