import json
import os
import copy
from config import STYLE_KEYS

PRESETS_FILE = "presets.json"


# 内置默认预设（用户第一次启动时使用）
BUILTIN_PRESETS = {
    "current": "默认",
    "presets": {
        "默认": {
            "overlay_style": "bar",
            "overlay_direction": "horizontal",
            "bar_orientation": "horizontal",
            "fill_direction": "from-left",
            "overlay_opacity": 100,
            "bg_opacity": 0,
            "bg_corner_radius": 0,
            "bar_corner_radius": 1,
            "border_enabled": False,
            "border_color": "#00C8FF",
            "border_width": 2,
            "role_color_enabled": False,
            "role_color_1": "#FF6B6B",
            "role_color_2": "#4ECDC4",
            "role_color_3": "#FFD93D",
            "role_color_4": "#A29BFE",
            "highlight_enabled": True,
            "highlight_threshold": 100,
            "highlight_color": "#ffffff",
            "highlight_width": 1,
            "highlight_layers": 2,
            "unavailable_opacity": 30,
            "size_h_bar_length": 72,
            "size_h_bar_thickness": 6,
            "size_h_bar_gap": 10,
            "size_v_bar_length": 200,
            "size_v_bar_thickness": 10,
            "size_v_bar_gap": 8,
            "size_h_circle_diameter": 60,
            "size_h_circle_thickness": 6,
            "size_h_circle_gap": 8,
            "size_v_circle_diameter": 60,
            "size_v_circle_thickness": 6,
            "size_v_circle_gap": 8,
            "window_margin": 35,
            "number_visible": False,
            "number_position": "left",
            "number_font_size": 9,
            "number_font_weight": 700,
            "number_color": "#FFFFFF",
            "number_offset": 5,
            "percentage_visible": False,
            "percentage_position": "right",
            "percentage_font_size": 8,
            "percentage_font_weight": 400,
            "percentage_color": "#E6E6EB",
            "percentage_offset": 5,
            "base_width": 1920,
            "base_height": 1080,
            "areas": [
                {"left": 42,  "top": 987, "width": 83, "height": 3},
                {"left": 159, "top": 987, "width": 83, "height": 3},
                {"left": 276, "top": 987, "width": 83, "height": 3},
                {"left": 393, "top": 987, "width": 83, "height": 3},
            ],
            "horizontal_pos": {"x": 766, "y": 903},
            "vertical_pos": {"x": None, "y": None},
        }
    }
}


def _default_preset(config):
    return {k: config.get(k) for k in STYLE_KEYS if k in config}


def load_presets(config):
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "current" not in data:
                    data["current"] = "默认"
                if "presets" not in data:
                    data["presets"] = {}
                if not data["presets"]:
                    data["presets"]["默认"] = _default_preset(config)
                return data
        except Exception as e:
            print(f"预设文件损坏，已重置：{e}")
    
    # 首次启动：用内置预设
    data = copy.deepcopy(BUILTIN_PRESETS)
    save_presets(data)
    return data


def save_presets(data):
    try:
        with open(PRESETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存预设失败：{e}")


def extract_style(config):
    return {k: config.get(k) for k in STYLE_KEYS if k in config}


def apply_style(config, style):
    new_config = config.copy()
    for k, v in style.items():
        if k in STYLE_KEYS:
            new_config[k] = v
    return new_config


def unique_name(presets, base_name):
    if base_name not in presets:
        return base_name
    i = 2
    while f"{base_name} ({i})" in presets:
        i += 1
    return f"{base_name} ({i})"


def add_preset(data, name, config):
    actual_name = unique_name(data["presets"], name)
    data["presets"][actual_name] = extract_style(config)
    save_presets(data)
    return actual_name


def delete_preset(data, name):
    if name in data["presets"] and len(data["presets"]) > 1:
        del data["presets"][name]
        if data["current"] == name:
            data["current"] = list(data["presets"].keys())[0]
        save_presets(data)
        return True
    return False


def rename_preset(data, old_name, new_name):
    if old_name not in data["presets"]:
        return False
    if new_name == old_name:
        return True
    actual_name = unique_name(data["presets"], new_name)
    new_presets = {}
    for k, v in data["presets"].items():
        if k == old_name:
            new_presets[actual_name] = v
        else:
            new_presets[k] = v
    data["presets"] = new_presets
    if data["current"] == old_name:
        data["current"] = actual_name
    save_presets(data)
    return True


def update_current(data, config):
    current = data.get("current", "默认")
    data["presets"][current] = extract_style(config)
    save_presets(data)


def get_current_style(data):
    current = data.get("current", "默认")
    return data["presets"].get(current, {})


def export_presets(data, path):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"导出失败：{e}")
        return False


def import_presets(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if "presets" not in data:
            return None
        if "current" not in data:
            data["current"] = list(data["presets"].keys())[0] if data["presets"] else "默认"
        return data
    except Exception as e:
        print(f"导入失败：{e}")
        return None