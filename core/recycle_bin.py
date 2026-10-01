import ctypes


SHERB_NOCONFIRMATION = 0x00000001
SHERB_NOPROGRESSUI = 0x00000002
SHERB_NOSOUND = 0x00000004


def empty_recycle_bin():
    try:
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(
            None,
            None,
            SHERB_NOCONFIRMATION
            | SHERB_NOPROGRESSUI
            | SHERB_NOSOUND,
        )
        return result == 0
    except (AttributeError, OSError):
        return False
