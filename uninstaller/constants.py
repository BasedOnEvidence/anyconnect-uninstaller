CM_MODULE_NAME = 'Cisco AnyConnect ISE Compliance Module'
ISE_PM_MODULE_NAME = 'Cisco AnyConnect ISE Posture Module'
PM_MODULE_NAME = 'Cisco AnyConnect Posture Module'
NAM_MODULE_NAME = 'Cisco AnyConnect Network Access Manager'
SMC_MODULE_NAME = 'Cisco AnyConnect Secure Mobility Client'
DART_MODULE_NAME = 'Cisco AnyConnect Diagnostics and Reporting Tool'

MODULE_NAMES_LIST = [
    CM_MODULE_NAME,
    ISE_PM_MODULE_NAME,
    PM_MODULE_NAME,
    NAM_MODULE_NAME,
    SMC_MODULE_NAME,
    DART_MODULE_NAME
]

ISTALLATION_INFO_PATHS_LIST = [
    ('HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\'
     'Installer\\UserData\\S-1-5-18\\Products'),
    'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
    ('HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\'
     'Windows\\CurrentVersion\\Uninstall'),
    'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
]
PROFILES_PATH = ('HKLM\\SOFTWARE\\Microsoft\\Windows NT\\'
                 'CurrentVersion\\ProfileList')
