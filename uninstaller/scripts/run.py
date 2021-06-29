import ctypes
import sys

from uninstaller.cli import get_args_parser, reboot_system
from uninstaller.uninstall import uninstall_anyconnect


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except WindowsError:
        return False


def main():
    if is_admin():
        parser = get_args_parser()
        args = parser.parse_args()
        uninstall_anyconnect()
        reboot_system(args.restart)
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1
        )


if __name__ == "__main__":
    main()
