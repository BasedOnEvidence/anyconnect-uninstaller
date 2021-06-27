from uninstaller.getsystemdata import (
    get_sid_of_logged_on_user,
    get_logged_on_user,
    get_uninstall_data,
    get_uninstall_strings_list
)
from uninstaller.cmdhandler import make_list_from_cmd_output
from uninstaller.constants import MODULE_NAMES_LIST


ADMIN_SID = 'S-1-5-21-2611278916-3226575234-1263985935-1001'
ADMIN_LOGIN = 'admin'


def test_cmd_handler():
    assert 'REG' == make_list_from_cmd_output('reg /?')[0]


def test_user_data():
    assert ADMIN_LOGIN == get_logged_on_user()
    assert ADMIN_SID == get_sid_of_logged_on_user(ADMIN_LOGIN)


def test_uninstall_data():
    uninstall_data = get_uninstall_data()
    for key in uninstall_data:
        module_name = uninstall_data[key][0]
        assert module_name in MODULE_NAMES_LIST
    assert len(uninstall_data) < 7
    assert len(get_uninstall_strings_list()) == len(uninstall_data)
