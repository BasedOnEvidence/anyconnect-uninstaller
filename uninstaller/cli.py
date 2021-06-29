import argparse
import time
import os


def get_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r',
                        '--restart',
                        choices=['yes', 'no', 'ask'],
                        default='ask',
                        help='set restart parametr')
    return parser


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
