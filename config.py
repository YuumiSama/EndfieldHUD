import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    # ===== 坐标 =====
    "base_width": 1920,
    "base_height": 1080,
    "areas": [
        {"left": 42,  "top": 987, "width": 83, "height": 3},
        {"left": 159, "top": 987, "width": 83, "height": 3},
        {"left": 276, "top": 987, "width": 83, "height": 3},
        {"left": 393, "top": 987, "width": 83, "height": 3},
    ],
    
    # ===== 主界面 =====
    "close_to_tray": True,
    "close_choice_made": False,
    "theme": "dark",
    "character_count": 4,
    "auto_hide_when_no_game": False,
    "auto_hide_no_bar": False,
    "hide_animation": "fade",
    "fade_duration": 300,
    
    # ===== 预设相关 =====
    "apply_preset_pos": False,      # 切换预设时应用坐标
    "preview_enabled": True,        # 启用预览
    
    # ===== 悬浮窗样式 =====
    "overlay_style": "bar",
    "overlay_direction": "vertical",
    "bar_orientation": "horizontal",
    "fill_direction": "from-left",
    
    # ===== 悬浮窗外观 =====
    "overlay_opacity": 80,
    "bg_opacity": 0,
    "bg_corner_radius": 0,
    "bar_corner_radius": 0,
    "border_enabled": False,
    "border_color": "#00C8FF",
    "border_width": 2,
    
    # ===== 角色独立颜色 =====
    "role_color_enabled": False,
    "role_color_1": "#FF6B6B",
    "role_color_2": "#4ECDC4",
    "role_color_3": "#FFD93D",
    "role_color_4": "#A29BFE",
    
    # ===== 高亮 =====
    "highlight_enabled": True,
    "highlight_threshold": 50,
    "highlight_color": "#00FFFF",
    "highlight_width": 2,
    "highlight_layers": 2,
    
    # ===== 不可用透明度 =====
    "unavailable_opacity": 30,
    
    # ===== 内容尺寸 =====
    "size_h_bar_length": 200,
    "size_h_bar_thickness": 10,
    "size_h_bar_gap": 8,
    "size_v_bar_length": 200,
    "size_v_bar_thickness": 10,
    "size_v_bar_gap": 8,
    "size_h_circle_diameter": 60,
    "size_h_circle_thickness": 6,
    "size_h_circle_gap": 8,
    "size_v_circle_diameter": 60,
    "size_v_circle_thickness": 6,
    "size_v_circle_gap": 8,
    
    # ===== 窗口边距 =====
    "window_margin": 35,
    
    # ===== 序号样式 =====
    "number_visible": True,
    "number_position": "left",
    "number_font_size": 9,
    "number_font_weight": 700,
    "number_color": "#FFFFFF",
    "number_offset": 5,
    
    # ===== 百分比样式 =====
    "percentage_visible": True,
    "percentage_position": "right",
    "percentage_font_size": 8,
    "percentage_font_weight": 400,
    "percentage_color": "#E6E6EB",
    "percentage_offset": 5,
    
    # ===== 位置 =====
    "horizontal_pos": {"x": None, "y": None},
    "vertical_pos": {"x": None, "y": None},
    
    # ===== 日志 =====
    "log_enabled": False,
    "log_to_file": False,
    "log_max_lines": 500,
    "log_file_max_lines": 1000,
    
    # ===== 调试 =====
    "debug_mode": False,
}


STYLE_KEYS = [
    "overlay_style", "overlay_direction", "bar_orientation", "fill_direction",
    "overlay_opacity", "bg_opacity", "bg_corner_radius", "bar_corner_radius",
    "border_enabled", "border_color", "border_width",
    "role_color_enabled", "role_color_1", "role_color_2", "role_color_3", "role_color_4",
    "highlight_enabled", "highlight_threshold", "highlight_color",
    "highlight_width", "highlight_layers",
    "unavailable_opacity",
    "size_h_bar_length", "size_h_bar_thickness", "size_h_bar_gap",
    "size_v_bar_length", "size_v_bar_thickness", "size_v_bar_gap",
    "size_h_circle_diameter", "size_h_circle_thickness", "size_h_circle_gap",
    "size_v_circle_diameter", "size_v_circle_thickness", "size_v_circle_gap",
    "window_margin",
    "number_visible", "number_position", "number_font_size",
    "number_font_weight", "number_color", "number_offset",
    "percentage_visible", "percentage_position", "percentage_font_size",
    "percentage_font_weight", "percentage_color", "percentage_offset",
    "base_width", "base_height",
    "areas",
    "horizontal_pos", "vertical_pos",
]


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                merged = DEFAULT_CONFIG.copy()
                merged.update(config)
                if "areas" in config and len(config["areas"]) == 4:
                    merged["areas"] = config["areas"]
                return merged
        except Exception as e:
            print(f"配置文件损坏，已重置：{e}")
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    else:
        # 首次启动：用内置预设的样式初始化
        config = DEFAULT_CONFIG.copy()
        try:
            from presets import BUILTIN_PRESETS
            default_style = BUILTIN_PRESETS["presets"]["默认"]
            config.update(default_style)
        except Exception as e:
            print(f"加载内置预设失败：{e}")
        save_config(config)
        return config


def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存配置失败：{e}")