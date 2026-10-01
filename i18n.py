# -*- coding: utf-8 -*-
"""多语言翻译文件"""

TRANSLATIONS = {
    "zh_CN": {
        # ===== 应用信息 =====
        "app_title": "终末地连携监测",
        "app_title_bar": "终末地连携监测 v{version}",
        "app_tray_tooltip": "终末地连携监测 v{version}",

        # ===== 导航栏 =====
        "nav_home": "主页",
        "nav_settings": "设置",
        "nav_log": "日志",
        "nav_about": "关于",

        # ===== 主页 =====
        "home_title": "终末地连携监测",
        "home_desc": "实时监测角色的连携状态，悬浮窗显示在游戏上方。",
        "home_start": "启动悬浮窗",
        "home_pause": "暂停",
        "home_resume": "继续",
        "home_stop": "停止悬浮窗",
        "home_preset": "当前预设：",
        "home_apply_pos": "应用坐标",
        "home_preview": "启用预览",
        "home_role": "角色 {n}",

        # ===== 预设菜单 =====
        "preset_save": "保存当前为预设",
        "preset_new": "新建预设...",
        "preset_rename": "重命名当前预设...",
        "preset_delete": "删除当前预设",
        "preset_import": "导入预设...",
        "preset_export": "导出预设...",
        "preset_saved": "当前设置已保存到预设",
        "preset_created": "预设「{name}」已创建",
        "preset_renamed": "预设已重命名为「{name}」",
        "preset_delete_confirm": "确定删除预设「{name}」吗？",
        "preset_delete_title": "删除预设",
        "preset_cant_delete": "至少保留一个预设",
        "preset_cant_delete_title": "无法删除",
        "preset_import_success": "预设已导入",
        "preset_import_fail": "文件格式错误",
        "preset_export_success": "导出成功",
        "preset_export_fail": "写入文件失败",
        "preset_new_title": "新建预设",
        "preset_new_prompt": "预设名称：",
        "preset_rename_title": "重命名预设",
        "preset_rename_prompt": "新名称：",
        "preset_no_preview": "无预览",

        # ===== 设置页 - 分组标题 =====
        "settings_title": "设置",
        "settings_basic": "基础设置",
        "settings_appearance": "悬浮窗外观",
        "settings_role_color": "角色颜色",
        "settings_highlight": "高亮（光晕）",
        "settings_size": "尺寸",
        "settings_number": "序号样式",
        "settings_percentage": "百分比样式",
        "settings_other": "其他",

        # ===== 设置页 - 基础 =====
        "settings_role_count": "角色数量",
        "settings_close_tray": "关闭窗口时最小化到托盘",
        "settings_theme": "深色主题",
        "settings_language": "语言",
        "settings_hide_no_game": "游戏不在前台时隐藏",
        "settings_hide_no_bar": "无能量条时自动隐藏",
        "settings_hide_anim": "隐藏动画",
        "settings_hide_anim_fade": "淡入淡出",
        "settings_hide_anim_instant": "即时",
        "settings_fade_duration": "动画时长(ms)",
        "settings_style": "悬浮窗样式",
        "settings_style_bar": "长条",
        "settings_style_ring": "圆环",
        "settings_style_pie": "饼图",
        "settings_style_solid": "实心圆",
        "settings_direction": "排列方向",
        "settings_dir_horizontal": "横排",
        "settings_dir_vertical": "竖排",
        "settings_bar_orient": "条方向",
        "settings_bar_orient_h": "横条",
        "settings_bar_orient_v": "竖条",
        "settings_fill_dir": "填充方向",
        "settings_fill_left_right": "从左到右",
        "settings_fill_right_left": "从右到左",
        "settings_fill_bottom_top": "从下到上",
        "settings_fill_top_bottom": "从上到下",
        "settings_fill_clockwise": "顺时针",
        "settings_fill_counterclockwise": "逆时针",

        # ===== 设置页 - 外观 =====
        "settings_opacity": "整体透明度",
        "settings_bg_opacity": "背景透明度",
        "settings_bg_corner": "背景圆角",
        "settings_bar_corner": "进度条圆角",
        "settings_margin": "窗口边距",
        "settings_unavail_opacity": "角色不可用透明度",
        "settings_border": "启用边框",
        "settings_border_color": "边框颜色",
        "settings_border_width": "粗细",

        # ===== 设置页 - 角色颜色 =====
        "settings_role_color_enabled": "启用角色独立颜色",
        "settings_role_color_n": "角色 {n} 颜色",

        # ===== 设置页 - 高亮 =====
        "settings_hl_enabled": "启用高亮",
        "settings_hl_threshold": "高亮阈值",
        "settings_hl_color": "高亮颜色",
        "settings_hl_width": "高亮粗细",
        "settings_hl_layers": "高亮层数",

        # ===== 设置页 - 尺寸 =====
        "settings_bar_length": "条长度",
        "settings_bar_thickness": "条粗细",
        "settings_bar_gap": "条间距",
        "settings_circle_diameter": "圆环直径",
        "settings_circle_thickness": "圆环粗细",
        "settings_circle_gap": "圆间距",

        # ===== 设置页 - 序号 =====
        "settings_num_visible": "显示序号",
        "settings_num_position": "序号位置",
        "settings_num_offset": "序号距离",
        "settings_num_font_size": "序号字体大小",
        "settings_num_font_weight": "序号字体粗细",
        "settings_num_color": "序号字体颜色",
        "settings_position_center": "中心",
        "settings_position_top": "上方",
        "settings_position_bottom": "下方",
        "settings_position_left": "左侧",
        "settings_position_right": "右侧",
        "settings_position_none": "不显示",
        "settings_weight_normal": "默认",
        "settings_weight_bold": "加粗",

        # ===== 设置页 - 百分比 =====
        "settings_pct_visible": "显示百分比",
        "settings_pct_position": "百分比位置",
        "settings_pct_offset": "百分比距离",
        "settings_pct_font_size": "百分比字体大小",
        "settings_pct_font_weight": "百分比字体粗细",
        "settings_pct_color": "百分比字体颜色",

        # ===== 设置页 - 其他 =====
        "settings_tip_drag": "按住 Ctrl 键，用鼠标拖动悬浮窗调整位置。位置会自动保存。",
        "settings_reset_pos": "恢复默认位置",
        "settings_debug": "调试模式（每5秒记录识别数据）",
        "settings_log_enabled": "启用日志记录",
        "settings_log_file": "保存日志到文件",
        "settings_reset": "恢复默认设置",
        "settings_export": "导出配置",
        "settings_import": "导入配置",
        "settings_reset_pos_done": "下次启动悬浮窗将使用默认位置",
        "settings_reset_done": "请重启软件以应用所有设置",
        "settings_reset_confirm": "确定要恢复所有设置为默认值吗？",
        "settings_reset_title": "恢复默认设置",
        "settings_export_success": "导出成功",
        "settings_export_fail": "导出失败",
        "settings_import_success": "导入成功",
        "settings_import_fail": "导入失败",
        "settings_lang_changed": "请重启软件以应用语言更改",
        "settings_lang_title": "需要重启",
        "settings_lang_restart": "语言已切换，程序即将自动重启……",

        # ===== 颜色选择 =====
        "color_pick_title": "选择颜色",

        # ===== 日志页 =====
        "log_title": "日志",
        "log_enabled": "启用日志记录",
        "log_clear": "清空日志",

        # ===== 关于页 =====
        "about_title": "关于",
        "about_version": "终末地连携监测 v{version}",
        "about_desc": "一个基于屏幕识别的连携监测工具。\n不修改游戏文件、不读取游戏内存。\n仅供个人学习使用。",
        "about_repo": "GitHub 仓库",
        "about_update": "更新页面",
        "about_bilibili": "哔哩哔哩",
        "about_open": "打开",

        # ===== 关闭对话框 =====
        "close_title": "关闭窗口",
        "close_prompt": "关闭窗口时，你希望：",
        "close_tray_option": "最小化到托盘",
        "close_exit_option": "直接退出",
        "close_remember": "记住我的选择（下次不再提示）",
        "close_ok": "确定",
        "close_cancel": "取消",
        "close_tray_msg": "软件已最小化到托盘，双击托盘图标可重新打开。",

        # ===== 托盘菜单 =====
        "tray_show": "显示主界面",
        "tray_start": "启动悬浮窗",
        "tray_stop": "停止悬浮窗",
        "tray_quit": "退出",

        # ===== 通用 =====
        "yes": "是",
        "no": "否",

        # ===== 采样 / 平滑 =====
        "settings_sample_group": "识别性能",
        "settings_sample_preset": "采样档位",
        "settings_sample_saver": "省电",
        "settings_sample_normal": "默认",
        "settings_sample_performance": "性能",
        "settings_sample_precision": "高精度",
        "settings_sample_custom": "自定义",
        "settings_sample_interval": "采样间隔(ms)",
        "settings_sample_interval_hidden": "隐藏时采样间隔(ms)",
        "settings_sample_when_off": "悬浮窗未启动时仍采样",
        "settings_smooth_enabled": "启用平滑",
        "settings_smooth_window": "平滑窗口(帧)",
        "settings_smooth_mode": "平滑方式",
        "settings_smooth_median": "中值",
        "settings_smooth_mean": "平均",
        "settings_sample_tip_preset": "控制识别频率。档位越高越跟手，但占用更多 CPU。",
        "settings_sample_tip_interval": "可见时每隔多少毫秒识别一次。数值越小越灵敏，但更吃性能。",
        "settings_sample_tip_hidden": "悬浮窗自动隐藏时的识别间隔。可以设大一些省性能。",
        "settings_sample_tip_off": "开启后，即使没启动悬浮窗，主界面也会持续显示百分比。关闭可省性能。",
        "settings_smooth_tip_enabled": "对最近几帧结果做平滑，能抑制偶发的识别跳变。",
        "settings_smooth_tip_window": "参与平滑的帧数。越大越稳，但响应越慢。1 表示不平滑。",
        "settings_smooth_tip_mode": "中值：抗单帧误判最强；平均：更平滑，但一帧异常会拉偏结果。",
        "settings_sample_changed": "采样设置已更新",
    },

    "en_US": {
        # ===== App Info =====
        "app_title": "Endfield Link Monitor",
        "app_title_bar": "Endfield Link Monitor v{version}",
        "app_tray_tooltip": "Endfield Link Monitor v{version}",

        # ===== Navigation =====
        "nav_home": "Home",
        "nav_settings": "Settings",
        "nav_log": "Log",
        "nav_about": "About",

        # ===== Home =====
        "home_title": "Endfield Link Monitor",
        "home_desc": "Real-time monitoring of character link status, overlay shown on top of the game.",
        "home_start": "Start Overlay",
        "home_pause": "Pause",
        "home_resume": "Resume",
        "home_stop": "Stop Overlay",
        "home_preset": "Current Preset: ",
        "home_apply_pos": "Apply Position",
        "home_preview": "Enable Preview",
        "home_role": "Character {n}",

        # ===== Preset Menu =====
        "preset_save": "Save Current as Preset",
        "preset_new": "New Preset...",
        "preset_rename": "Rename Current Preset...",
        "preset_delete": "Delete Current Preset",
        "preset_import": "Import Preset...",
        "preset_export": "Export Preset...",
        "preset_saved": "Current settings saved to preset",
        "preset_created": "Preset \"{name}\" created",
        "preset_renamed": "Preset renamed to \"{name}\"",
        "preset_delete_confirm": "Delete preset \"{name}\"?",
        "preset_delete_title": "Delete Preset",
        "preset_cant_delete": "At least one preset must be kept",
        "preset_cant_delete_title": "Cannot Delete",
        "preset_import_success": "Preset imported",
        "preset_import_fail": "Invalid file format",
        "preset_export_success": "Export successful",
        "preset_export_fail": "Failed to write file",
        "preset_new_title": "New Preset",
        "preset_new_prompt": "Preset name:",
        "preset_rename_title": "Rename Preset",
        "preset_rename_prompt": "New name:",
        "preset_no_preview": "No Preview",

        # ===== Settings - Group Titles =====
        "settings_title": "Settings",
        "settings_basic": "Basic",
        "settings_appearance": "Appearance",
        "settings_role_color": "Character Colors",
        "settings_highlight": "Highlight (Glow)",
        "settings_size": "Size",
        "settings_number": "Number Style",
        "settings_percentage": "Percentage Style",
        "settings_other": "Other",

        # ===== Settings - Basic =====
        "settings_role_count": "Character Count",
        "settings_close_tray": "Minimize to tray on close",
        "settings_theme": "Dark Theme",
        "settings_language": "Language",
        "settings_hide_no_game": "Hide when game not in foreground",
        "settings_hide_no_bar": "Auto-hide when no energy bar",
        "settings_hide_anim": "Hide Animation",
        "settings_hide_anim_fade": "Fade",
        "settings_hide_anim_instant": "Instant",
        "settings_fade_duration": "Animation Duration (ms)",
        "settings_style": "Overlay Style",
        "settings_style_bar": "Bar",
        "settings_style_ring": "Ring",
        "settings_style_pie": "Pie",
        "settings_style_solid": "Solid Circle",
        "settings_direction": "Arrangement",
        "settings_dir_horizontal": "Horizontal",
        "settings_dir_vertical": "Vertical",
        "settings_bar_orient": "Bar Orientation",
        "settings_bar_orient_h": "Horizontal",
        "settings_bar_orient_v": "Vertical",
        "settings_fill_dir": "Fill Direction",
        "settings_fill_left_right": "Left to Right",
        "settings_fill_right_left": "Right to Left",
        "settings_fill_bottom_top": "Bottom to Top",
        "settings_fill_top_bottom": "Top to Bottom",
        "settings_fill_clockwise": "Clockwise",
        "settings_fill_counterclockwise": "Counterclockwise",

        # ===== Settings - Appearance =====
        "settings_opacity": "Overall Opacity",
        "settings_bg_opacity": "Background Opacity",
        "settings_bg_corner": "Background Corner Radius",
        "settings_bar_corner": "Bar Corner Radius",
        "settings_margin": "Window Margin",
        "settings_unavail_opacity": "Unavailable Character Opacity",
        "settings_border": "Enable Border",
        "settings_border_color": "Border Color",
        "settings_border_width": "Width",

        # ===== Settings - Role Color =====
        "settings_role_color_enabled": "Enable Per-character Colors",
        "settings_role_color_n": "Character {n} Color",

        # ===== Settings - Highlight =====
        "settings_hl_enabled": "Enable Highlight",
        "settings_hl_threshold": "Highlight Threshold",
        "settings_hl_color": "Highlight Color",
        "settings_hl_width": "Highlight Width",
        "settings_hl_layers": "Highlight Layers",

        # ===== Settings - Size =====
        "settings_bar_length": "Bar Length",
        "settings_bar_thickness": "Bar Thickness",
        "settings_bar_gap": "Bar Gap",
        "settings_circle_diameter": "Circle Diameter",
        "settings_circle_thickness": "Circle Thickness",
        "settings_circle_gap": "Circle Gap",

        # ===== Settings - Number =====
        "settings_num_visible": "Show Number",
        "settings_num_position": "Number Position",
        "settings_num_offset": "Number Offset",
        "settings_num_font_size": "Number Font Size",
        "settings_num_font_weight": "Number Font Weight",
        "settings_num_color": "Number Font Color",
        "settings_position_center": "Center",
        "settings_position_top": "Top",
        "settings_position_bottom": "Bottom",
        "settings_position_left": "Left",
        "settings_position_right": "Right",
        "settings_position_none": "None",
        "settings_weight_normal": "Normal",
        "settings_weight_bold": "Bold",

        # ===== Settings - Percentage =====
        "settings_pct_visible": "Show Percentage",
        "settings_pct_position": "Percentage Position",
        "settings_pct_offset": "Percentage Offset",
        "settings_pct_font_size": "Percentage Font Size",
        "settings_pct_font_weight": "Percentage Font Weight",
        "settings_pct_color": "Percentage Font Color",

        # ===== Settings - Other =====
        "settings_tip_drag": "Hold Ctrl and drag the overlay to adjust position. Position is auto-saved.",
        "settings_reset_pos": "Reset Position",
        "settings_debug": "Debug Mode (log every 5s)",
        "settings_log_enabled": "Enable Logging",
        "settings_log_file": "Save Log to File",
        "settings_reset": "Reset Settings",
        "settings_export": "Export Config",
        "settings_import": "Import Config",
        "settings_reset_pos_done": "Default position will be used next time",
        "settings_reset_done": "Please restart the app to apply settings",
        "settings_reset_confirm": "Reset all settings to default?",
        "settings_reset_title": "Reset Settings",
        "settings_export_success": "Export successful",
        "settings_export_fail": "Export failed",
        "settings_import_success": "Import successful",
        "settings_import_fail": "Import failed",
        "settings_lang_changed": "Please restart the app to apply language change",
        "settings_lang_title": "Restart Required",
        "settings_lang_restart": "Language changed. Restarting the app...",

        # ===== Color Pick =====
        "color_pick_title": "Select Color",

        # ===== Log Page =====
        "log_title": "Log",
        "log_enabled": "Enable Logging",
        "log_clear": "Clear Log",

        # ===== About Page =====
        "about_title": "About",
        "about_version": "Endfield Link Monitor v{version}",
        "about_desc": "A screen-recognition based link monitoring tool.\nDoes not modify game files or read game memory.\nFor personal learning use only.",
        "about_repo": "GitHub Repository",
        "about_update": "Update Page",
        "about_bilibili": "Bilibili",
        "about_open": "Open",

        # ===== Close Dialog =====
        "close_title": "Close Window",
        "close_prompt": "When closing the window, you want to:",
        "close_tray_option": "Minimize to tray",
        "close_exit_option": "Exit directly",
        "close_remember": "Remember my choice (don't ask again)",
        "close_ok": "OK",
        "close_cancel": "Cancel",
        "close_tray_msg": "App minimized to tray. Double-click tray icon to reopen.",

        # ===== Tray Menu =====
        "tray_show": "Show Main Window",
        "tray_start": "Start Overlay",
        "tray_stop": "Stop Overlay",
        "tray_quit": "Quit",

        # ===== Common =====
        "yes": "Yes",
        "no": "No",

        # ===== Sampling / Smoothing =====
        "settings_sample_group": "Performance",
        "settings_sample_preset": "Sampling Preset",
        "settings_sample_saver": "Saver",
        "settings_sample_normal": "Normal",
        "settings_sample_performance": "Performance",
        "settings_sample_precision": "Precision",
        "settings_sample_custom": "Custom",
        "settings_sample_interval": "Interval (ms)",
        "settings_sample_interval_hidden": "Hidden Interval (ms)",
        "settings_sample_when_off": "Sample when overlay is off",
        "settings_smooth_enabled": "Enable Smoothing",
        "settings_smooth_window": "Smoothing Window (frames)",
        "settings_smooth_mode": "Smoothing Mode",
        "settings_smooth_median": "Median",
        "settings_smooth_mean": "Mean",
        "settings_sample_tip_preset": "Controls sampling frequency. Higher presets are more responsive but use more CPU.",
        "settings_sample_tip_interval": "How often to sample when visible. Smaller is more responsive but heavier.",
        "settings_sample_tip_hidden": "Sampling interval when the overlay is auto-hidden. Increase to save CPU.",
        "settings_sample_tip_off": "When on, the main window keeps updating even if the overlay is off. Turn off to save CPU.",
        "settings_smooth_tip_enabled": "Smooth recent frames to suppress occasional detection jumps.",
        "settings_smooth_tip_window": "Number of frames used for smoothing. Larger is steadier but slower. 1 disables smoothing.",
        "settings_smooth_tip_mode": "Median: best against single-frame errors; Mean: smoother but an outlier can skew it.",
        "settings_sample_changed": "Sampling settings updated",
    },

    "zh_TW": {
        # ===== 應用資訊 =====
        "app_title": "終末地連攜監測",
        "app_title_bar": "終末地連攜監測 v{version}",
        "app_tray_tooltip": "終末地連攜監測 v{version}",

        # ===== 導航欄 =====
        "nav_home": "主頁",
        "nav_settings": "設定",
        "nav_log": "日誌",
        "nav_about": "關於",

        # ===== 主頁 =====
        "home_title": "終末地連攜監測",
        "home_desc": "即時監測角色的連攜狀態，懸浮窗顯示在遊戲上方。",
        "home_start": "啟動懸浮窗",
        "home_pause": "暫停",
        "home_resume": "繼續",
        "home_stop": "停止懸浮窗",
        "home_preset": "當前預設：",
        "home_apply_pos": "應用座標",
        "home_preview": "啟用預覽",
        "home_role": "角色 {n}",

        # ===== 預設選單 =====
        "preset_save": "儲存當前為預設",
        "preset_new": "新建預設...",
        "preset_rename": "重新命名當前預設...",
        "preset_delete": "刪除當前預設",
        "preset_import": "匯入預設...",
        "preset_export": "匯出預設...",
        "preset_saved": "當前設定已儲存到預設",
        "preset_created": "預設「{name}」已建立",
        "preset_renamed": "預設已重新命名為「{name}」",
        "preset_delete_confirm": "確定刪除預設「{name}」嗎？",
        "preset_delete_title": "刪除預設",
        "preset_cant_delete": "至少保留一個預設",
        "preset_cant_delete_title": "無法刪除",
        "preset_import_success": "預設已匯入",
        "preset_import_fail": "檔案格式錯誤",
        "preset_export_success": "匯出成功",
        "preset_export_fail": "寫入檔案失敗",
        "preset_new_title": "新建預設",
        "preset_new_prompt": "預設名稱：",
        "preset_rename_title": "重新命名預設",
        "preset_rename_prompt": "新名稱：",
        "preset_no_preview": "無預覽",

        # ===== 設定頁 - 群組標題 =====
        "settings_title": "設定",
        "settings_basic": "基礎設定",
        "settings_appearance": "懸浮窗外觀",
        "settings_role_color": "角色顏色",
        "settings_highlight": "高亮（光暈）",
        "settings_size": "尺寸",
        "settings_number": "序號樣式",
        "settings_percentage": "百分比樣式",
        "settings_other": "其他",

        # ===== 設定頁 - 基礎 =====
        "settings_role_count": "角色數量",
        "settings_close_tray": "關閉視窗時最小化到托盤",
        "settings_theme": "深色主題",
        "settings_language": "語言",
        "settings_hide_no_game": "遊戲不在前台時隱藏",
        "settings_hide_no_bar": "無能量條時自動隱藏",
        "settings_hide_anim": "隱藏動畫",
        "settings_hide_anim_fade": "淡入淡出",
        "settings_hide_anim_instant": "即時",
        "settings_fade_duration": "動畫時長(ms)",
        "settings_style": "懸浮窗樣式",
        "settings_style_bar": "長條",
        "settings_style_ring": "圓環",
        "settings_style_pie": "餅圖",
        "settings_style_solid": "實心圓",
        "settings_direction": "排列方向",
        "settings_dir_horizontal": "橫排",
        "settings_dir_vertical": "豎排",
        "settings_bar_orient": "條方向",
        "settings_bar_orient_h": "橫條",
        "settings_bar_orient_v": "豎條",
        "settings_fill_dir": "填充方向",
        "settings_fill_left_right": "從左到右",
        "settings_fill_right_left": "從右到左",
        "settings_fill_bottom_top": "從下到上",
        "settings_fill_top_bottom": "從上到下",
        "settings_fill_clockwise": "順時針",
        "settings_fill_counterclockwise": "逆時針",

        # ===== 設定頁 - 外觀 =====
        "settings_opacity": "整體透明度",
        "settings_bg_opacity": "背景透明度",
        "settings_bg_corner": "背景圓角",
        "settings_bar_corner": "進度條圓角",
        "settings_margin": "視窗邊距",
        "settings_unavail_opacity": "角色不可用透明度",
        "settings_border": "啟用邊框",
        "settings_border_color": "邊框顏色",
        "settings_border_width": "粗細",

        # ===== 設定頁 - 角色顏色 =====
        "settings_role_color_enabled": "啟用角色獨立顏色",
        "settings_role_color_n": "角色 {n} 顏色",

        # ===== 設定頁 - 高亮 =====
        "settings_hl_enabled": "啟用高亮",
        "settings_hl_threshold": "高亮閾值",
        "settings_hl_color": "高亮顏色",
        "settings_hl_width": "高亮粗細",
        "settings_hl_layers": "高亮層數",

        # ===== 設定頁 - 尺寸 =====
        "settings_bar_length": "條長度",
        "settings_bar_thickness": "條粗細",
        "settings_bar_gap": "條間距",
        "settings_circle_diameter": "圓環直徑",
        "settings_circle_thickness": "圓環粗細",
        "settings_circle_gap": "圓間距",

        # ===== 設定頁 - 序號 =====
        "settings_num_visible": "顯示序號",
        "settings_num_position": "序號位置",
        "settings_num_offset": "序號距離",
        "settings_num_font_size": "序號字體大小",
        "settings_num_font_weight": "序號字體粗細",
        "settings_num_color": "序號字體顏色",
        "settings_position_center": "中心",
        "settings_position_top": "上方",
        "settings_position_bottom": "下方",
        "settings_position_left": "左側",
        "settings_position_right": "右側",
        "settings_position_none": "不顯示",
        "settings_weight_normal": "預設",
        "settings_weight_bold": "加粗",

        # ===== 設定頁 - 百分比 =====
        "settings_pct_visible": "顯示百分比",
        "settings_pct_position": "百分比位置",
        "settings_pct_offset": "百分比距離",
        "settings_pct_font_size": "百分比字體大小",
        "settings_pct_font_weight": "百分比字體粗細",
        "settings_pct_color": "百分比字體顏色",

        # ===== 設定頁 - 其他 =====
        "settings_tip_drag": "按住 Ctrl 鍵，用滑鼠拖動懸浮窗調整位置。位置會自動儲存。",
        "settings_reset_pos": "恢復預設位置",
        "settings_debug": "除錯模式（每5秒記錄識別資料）",
        "settings_log_enabled": "啟用日誌記錄",
        "settings_log_file": "儲存日誌到檔案",
        "settings_reset": "恢復預設設定",
        "settings_export": "匯出設定",
        "settings_import": "匯入設定",
        "settings_reset_pos_done": "下次啟動懸浮窗將使用預設位置",
        "settings_reset_done": "請重啟軟體以套用所有設定",
        "settings_reset_confirm": "確定要恢復所有設定為預設值嗎？",
        "settings_reset_title": "恢復預設設定",
        "settings_export_success": "匯出成功",
        "settings_export_fail": "匯出失敗",
        "settings_import_success": "匯入成功",
        "settings_import_fail": "匯入失敗",
        "settings_lang_changed": "請重啟軟體以套用語言變更",
        "settings_lang_title": "需要重啟",
        "settings_lang_restart": "語言已切換，程式即將自動重啟……",

        # ===== 顏色選擇 =====
        "color_pick_title": "選擇顏色",

        # ===== 日誌頁 =====
        "log_title": "日誌",
        "log_enabled": "啟用日誌記錄",
        "log_clear": "清空日誌",

        # ===== 關於頁 =====
        "about_title": "關於",
        "about_version": "終末地連攜監測 v{version}",
        "about_desc": "一個基於螢幕辨識的連攜監測工具。\n不修改遊戲檔案、不讀取遊戲記憶體。\n僅供個人學習使用。",
        "about_repo": "GitHub 倉庫",
        "about_update": "更新頁面",
        "about_bilibili": "嗶哩嗶哩",
        "about_open": "開啟",

        # ===== 關閉對話框 =====
        "close_title": "關閉視窗",
        "close_prompt": "關閉視窗時，你希望：",
        "close_tray_option": "最小化到托盤",
        "close_exit_option": "直接退出",
        "close_remember": "記住我的選擇（下次不再提示）",
        "close_ok": "確定",
        "close_cancel": "取消",
        "close_tray_msg": "軟體已最小化到托盤，雙擊托盤圖示可重新開啟。",

        # ===== 托盤選單 =====
        "tray_show": "顯示主介面",
        "tray_start": "啟動懸浮窗",
        "tray_stop": "停止懸浮窗",
        "tray_quit": "退出",

        # ===== 通用 =====
        "yes": "是",
        "no": "否",

        # ===== 取樣 / 平滑 =====
        "settings_sample_group": "辨識效能",
        "settings_sample_preset": "取樣檔位",
        "settings_sample_saver": "省電",
        "settings_sample_normal": "預設",
        "settings_sample_performance": "效能",
        "settings_sample_precision": "高精度",
        "settings_sample_custom": "自訂",
        "settings_sample_interval": "取樣間隔(ms)",
        "settings_sample_interval_hidden": "隱藏時取樣間隔(ms)",
        "settings_sample_when_off": "懸浮窗未啟動時仍取樣",
        "settings_smooth_enabled": "啟用平滑",
        "settings_smooth_window": "平滑視窗(幀)",
        "settings_smooth_mode": "平滑方式",
        "settings_smooth_median": "中值",
        "settings_smooth_mean": "平均",
        "settings_sample_tip_preset": "控制辨識頻率。檔位越高越跟手，但佔用更多 CPU。",
        "settings_sample_tip_interval": "可見時每隔多少毫秒辨識一次。數值越小越靈敏，但更吃效能。",
        "settings_sample_tip_hidden": "懸浮窗自動隱藏時的辨識間隔。可以設大一些省效能。",
        "settings_sample_tip_off": "開啟後，即使沒啟動懸浮窗，主介面也會持續顯示百分比。關閉可省效能。",
        "settings_smooth_tip_enabled": "對最近幾幀結果做平滑，能抑制偶發的辨識跳變。",
        "settings_smooth_tip_window": "參與平滑的幀數。越大越穩，但回應越慢。1 表示不平滑。",
        "settings_smooth_tip_mode": "中值：抗單幀誤判最強；平均：更平滑，但一幀異常會拉偏結果。",
        "settings_sample_changed": "取樣設定已更新",
    },
}


def t(key, lang="zh_CN", **kwargs):
    """获取翻译文字
    key: 翻译键
    lang: 语言代码
    kwargs: 格式化参数（比如 name, version, n）
    """
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["zh_CN"])
    text = translations.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    return text