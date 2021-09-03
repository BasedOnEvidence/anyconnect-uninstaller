from uninstaller.constants import MODULE_NAMES_LIST
from uninstaller.logger import get_logger
import os


logger = get_logger(__name__)


def get_reg_paths(list):
    reg_paths = []
    for item in list:
        if 'HKEY' in item:
            reg_paths.append(item)
    return reg_paths


def filter_HKU_sids(reg_paths_list):
    HKU_sids = []
    for reg_path in reg_paths_list:
        _, sid = os.path.split(reg_path)
        if (
            (len(sid) > 20) and
            ('_' not in sid) and
            ('.' not in sid)
        ):
            HKU_sids.append(sid)
    return HKU_sids


def get_profile_path(reg_data):
    try:
        if 'sers\\' in reg_data[-1]:
            return reg_data[-1]
        else:
            logger.warning('No profile path in {}'. format(reg_data))
            return None
    except IndexError as err:
        logger.warning(err)
        pass
    return None


def get_module_name(reg_data):
    try:
        for name in MODULE_NAMES_LIST:
            if name in reg_data[-1]:
                return name
        return None
    except IndexError as err:
        logger.warning(err)
        pass
    return None


def get_uninstall_string(reg_data):
    MSIEXEC_LIST = ['MsiExec.exe', 'msiexec.exe', 'MSIEXEC.exe', 'MSIEXEC.EXE']
    try:
        for str in MSIEXEC_LIST:
            if str in reg_data[-1]:
                if ' /I' in reg_data[-1]:
                    logger.warning(
                        'Bad uninstall cmd detected: {}'. format(reg_data[-1])
                    )
                    reg_data[-1] = reg_data[-1].replace(' /I', ' /X')
                    logger.info(
                        'New uninstall cmd: {}'. format(reg_data[-1])
                    )
                return reg_data[-1].rstrip('\r\n')
        return None
    except IndexError as err:
        logger.warning(err)
        pass
    return None
