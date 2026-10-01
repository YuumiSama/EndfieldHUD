import mss
import cv2
import numpy as np
import win32gui
from collections import deque
from logger import logger

WINDOW_KEYWORDS = ["Endfield"]


# ==================== 采样档位 ====================
SAMPLE_PRESETS = {
    "saver":       {"interval": 300, "hidden": 2000},
    "normal":      {"interval": 200, "hidden": 1000},
    "performance": {"interval": 100, "hidden": 500},
    "precision":   {"interval": 50,  "hidden": 300},
}


def get_sample_intervals(config, hidden=False):
    """根据档位返回 (可见间隔, 隐藏间隔) 中的对应值"""
    preset = config.get("sample_preset", "normal")
    if preset == "custom":
        visible = config.get("sample_interval_custom", 200)
        hid = config.get("sample_interval_hidden_custom", 1000)
        return hid if hidden else visible
    p = SAMPLE_PRESETS.get(preset, SAMPLE_PRESETS["normal"])
    return p["hidden"] if hidden else p["interval"]


# ==================== 平滑采样器 ====================
class Sampler:
    """对每个角色维护滑动窗口，按中值/平均输出平滑值"""

    def __init__(self, config):
        self.window = max(1, config.get("smooth_window", 5))
        self.mode = config.get("smooth_mode", "median")
        self.enabled = config.get("smooth_enabled", True)
        self.buffers = []

    def configure(self, config):
        """参数变化时调用；窗口帧数或方式改变会清空缓冲"""
        new_window = max(1, config.get("smooth_window", 5))
        new_mode = config.get("smooth_mode", "median")
        new_enabled = config.get("smooth_enabled", True)
        if (new_window != self.window or new_mode != self.mode
                or new_enabled != self.enabled):
            self.window = new_window
            self.mode = new_mode
            self.enabled = new_enabled
            self.buffers = []

    def clear(self):
        self.buffers = []

    def push(self, values):
        """values: 本帧原始百分比列表，返回平滑后的列表"""
        if not self.enabled or self.window <= 1:
            return list(values)

        while len(self.buffers) < len(values):
            self.buffers.append(deque(maxlen=self.window))
        if len(self.buffers) > len(values):
            self.buffers = self.buffers[:len(values)]

        out = []
        for i, v in enumerate(values):
            self.buffers[i].append(v)
            buf = self.buffers[i]
            if self.mode == "mean":
                out.append(sum(buf) / len(buf))
            else:
                s = sorted(buf)
                n = len(s)
                if n % 2 == 1:
                    out.append(s[n // 2])
                else:
                    out.append((s[n // 2 - 1] + s[n // 2]) / 2.0)
        return out


def find_game_window():
    result = {"hwnd": None}
    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            for kw in WINDOW_KEYWORDS:
                if kw in title:
                    result["hwnd"] = hwnd
                    return False
        return True
    try:
        win32gui.EnumWindows(enum_callback, None)
    except Exception as e:
        logger.error(f"枚举窗口失败: {e}")
        return None
    return result["hwnd"]


def is_game_foreground():
    hwnd = find_game_window()
    if hwnd is None:
        return False
    try:
        foreground = win32gui.GetForegroundWindow()
        return foreground == hwnd
    except Exception as e:
        logger.error(f"检测前台窗口失败: {e}")
        return False


def is_game_available():
    return find_game_window() is not None


def get_actual_areas(config):
    from PyQt5.QtWidgets import QApplication
    screen = QApplication.primaryScreen()
    if screen is None:
        logger.error("无法获取屏幕信息")
        return None

    current_width = screen.size().width()
    current_height = screen.size().height()

    base_width = config.get("base_width", 1920)
    base_height = config.get("base_height", 1080)

    scale_x = current_width / base_width
    scale_y = current_height / base_height

    actual_areas = []
    try:
        for area in config["areas"]:
            actual_areas.append({
                "left": int(area["left"] * scale_x),
                "top": int(area["top"] * scale_y),
                "width": max(1, int(area["width"] * scale_x)),
                "height": max(3, int(area["height"] * scale_y))
            })
    except Exception as e:
        logger.error(f"换算坐标失败: {e}")
        return None

    return actual_areas


def _max_consecutive(arr):
    """统计数组中最长连续 True 的长度"""
    max_count = 0
    count = 0
    for v in arr:
        if v:
            count += 1
            if count > max_count:
                max_count = count
        else:
            count = 0
    return max_count


def check_single_ui(area):
    """检测单个角色区域是否有 UI（白条 + 血条）"""
    try:
        left = area["left"]
        top = area["top"]
        width = area["width"]

        combined = {
            "left": left,
            "top": max(0, top - 2),
            "width": width,
            "height": 16
        }

        with mss.mss() as sct:
            img = np.array(sct.grab(combined))
            white_row = img[3, :, :3]
            blood_row = img[11, :, :3]

            b1 = white_row[:, 0].astype(int)
            g1 = white_row[:, 1].astype(int)
            r1 = white_row[:, 2].astype(int)

            b2 = blood_row[:, 0].astype(int)
            g2 = blood_row[:, 1].astype(int)
            r2 = blood_row[:, 2].astype(int)

            is_white = (r1 > 150) & (g1 > 150) & (b1 > 150)
            white_ratio = _max_consecutive(is_white) / len(is_white)

            is_blood = ((b2 > 150) & ((b2 - r2) > 60)) | ((r2 > 150) & ((r2 - g2) > 40))
            blood_ratio = _max_consecutive(is_blood) / len(is_blood)

            if white_ratio > 0.5 and blood_ratio > 0.5:
                return True
    except:
        pass
    return False


def check_ui_available(config):
    """检测所有角色是否有 UI，返回 [bool, bool, bool, bool]"""
    try:
        areas = get_actual_areas(config)
        if not areas:
            return [False] * config.get("character_count", 4)

        result = []
        count = config.get("character_count", 4)
        for i in range(count):
            if i < len(areas):
                result.append(check_single_ui(areas[i]))
            else:
                result.append(False)
        return result
    except:
        return [False] * config.get("character_count", 4)


def capture_percentage(area):
    try:
        with mss.mss() as sct:
            img = np.array(sct.grab(area))
            if img is None or img.size == 0:
                return 0.0
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            middle_row = img_bgr.shape[0] // 2
            cropped_img = img_bgr[middle_row:middle_row+1, :]
            gray_cropped = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
            _, threshold_img = cv2.threshold(gray_cropped, 120, 255, cv2.THRESH_BINARY)
            valid_pixels = np.count_nonzero(threshold_img)
            total_pixels = threshold_img.size
            if total_pixels == 0:
                return 0.0
            return (valid_pixels / total_pixels) * 100
    except mss.exception.ScreenShotError as e:
        logger.error(f"截图失败（游戏窗口可能被最小化）: {e}")
        return 0.0
    except Exception as e:
        logger.error(f"识别异常: {e}")
        return 0.0


def capture_all(config):
    """原始采样，不做平滑"""
    count = config.get("character_count", 4)

    if not is_game_available():
        return [0.0] * count

    areas = get_actual_areas(config)
    if areas is None:
        return [0.0] * count

    results = []
    for i in range(count):
        if i < len(areas):
            results.append(capture_percentage(areas[i]))
        else:
            results.append(0.0)

    return results


def capture_all_smoothed(config, sampler):
    """采样 + 平滑。sampler 为 None 时退化为原始采样"""
    raw = capture_all(config)
    if sampler is None:
        return raw
    sampler.configure(config)
    return sampler.push(raw)