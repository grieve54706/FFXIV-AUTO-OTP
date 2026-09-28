import time
import ctypes
import pyautogui

import win32gui
import win32con
import win32process

# Disable pyautogui fail-safe (moving mouse to corner won't abort)
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


def find_launcher_window(title_substring: str = "FINAL FANTASY XIV 繁體中文版") -> int | None:
    """Find the FFXIV launcher window by title substring. Returns HWND or None."""
    result = []

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_substring in title:
                result.append(hwnd)

    win32gui.EnumWindows(enum_callback, None)
    return result[0] if result else None


def focus_window(hwnd: int) -> bool:
    """Bring the window to foreground."""
    try:
        # Restore if minimized
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # Try SetForegroundWindow directly first
        try:
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception:
            pass

        # Workaround: attach to the foreground thread to gain permission
        foreground_hwnd = win32gui.GetForegroundWindow()
        if foreground_hwnd:
            foreground_tid, _ = win32process.GetWindowThreadProcessId(foreground_hwnd)
            target_tid, _ = win32process.GetWindowThreadProcessId(hwnd)
            if foreground_tid != target_tid:
                ctypes.windll.user32.AttachThreadInput(foreground_tid, target_tid, True)
                win32gui.SetForegroundWindow(hwnd)
                ctypes.windll.user32.AttachThreadInput(foreground_tid, target_tid, False)
            else:
                win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False


def enter_otp_and_login(otp_code: str, launcher_title: str = "FINAL FANTASY XIV 繁體中文版",
                        delay: float = 0.3) -> str:
    """
    Find the launcher, focus it, type the OTP, and press Enter.
    Returns a status message string.
    """
    hwnd = find_launcher_window(launcher_title)
    if hwnd is None:
        return "找不到 FFXIV 啟動器視窗"

    if not focus_window(hwnd):
        return "無法將啟動器視窗帶到前景"

    time.sleep(max(delay, 0.5))

    # Type the 6-digit OTP code (field should be empty on login page)
    pyperclip.copy(otp_code)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)

    # Press Enter to submit login
    pyautogui.press("enter")

    return "已輸入驗證碼並送出登入"
