import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSystemTrayIcon, QMenu, QAction, QFileDialog, QColorDialog,
    QScrollArea, QPushButton, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QUrl, QRectF
from PyQt5.QtGui import QIcon, QColor, QFont, QPainter, QPen, QBrush, QDesktopServices
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, SubtitleLabel,
    PrimaryPushButton, PushButton, CardWidget, BodyLabel,
    ProgressBar, setTheme, Theme, SwitchButton, Slider,
    ComboBox, TextEdit, StrongBodyLabel, InfoBar,
    InfoBarPosition, MessageBox, LineEdit, RoundMenu, Action,
    FluentIcon
)
from config import load_config, save_config, DEFAULT_CONFIG
from capture import capture_all
from overlay import Overlay
from logger import logger
from presets import (
    load_presets, save_presets, add_preset, delete_preset,
    rename_preset, update_current, apply_style, get_current_style,
    export_presets, import_presets
)

VERSION = "0.0.1"


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def make_group_title(text, parent):
    label = SubtitleLabel(text, parent)
    label.setContentsMargins(5, 14, 0, 6)
    return label


def make_slider_row(label_text, min_val, max_val, current_val, parent, callback,
                    slider_width=120, edit_width=50):
    row = QHBoxLayout()
    label = BodyLabel(label_text, parent)
    label.setFixedWidth(110)
    row.addWidget(label)
    slider = Slider(Qt.Horizontal, parent)
    slider.setRange(min_val, max_val)
    slider.setValue(current_val)
    slider.setFixedWidth(slider_width)
    row.addWidget(slider)
    row.addStretch()
    edit = LineEdit(parent)
    edit.setFixedWidth(edit_width)
    edit.setText(str(current_val))
    row.addWidget(edit)
    def on_slider(val):
        edit.setText(str(val))
        callback(val)
    def on_edit_finish():
        try:
            val = int(edit.text())
            if val < min_val or val > max_val:
                raise ValueError
            slider.setValue(val)
            callback(val)
        except ValueError:
            edit.setText(str(slider.value()))
    slider.valueChanged.connect(on_slider)
    edit.editingFinished.connect(on_edit_finish)
    return row, slider, edit


def make_switch_row(label_text, current_val, parent, callback):
    row = QHBoxLayout()
    label = BodyLabel(label_text, parent)
    row.addWidget(label)
    row.addStretch()
    sw = SwitchButton(parent)
    sw.setOnText("是")
    sw.setOffText("否")
    sw.setChecked(current_val)
    sw.checkedChanged.connect(callback)
    row.addWidget(sw)
    return row, sw


def make_combo_row(label_text, items, current_idx, parent, callback):
    row = QHBoxLayout()
    label = BodyLabel(label_text, parent)
    row.addWidget(label)
    row.addStretch()
    combo = ComboBox(parent)
    combo.addItems(items)
    combo.setCurrentIndex(current_idx)
    combo.currentIndexChanged.connect(callback)
    row.addWidget(combo)
    return row, combo


def make_color_row(label_text, color_str, parent, callback):
    row = QHBoxLayout()
    label = BodyLabel(label_text, parent)
    row.addWidget(label)
    row.addStretch()
    btn = PushButton(color_str, parent)
    def on_click():
        color = QColorDialog.getColor(QColor(color_str), parent)
        if color.isValid():
            callback(color.name())
            btn.setText(color.name())
    btn.clicked.connect(on_click)
    row.addWidget(btn)
    return row, btn


class PresetPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.style = {}
        self.setFixedSize(160, 80)
        self.setStyleSheet("background: rgba(30, 30, 35, 100); border-radius: 8px;")
    
    def update_preview(self, style):
        self.style = style or {}
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        style = self.style
        if not style:
            painter.setPen(QPen(QColor(120, 120, 120)))
            painter.setFont(QFont("Microsoft YaHei", 9))
            painter.drawText(self.rect(), Qt.AlignCenter, "无预览")
            return
        
        overlay_style = style.get("overlay_style", "bar")
        direction = style.get("overlay_direction", "vertical")
        bar_orient = style.get("bar_orientation", "horizontal")
        overlay_opacity = style.get("overlay_opacity", 80) / 100.0
        bar_corner = style.get("bar_corner_radius", 0)
        fill_dir = style.get("fill_direction", "from-bottom")
        role_color_enabled = style.get("role_color_enabled", False)
        
        count = 4
        margin = 8
        percentages = [80, 100, 30, 65]
        
        def get_fill_color(pct, role_idx=0):
            if role_color_enabled:
                color_str = style.get(f"role_color_{role_idx + 1}", "#FFFFFF")
                return QColor(color_str)
            return QColor(230, 230, 235, 230)
        
        painter.setOpacity(overlay_opacity)
        efd = fill_dir
        
        if overlay_style == "bar":
            if direction == "horizontal" and bar_orient == "horizontal":
                bar_length = 30
                bar_thickness = 8
                gap = 4
                y = (self.height() - bar_thickness) // 2
                for i, pct in enumerate(percentages):
                    x = margin + i * (bar_length + gap)
                    if x + bar_length > self.width() - margin:
                        break
                    corner = bar_corner if bar_corner > 0 else bar_thickness // 2
                    corner = min(corner, bar_thickness // 2)
                    painter.setBrush(QBrush(QColor(30, 30, 35, 200)))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(x, y, bar_length, bar_thickness, corner, corner)
                    fill = int(bar_length * (pct / 100.0))
                    if fill > 0:
                        painter.setBrush(QBrush(get_fill_color(pct, i)))
                        if efd == "from-right":
                            painter.drawRoundedRect(x + bar_length - fill, y, fill, bar_thickness, corner, corner)
                        else:
                            painter.drawRoundedRect(x, y, fill, bar_thickness, corner, corner)
            elif direction == "vertical" and bar_orient == "horizontal":
                bar_length = 110
                bar_thickness = 8
                gap = 4
                x = (self.width() - bar_length) // 2
                for i, pct in enumerate(percentages):
                    y = margin + i * (bar_thickness + gap)
                    if y + bar_thickness > self.height() - margin:
                        break
                    corner = bar_corner if bar_corner > 0 else bar_thickness // 2
                    corner = min(corner, bar_thickness // 2)
                    painter.setBrush(QBrush(QColor(30, 30, 35, 200)))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(x, y, bar_length, bar_thickness, corner, corner)
                    fill = int(bar_length * (pct / 100.0))
                    if fill > 0:
                        painter.setBrush(QBrush(get_fill_color(pct, i)))
                        if efd == "from-right":
                            painter.drawRoundedRect(x + bar_length - fill, y, fill, bar_thickness, corner, corner)
                        else:
                            painter.drawRoundedRect(x, y, fill, bar_thickness, corner, corner)
            elif direction == "horizontal" and bar_orient == "vertical":
                bar_length = 50
                bar_thickness = 8
                gap = 6
                y = (self.height() - bar_length) // 2
                for i, pct in enumerate(percentages):
                    x = margin + i * (bar_thickness + gap)
                    if x + bar_thickness > self.width() - margin:
                        break
                    corner = bar_corner if bar_corner > 0 else bar_thickness // 2
                    corner = min(corner, bar_thickness // 2)
                    painter.setBrush(QBrush(QColor(30, 30, 35, 200)))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(x, y, bar_thickness, bar_length, corner, corner)
                    fill = int(bar_length * (pct / 100.0))
                    if fill > 0:
                        painter.setBrush(QBrush(get_fill_color(pct, i)))
                        if efd == "from-top":
                            painter.drawRoundedRect(x, y, bar_thickness, fill, corner, corner)
                        else:
                            painter.drawRoundedRect(x, y + bar_length - fill, bar_thickness, fill, corner, corner)
            else:
                bar_length = 12
                bar_thickness = 8
                gap = 4
                x = (self.width() - bar_thickness * count - gap * (count - 1)) // 2
                y = (self.height() - bar_length) // 2
                for i, pct in enumerate(percentages):
                    bx = x + i * (bar_thickness + gap)
                    corner = bar_corner if bar_corner > 0 else bar_thickness // 2
                    corner = min(corner, bar_thickness // 2)
                    painter.setBrush(QBrush(QColor(30, 30, 35, 200)))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(bx, y, bar_thickness, bar_length, corner, corner)
                    fill = int(bar_length * (pct / 100.0))
                    if fill > 0:
                        painter.setBrush(QBrush(get_fill_color(pct, i)))
                        if efd == "from-top":
                            painter.drawRoundedRect(bx, y, bar_thickness, fill, corner, corner)
                        else:
                            painter.drawRoundedRect(bx, y + bar_length - fill, bar_thickness, fill, corner, corner)
        else:
            d = 24
            gap = 8
            y = (self.height() - d) // 2
            total_w = count * d + (count - 1) * gap
            x_start = (self.width() - total_w) // 2
            
            for i, pct in enumerate(percentages):
                x = x_start + i * (d + gap)
                rect = QRectF(x, y, d, d)
                
                if overlay_style == "ring":
                    thickness = 3
                    painter.setPen(QPen(QColor(30, 30, 35, 200), thickness))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawArc(rect, 0, 360 * 16)
                    painter.setPen(QPen(get_fill_color(pct, i), thickness))
                    span = -int(360 * 16 * (pct / 100.0))
                    if efd == "counterclockwise":
                        painter.drawArc(rect, 90 * 16, -span)
                    else:
                        painter.drawArc(rect, 90 * 16, span)
                elif overlay_style == "pie":
                    painter.setBrush(QBrush(QColor(30, 30, 35, 200)))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(rect)
                    painter.setBrush(QBrush(get_fill_color(pct, i)))
                    span = -int(360 * 16 * (pct / 100.0))
                    if efd == "counterclockwise":
                        painter.drawPie(rect, 90 * 16, -span)
                    else:
                        painter.drawPie(rect, 90 * 16, span)
                else:
                    painter.setBrush(QBrush(QColor(30, 30, 35, 200)))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(rect)
                    if pct > 0:
                        c = get_fill_color(pct, i)
                        painter.setBrush(QBrush(c))
                        painter.save()
                        painter.setClipRect(rect, Qt.IntersectClip)
                        fill_h = d * (pct / 100.0)
                        if efd == "from-top":
                            fr = QRectF(x, y, d, fill_h)
                        else:
                            fr = QRectF(x, y + d - fill_h, d, fill_h)
                        painter.drawRect(fr)
                        painter.restore()
        
        painter.setOpacity(1.0)


# ============================================================
# 主页
# ============================================================
class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("home_page")
        self.config = load_config()
        self.presets_data = load_presets(self.config)
        self.overlay = None
        self.cards = []
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)
        
        title = SubtitleLabel("终末地连携监测", self)
        self.layout.addWidget(title)
        
        desc = BodyLabel("实时监测角色的连携状态，悬浮窗显示在游戏上方。", self)
        self.layout.addWidget(desc)
        
        self.card_container = QWidget(self)
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(10)
        self.layout.addWidget(self.card_container)
        
        # 按钮区：启动 / 暂停 / 停止
        btn_layout = QHBoxLayout()
        self.start_btn = PrimaryPushButton("启动悬浮窗", self)
        self.start_btn.clicked.connect(self.start_overlay)
        btn_layout.addWidget(self.start_btn)
        
        self.pause_btn = PushButton("暂停", self)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        btn_layout.addWidget(self.pause_btn)
        
        self.stop_btn = PushButton("停止悬浮窗", self)
        self.stop_btn.clicked.connect(self.stop_overlay)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        self.layout.addLayout(btn_layout)
        
        # 预设行
        preset_row = QHBoxLayout()
        preset_row.addWidget(BodyLabel("当前预设：", self))
        
        self.preset_combo = ComboBox(self)
        self.refresh_preset_combo()
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_row.addWidget(self.preset_combo)
        
        self.menu_btn = PushButton("⋯", self)
        self.menu_btn.setFixedWidth(40)
        self.menu_btn.clicked.connect(self.show_preset_menu)
        preset_row.addWidget(self.menu_btn)
        
        preset_row.addSpacing(20)
        
        # 应用坐标开关
        preset_row.addWidget(BodyLabel("应用坐标", self))
        self.apply_pos_switch = SwitchButton(self)
        self.apply_pos_switch.setOnText("是")
        self.apply_pos_switch.setOffText("否")
        self.apply_pos_switch.setChecked(self.config.get("apply_preset_pos", False))
        self.apply_pos_switch.checkedChanged.connect(self.on_apply_pos_changed)
        preset_row.addWidget(self.apply_pos_switch)
        
        preset_row.addSpacing(10)
        
        # 启用预览开关
        preset_row.addWidget(BodyLabel("启用预览", self))
        self.preview_switch = SwitchButton(self)
        self.preview_switch.setOnText("是")
        self.preview_switch.setOffText("否")
        self.preview_switch.setChecked(self.config.get("preview_enabled", True))
        self.preview_switch.checkedChanged.connect(self.on_preview_enabled_changed)
        preset_row.addWidget(self.preview_switch)
        
        preset_row.addStretch()
        self.layout.addLayout(preset_row)
        
        # 预览区（单独一行，居中）
        preview_row = QHBoxLayout()
        preview_row.addStretch()
        self.preset_preview = PresetPreview(self)
        self.preset_preview.setFixedSize(220, 110)
        preview_row.addWidget(self.preset_preview)
        preview_row.addStretch()
        self.layout.addLayout(preview_row)
        
        self.update_preview()
        self.update_preview_visibility()
        
        self.layout.addStretch()
        self.rebuild_cards()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(200)
    
    def toggle_pause(self):
        """暂停/继续切换"""
        if self.overlay is None:
            return
        if self.overlay.paused:
            self.overlay.resume()
            self.pause_btn.setText("暂停")
        else:
            self.overlay.pause()
            self.pause_btn.setText("继续")
    
    def refresh_preset_combo(self):
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        names = list(self.presets_data["presets"].keys())
        self.preset_combo.addItems(names)
        current = self.presets_data.get("current", "默认")
        if current in names:
            self.preset_combo.setCurrentText(current)
        self.preset_combo.blockSignals(False)
    
    def update_preview(self):
        if not self.config.get("preview_enabled", True):
            return
        current = self.presets_data.get("current", "默认")
        style = self.presets_data["presets"].get(current, {})
        self.preset_preview.update_preview(style)
    
    def update_preview_visibility(self):
        """预览区：禁用时清空内容，保留占位"""
        enabled = self.config.get("preview_enabled", True)
        if enabled:
            current = self.presets_data.get("current", "默认")
            style = self.presets_data["presets"].get(current, {})
            self.preset_preview.update_preview(style)
        else:
            self.preset_preview.update_preview({})
    
    def on_apply_pos_changed(self, checked):
        self.config["apply_preset_pos"] = checked
        save_config(self.config)
        self.config = load_config()
    
    def on_preview_enabled_changed(self, checked):
        self.config["preview_enabled"] = checked
        save_config(self.config)
        self.config = load_config()
        self.update_preview_visibility()
    
    def on_preset_changed(self, name):
        if not name or name not in self.presets_data["presets"]:
            return
        self.presets_data["current"] = name
        save_presets(self.presets_data)
        style = self.presets_data["presets"][name]
        latest_config = load_config()
        
        apply_pos = latest_config.get("apply_preset_pos", False)
        
        if apply_pos:
            # 应用坐标：完整覆盖
            latest_config = apply_style(latest_config, style)
        else:
            # 不应用坐标：只覆盖样式，保留当前坐标
            style_no_pos = {k: v for k, v in style.items() 
                            if k not in ("areas", "horizontal_pos", "vertical_pos", "base_width", "base_height")}
            latest_config = apply_style(latest_config, style_no_pos)
        
        save_config(latest_config)
        self.config = latest_config
        
        if self.overlay:
            self.overlay.apply_config(latest_config)
        
        if hasattr(self, 'settings_page_ref') and self.settings_page_ref:
            self.settings_page_ref.reload_from_config()
        self.update_preview()
    
    def show_preset_menu(self):
        menu = RoundMenu(parent=self)
        a1 = Action("保存当前为预设", self)
        a1.triggered.connect(self.save_current_preset)
        menu.addAction(a1)
        a2 = Action("新建预设...", self)
        a2.triggered.connect(self.new_preset)
        menu.addAction(a2)
        a3 = Action("重命名当前预设...", self)
        a3.triggered.connect(self.rename_current_preset)
        menu.addAction(a3)
        menu.addSeparator()
        a4 = Action("删除当前预设", self)
        a4.triggered.connect(self.delete_current_preset)
        menu.addAction(a4)
        menu.addSeparator()
        a5 = Action("导入预设...", self)
        a5.triggered.connect(self.import_presets_file)
        menu.addAction(a5)
        a6 = Action("导出预设...", self)
        a6.triggered.connect(self.export_presets_file)
        menu.addAction(a6)
        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))
    
    def save_current_preset(self):
        latest_config = load_config()
        self.config = latest_config
        update_current(self.presets_data, latest_config)
        self.update_preview()
        InfoBar.success(title="已保存", content="当前设置已保存到预设",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=2000, parent=self)
    
    def new_preset(self):
        name, ok = QInputDialog.getText(self, "新建预设", "预设名称：")
        if ok and name.strip():
            latest_config = load_config()
            self.config = latest_config
            actual = add_preset(self.presets_data, name.strip(), latest_config)
            self.presets_data["current"] = actual
            save_presets(self.presets_data)
            self.refresh_preset_combo()
            self.update_preview()
            InfoBar.success(title="已创建", content=f"预设「{actual}」已创建",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=2000, parent=self)
    
    def rename_current_preset(self):
        current = self.presets_data.get("current", "默认")
        name, ok = QInputDialog.getText(self, "重命名预设", "新名称：", text=current)
        if ok and name.strip() and name.strip() != current:
            rename_preset(self.presets_data, current, name.strip())
            self.refresh_preset_combo()
            InfoBar.success(title="已重命名", content=f"预设已重命名为「{name.strip()}」",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=2000, parent=self)
    
    def delete_current_preset(self):
        current = self.presets_data.get("current", "默认")
        if len(self.presets_data["presets"]) <= 1:
            InfoBar.warning(title="无法删除", content="至少保留一个预设",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=2000, parent=self)
            return
        box = MessageBox("删除预设", f"确定删除预设「{current}」吗？", self)
        if box.exec():
            delete_preset(self.presets_data, current)
            self.refresh_preset_combo()
            new_current = self.presets_data["current"]
            self.on_preset_changed(new_current)
    
    def import_presets_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入预设", "", "JSON (*.json)")
        if path:
            data = import_presets(path)
            if data:
                self.presets_data = data
                save_presets(self.presets_data)
                self.refresh_preset_combo()
                self.update_preview()
                InfoBar.success(title="导入成功", content="预设已导入",
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=2000, parent=self)
            else:
                InfoBar.error(title="导入失败", content="文件格式错误",
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=2000, parent=self)
    
    def export_presets_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出预设", "presets_backup.json", "JSON (*.json)")
        if path:
            if export_presets(self.presets_data, path):
                InfoBar.success(title="导出成功", content=path,
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=2000, parent=self)
            else:
                InfoBar.error(title="导出失败", content="写入文件失败",
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=2000, parent=self)
    
    def rebuild_cards(self):
        for card in self.cards:
            card.setParent(None)
        self.cards = []
        count = self.config.get("character_count", 4)
        for i in range(count):
            card = CardWidget(self.card_container)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(20, 15, 20, 15)
            label = BodyLabel(f"角色 {i+1}", card)
            label.setFixedWidth(80)
            card_layout.addWidget(label)
            bar = ProgressBar(card)
            bar.setValue(0)
            bar.setFixedHeight(12)
            card_layout.addWidget(bar)
            percent_label = BodyLabel("0%", card)
            percent_label.setFixedWidth(50)
            percent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            card_layout.addWidget(percent_label)
            self.cards.append(card)
            self.card_layout.addWidget(card)
    
    def start_overlay(self):
        if self.overlay is None:
            self.overlay = Overlay(self.config)
        self.overlay.apply_config(self.config)
        self.overlay.start()
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("暂停")
        self.stop_btn.setEnabled(True)
    
    def stop_overlay(self):
        if self.overlay:
            self.overlay.stop()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("暂停")
        self.stop_btn.setEnabled(False)
    
    def refresh(self):
        count = self.config.get("character_count", 4)
        if len(self.cards) != count:
            self.rebuild_cards()
        
        from capture import check_ui_available
        available = check_ui_available(self.config)
        if any(available):
            percentages = capture_all(self.config)
        else:
            percentages = [0.0] * count
        
        for i, card in enumerate(self.cards):
            if i < len(percentages):
                bar = card.findChild(ProgressBar)
                labels = card.findChildren(BodyLabel)
                if bar and labels:
                    label = labels[-1]
                    bar.setValue(int(percentages[i]))
                    label.setText(f"{int(percentages[i])}%")
# ============================================================
# 设置页
# ============================================================
class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_page")
        self.config = load_config()
        self.main_window = parent
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(120, 120, 120, 180);
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(160, 160, 160, 220);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        scroll.viewport().setStyleSheet("background: transparent;")
        outer_layout.addWidget(scroll)
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        scroll.setWidget(content)
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(4)
        
        title = SubtitleLabel("设置", self)
        layout.addWidget(title)
        
        pos_map = {"center": 0, "top": 1, "bottom": 2, "left": 3, "right": 4, "none": 5}
        
        # ==================== 基础设置 ====================
        layout.addWidget(make_group_title("基础设置", self))
        
        card1 = CardWidget(self)
        self.g1 = QGridLayout(card1)
        self.g1.setContentsMargins(20, 16, 20, 16)
        self.g1.setVerticalSpacing(12)
        
        r, self.count_combo = make_combo_row(
            "角色数量", ["1", "2", "3", "4"],
            self.config.get("character_count", 4) - 1, card1, self.on_count_changed)
        self.g1.addLayout(r, 0, 0, 1, 2)
        
        r, self.close_switch = make_switch_row(
            "关闭窗口时最小化到托盘", self.config.get("close_to_tray", True),
            card1, lambda c: self.set_config("close_to_tray", c))
        self.g1.addLayout(r, 1, 0, 1, 2)
        
        r, self.theme_switch = make_switch_row(
            "深色主题", self.config.get("theme", "dark") == "dark",
            card1, self.on_theme_changed)
        self.g1.addLayout(r, 2, 0, 1, 2)
        
        r, self.hide_switch = make_switch_row(
            "游戏不在前台时隐藏", self.config.get("auto_hide_when_no_game", False),
            card1, lambda c: self.set_config("auto_hide_when_no_game", c))
        self.g1.addLayout(r, 3, 0, 1, 2)
        
        r, self.hide_no_bar_switch = make_switch_row(
            "无能量条时自动隐藏", self.config.get("auto_hide_no_bar", False),
            card1, lambda c: self.set_config("auto_hide_no_bar", c))
        self.g1.addLayout(r, 4, 0, 1, 2)
        
        r, self.hide_anim_combo = make_combo_row(
            "隐藏动画", ["淡入淡出", "即时"],
            0 if self.config.get("hide_animation", "fade") == "fade" else 1,
            card1, self.on_hide_anim_changed)
        self.g1.addLayout(r, 5, 0, 1, 2)
        
        r, self.fade_dur_slider, self.fade_dur_edit = make_slider_row(
            "动画时长(ms)", 100, 1000, self.config.get("fade_duration", 300),
            card1, lambda v: self.set_config("fade_duration", v))
        self.g1.addLayout(r, 6, 0, 1, 2)
        self.fade_dur_label = r.itemAt(0).widget()
        
        style_map = {"bar": 0, "ring": 1, "pie": 2, "solid": 3}
        r, self.style_combo = make_combo_row(
            "悬浮窗样式", ["长条", "圆环", "饼图", "实心圆"],
            style_map.get(self.config.get("overlay_style", "bar"), 0),
            card1, self.on_style_changed)
        self.g1.addLayout(r, 7, 0, 1, 2)
        
        r, self.dir_combo = make_combo_row(
            "排列方向", ["横排", "竖排"],
            0 if self.config.get("overlay_direction") == "horizontal" else 1,
            card1, self.on_direction_changed)
        self.g1.addLayout(r, 8, 0, 1, 2)
        
        r, self.bar_orient_combo = make_combo_row(
            "条方向", ["横条", "竖条"],
            0 if self.config.get("bar_orientation", "horizontal") == "horizontal" else 1,
            card1, self.on_bar_orient_changed)
        self.g1.addLayout(r, 9, 0, 1, 2)
        self.bar_orient_label = r.itemAt(0).widget()
        
        r, self.fill_dir_combo = make_combo_row(
            "填充方向", ["从左到右"],
            0, card1, self.on_fill_dir_changed)
        self.g1.addLayout(r, 10, 0, 1, 2)
        self.fill_dir_label = r.itemAt(0).widget()
        
        layout.addWidget(card1)
        
        self._update_fill_dir_options()
        self._update_anim_visibility()
        
        # ==================== 悬浮窗外观 ====================
        layout.addWidget(make_group_title("悬浮窗外观", self))
        
        card2 = CardWidget(self)
        g2 = QVBoxLayout(card2)
        g2.setContentsMargins(20, 16, 20, 16)
        g2.setSpacing(8)
        
        r, self.opacity_slider, self.opacity_edit = make_slider_row(
            "整体透明度", 10, 100, self.config.get("overlay_opacity", 80),
            card2, lambda v: self.set_config("overlay_opacity", v))
        g2.addLayout(r)
        
        r, self.bg_slider, self.bg_edit = make_slider_row(
            "背景透明度", 0, 255, self.config.get("bg_opacity", 0),
            card2, lambda v: self.set_config("bg_opacity", v))
        g2.addLayout(r)
        
        r, self.bg_corner_slider, self.bg_corner_edit = make_slider_row(
            "背景圆角", 0, 30, self.config.get("bg_corner_radius", 0),
            card2, lambda v: self.set_config("bg_corner_radius", v))
        g2.addLayout(r)
        
        r, self.bar_corner_slider, self.bar_corner_edit = make_slider_row(
            "进度条圆角", 0, 30, self.config.get("bar_corner_radius", 0),
            card2, lambda v: self.set_config("bar_corner_radius", v))
        g2.addLayout(r)
        
        r, self.margin_slider, self.margin_edit = make_slider_row(
            "窗口边距", 0, 100, self.config.get("window_margin", 35),
            card2, lambda v: self.set_config("window_margin", v))
        g2.addLayout(r)
        
        r, self.unavail_slider, self.unavail_edit = make_slider_row(
            "角色不可用透明度", 0, 100, self.config.get("unavailable_opacity", 30),
            card2, lambda v: self.set_config("unavailable_opacity", v))
        g2.addLayout(r)
        
        r, self.border_switch = make_switch_row(
            "启用边框", self.config.get("border_enabled", False),
            card2, lambda c: self.set_config("border_enabled", c))
        g2.addLayout(r)
        
        bc_row = QHBoxLayout()
        bc_row.addWidget(BodyLabel("边框颜色", card2))
        self.color_btn = PushButton("选择颜色", card2)
        self.color_btn.clicked.connect(self.pick_border_color)
        self.update_color_btn()
        bc_row.addWidget(self.color_btn)
        bc_row.addSpacing(20)
        bc_row.addWidget(BodyLabel("粗细", card2))
        self.border_width_slider = Slider(Qt.Horizontal, card2)
        self.border_width_slider.setRange(1, 5)
        self.border_width_slider.setValue(self.config.get("border_width", 2))
        self.border_width_slider.setFixedWidth(80)
        self.border_width_edit = LineEdit(card2)
        self.border_width_edit.setFixedWidth(40)
        self.border_width_edit.setText(str(self.config.get("border_width", 2)))
        def bw_slider(val):
            self.border_width_edit.setText(str(val))
            self.set_config("border_width", val)
        def bw_edit():
            try:
                v = int(self.border_width_edit.text())
                if v < 1 or v > 5: raise ValueError
                self.border_width_slider.setValue(v)
                self.set_config("border_width", v)
            except ValueError:
                self.border_width_edit.setText(str(self.border_width_slider.value()))
        self.border_width_slider.valueChanged.connect(bw_slider)
        self.border_width_edit.editingFinished.connect(bw_edit)
        bc_row.addWidget(self.border_width_slider)
        bc_row.addWidget(self.border_width_edit)
        bc_row.addStretch()
        g2.addLayout(bc_row)
        
        layout.addWidget(card2)
        
        # ==================== 角色颜色 ====================
        layout.addWidget(make_group_title("角色颜色", self))
        
        card_rc = CardWidget(self)
        grc = QVBoxLayout(card_rc)
        grc.setContentsMargins(20, 16, 20, 16)
        grc.setSpacing(8)
        
        r, self.rc_enabled_switch = make_switch_row(
            "启用角色独立颜色", self.config.get("role_color_enabled", False),
            card_rc, self.on_role_color_enabled_changed)
        grc.addLayout(r)
        
        self.rc_rows = []
        self.rc_btns = []
        for i in range(4):
            r, btn = make_color_row(
                f"角色 {i+1} 颜色",
                self.config.get(f"role_color_{i+1}", "#FFFFFF"),
                card_rc,
                lambda color, idx=i: self.on_role_color_changed(idx, color))
            grc.addLayout(r)
            self.rc_rows.append(r)
            self.rc_btns.append(btn)
        
        layout.addWidget(card_rc)
        
        self._update_role_color_visibility()
        
        # ==================== 高亮 ====================
        layout.addWidget(make_group_title("高亮（光晕）", self))
        
        card_hl = CardWidget(self)
        ghl = QVBoxLayout(card_hl)
        ghl.setContentsMargins(20, 16, 20, 16)
        ghl.setSpacing(8)
        
        r, self.hl_switch = make_switch_row(
            "启用高亮", self.config.get("highlight_enabled", True),
            card_hl, lambda c: self.set_config("highlight_enabled", c))
        ghl.addLayout(r)
        
        r, self.hl_thresh_slider, self.hl_thresh_edit = make_slider_row(
            "高亮阈值", 0, 100, self.config.get("highlight_threshold", 50),
            card_hl, lambda v: self.set_config("highlight_threshold", v))
        ghl.addLayout(r)
        
        hl_color_row = QHBoxLayout()
        hl_color_row.addWidget(BodyLabel("高亮颜色", card_hl))
        hl_color_row.addStretch()
        self.hl_color_btn = PushButton("选择颜色", card_hl)
        self.hl_color_btn.clicked.connect(self.pick_highlight_color)
        self.update_hl_color_btn()
        hl_color_row.addWidget(self.hl_color_btn)
        ghl.addLayout(hl_color_row)
        
        r, self.hl_width_slider, self.hl_width_edit = make_slider_row(
            "高亮粗细", 1, 10, self.config.get("highlight_width", 2),
            card_hl, lambda v: self.set_config("highlight_width", v))
        ghl.addLayout(r)
        
        r, self.hl_layers_slider, self.hl_layers_edit = make_slider_row(
            "高亮层数", 1, 3, self.config.get("highlight_layers", 2),
            card_hl, lambda v: self.set_config("highlight_layers", v))
        ghl.addLayout(r)
        
        layout.addWidget(card_hl)
        
        # ==================== 尺寸 ====================
        layout.addWidget(make_group_title("尺寸", self))
        
        self.card_size = CardWidget(self)
        self.size_layout = QVBoxLayout(self.card_size)
        self.size_layout.setContentsMargins(20, 16, 20, 16)
        self.size_layout.setSpacing(8)
        self.rebuild_size_widgets()
        layout.addWidget(self.card_size)
        
        # ==================== 序号样式 ====================
        layout.addWidget(make_group_title("序号样式", self))
        
        card3 = CardWidget(self)
        g3 = QVBoxLayout(card3)
        g3.setContentsMargins(20, 16, 20, 16)
        g3.setSpacing(8)
        
        r, self.num_visible_switch = make_switch_row(
            "显示序号", self.config.get("number_visible", True),
            card3, lambda c: self.set_config("number_visible", c))
        g3.addLayout(r)
        
        r, self.num_pos_combo = make_combo_row(
            "序号位置", ["中心", "上方", "下方", "左侧", "右侧", "不显示"],
            pos_map.get(self.config.get("number_position", "left"), 3),
            card3, self.on_num_pos_changed)
        g3.addLayout(r)
        
        r, self.num_offset_slider, self.num_offset_edit = make_slider_row(
            "序号距离", -20, 20, self.config.get("number_offset", 5),
            card3, lambda v: self.set_config("number_offset", v))
        g3.addLayout(r)
        
        r, self.num_font_slider, self.num_font_edit = make_slider_row(
            "序号字体大小", 6, 20, self.config.get("number_font_size", 9),
            card3, lambda v: self.set_config("number_font_size", v))
        g3.addLayout(r)
        
        current_nw = self.config.get("number_font_weight", 700)
        nw_idx = 1 if current_nw >= 700 else 0
        r, self.num_weight_combo = make_combo_row(
            "序号字体粗细", ["默认", "加粗"],
            nw_idx, card3, self.on_num_weight_changed)
        g3.addLayout(r)
        
        nc_row = QHBoxLayout()
        nc_row.addWidget(BodyLabel("序号字体颜色", card3))
        nc_row.addStretch()
        self.num_color_btn = PushButton("选择颜色", card3)
        self.num_color_btn.clicked.connect(self.pick_number_color)
        self.update_num_color_btn()
        nc_row.addWidget(self.num_color_btn)
        g3.addLayout(nc_row)
        
        layout.addWidget(card3)
        
        # ==================== 百分比样式 ====================
        layout.addWidget(make_group_title("百分比样式", self))
        
        card4 = CardWidget(self)
        g4 = QVBoxLayout(card4)
        g4.setContentsMargins(20, 16, 20, 16)
        g4.setSpacing(8)
        
        r, self.pct_visible_switch = make_switch_row(
            "显示百分比", self.config.get("percentage_visible", True),
            card4, lambda c: self.set_config("percentage_visible", c))
        g4.addLayout(r)
        
        r, self.pct_pos_combo = make_combo_row(
            "百分比位置", ["中心", "上方", "下方", "左侧", "右侧", "不显示"],
            pos_map.get(self.config.get("percentage_position", "right"), 4),
            card4, self.on_pct_pos_changed)
        g4.addLayout(r)
        
        r, self.pct_offset_slider, self.pct_offset_edit = make_slider_row(
            "百分比距离", -20, 20, self.config.get("percentage_offset", 5),
            card4, lambda v: self.set_config("percentage_offset", v))
        g4.addLayout(r)
        
        r, self.pct_font_slider, self.pct_font_edit = make_slider_row(
            "百分比字体大小", 6, 20, self.config.get("percentage_font_size", 8),
            card4, lambda v: self.set_config("percentage_font_size", v))
        g4.addLayout(r)
        
        current_pw = self.config.get("percentage_font_weight", 400)
        pw_idx = 1 if current_pw >= 700 else 0
        r, self.pct_weight_combo = make_combo_row(
            "百分比字体粗细", ["默认", "加粗"],
            pw_idx, card4, self.on_pct_weight_changed)
        g4.addLayout(r)
        
        pc_row = QHBoxLayout()
        pc_row.addWidget(BodyLabel("百分比字体颜色", card4))
        pc_row.addStretch()
        self.pct_color_btn = PushButton("选择颜色", card4)
        self.pct_color_btn.clicked.connect(self.pick_percentage_color)
        self.update_pct_color_btn()
        pc_row.addWidget(self.pct_color_btn)
        g4.addLayout(pc_row)
        
        layout.addWidget(card4)
        
        # ==================== 其他 ====================
        layout.addWidget(make_group_title("其他", self))
        
        card5 = CardWidget(self)
        g5 = QVBoxLayout(card5)
        g5.setContentsMargins(20, 16, 20, 16)
        g5.setSpacing(8)
        
        tip = BodyLabel("按住 Ctrl 键，用鼠标拖动悬浮窗调整位置。位置会自动保存。", card5)
        g5.addWidget(tip)
        
        reset_pos_btn = PushButton("恢复默认位置", card5)
        reset_pos_btn.clicked.connect(self.reset_position)
        g5.addWidget(reset_pos_btn)
        
        r, self.debug_switch = make_switch_row(
            "调试模式（每5秒记录识别数据）", self.config.get("debug_mode", False),
            card5, self.on_debug_changed)
        g5.addLayout(r)
        
        r, self.log_switch = make_switch_row(
            "启用日志记录", self.config.get("log_enabled", False),
            card5, self.on_log_enabled_changed)
        g5.addLayout(r)
        
        r, self.log_file_switch = make_switch_row(
            "保存日志到文件", self.config.get("log_to_file", False),
            card5, self.on_log_file_changed)
        g5.addLayout(r)
        
        cfg_row = QHBoxLayout()
        reset_btn = PushButton("恢复默认设置", card5)
        reset_btn.clicked.connect(self.reset_config)
        cfg_row.addWidget(reset_btn)
        export_btn = PushButton("导出配置", card5)
        export_btn.clicked.connect(self.export_config)
        cfg_row.addWidget(export_btn)
        import_btn = PushButton("导入配置", card5)
        import_btn.clicked.connect(self.import_config)
        cfg_row.addWidget(import_btn)
        g5.addLayout(cfg_row)
        
        layout.addWidget(card5)
        layout.addStretch()
        
        self._update_orient_visibility()
        self._update_role_color_visibility()
    
    def _update_orient_visibility(self):
        style = self.config.get("overlay_style", "bar")
        if style == "bar":
            self.bar_orient_label.setVisible(True)
            self.bar_orient_combo.setVisible(True)
            self.fill_dir_label.setVisible(True)
            self.fill_dir_combo.setVisible(True)
        else:
            self.bar_orient_label.setVisible(False)
            self.bar_orient_combo.setVisible(False)
            self.fill_dir_label.setVisible(True)
            self.fill_dir_combo.setVisible(True)
    
    def _update_anim_visibility(self):
        anim = self.config.get("hide_animation", "fade")
        visible = (anim == "fade")
        try:
            self.fade_dur_label.setVisible(visible)
            self.fade_dur_slider.setVisible(visible)
            self.fade_dur_edit.setVisible(visible)
        except:
            pass
    
    def _update_role_color_visibility(self):
        count = self.config.get("character_count", 4)
        for i in range(4):
            visible = (i < count)
            try:
                row = self.rc_rows[i]
                for j in range(row.count()):
                    w = row.itemAt(j).widget()
                    if w:
                        w.setVisible(visible)
            except:
                pass
    
    def _update_fill_dir_options(self):
        style = self.config.get("overlay_style", "bar")
        bar_orient = self.config.get("bar_orientation", "horizontal")
        current = self.config.get("fill_direction", "")
        
        if style == "bar":
            if bar_orient == "horizontal":
                options = ["from-left", "from-right"]
                labels = ["从左到右", "从右到左"]
            else:
                options = ["from-bottom", "from-top"]
                labels = ["从下到上", "从上到下"]
        elif style in ("ring", "pie"):
            options = ["clockwise", "counterclockwise"]
            labels = ["顺时针", "逆时针"]
        elif style == "solid":
            options = ["from-bottom", "from-top"]
            labels = ["从下到上", "从上到下"]
        else:
            options = ["from-bottom"]
            labels = ["从下到上"]
        
        self._fill_dir_options = options
        self.fill_dir_combo.blockSignals(True)
        self.fill_dir_combo.clear()
        self.fill_dir_combo.addItems(labels)
        if current in options:
            self.fill_dir_combo.setCurrentIndex(options.index(current))
        else:
            self.fill_dir_combo.setCurrentIndex(0)
            self.config["fill_direction"] = options[0]
            save_config(self.config)
        self.fill_dir_combo.blockSignals(False)
    
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
            elif item.layout():
                self._clear_layout(item.layout())
    
    def rebuild_size_widgets(self):
        self._clear_layout(self.size_layout)
        
        style = self.config.get("overlay_style", "bar")
        direction = self.config.get("overlay_direction", "vertical")
        prefix = "size_h_" if direction == "horizontal" else "size_v_"
        
        if style == "bar":
            r, _, _ = make_slider_row(
                "条长度", 30, 500, self.config.get(prefix + "bar_length", 200),
                self.card_size, lambda v: self.on_size_changed(prefix + "bar_length", v))
            self.size_layout.addLayout(r)
            r, _, _ = make_slider_row(
                "条粗细", 3, 50, self.config.get(prefix + "bar_thickness", 10),
                self.card_size, lambda v: self.on_size_changed(prefix + "bar_thickness", v))
            self.size_layout.addLayout(r)
            r, _, _ = make_slider_row(
                "条间距", 0, 100, self.config.get(prefix + "bar_gap", 8),
                self.card_size, lambda v: self.on_size_changed(prefix + "bar_gap", v))
            self.size_layout.addLayout(r)
        else:
            r, _, _ = make_slider_row(
                "圆环直径", 20, 200, self.config.get(prefix + "circle_diameter", 60),
                self.card_size, lambda v: self.on_size_changed(prefix + "circle_diameter", v))
            self.size_layout.addLayout(r)
            if style == "ring":
                r, _, _ = make_slider_row(
                    "圆环粗细", 2, 30, self.config.get(prefix + "circle_thickness", 6),
                    self.card_size, lambda v: self.on_size_changed(prefix + "circle_thickness", v))
                self.size_layout.addLayout(r)
            r, _, _ = make_slider_row(
                "圆间距", 0, 100, self.config.get(prefix + "circle_gap", 8),
                self.card_size, lambda v: self.on_size_changed(prefix + "circle_gap", v))
            self.size_layout.addLayout(r)
    
    def reload_from_config(self):
        self.config = load_config()
        pos_map = {"center": 0, "top": 1, "bottom": 2, "left": 3, "right": 4, "none": 5}
        style_map = {"bar": 0, "ring": 1, "pie": 2, "solid": 3}
        
        widgets = [
            self.count_combo, self.close_switch, self.theme_switch,
            self.hide_switch, self.hide_no_bar_switch, self.hide_anim_combo,
            self.fade_dur_slider,
            self.style_combo, self.dir_combo, self.bar_orient_combo,
            self.opacity_slider, self.bg_slider, self.bg_corner_slider,
            self.bar_corner_slider, self.margin_slider, self.unavail_slider,
            self.border_switch, self.border_width_slider,
            self.rc_enabled_switch,
            self.hl_switch, self.hl_thresh_slider, self.hl_width_slider, self.hl_layers_slider,
            self.num_visible_switch, self.num_pos_combo, self.num_offset_slider,
            self.num_font_slider, self.num_weight_combo,
            self.pct_visible_switch, self.pct_pos_combo, self.pct_offset_slider,
            self.pct_font_slider, self.pct_weight_combo,
            self.debug_switch, self.log_switch, self.log_file_switch,
        ]
        for w in widgets:
            try:
                w.blockSignals(True)
            except:
                pass
        
        self.count_combo.setCurrentIndex(self.config.get("character_count", 4) - 1)
        self.close_switch.setChecked(self.config.get("close_to_tray", True))
        self.theme_switch.setChecked(self.config.get("theme", "dark") == "dark")
        self.hide_switch.setChecked(self.config.get("auto_hide_when_no_game", False))
        self.hide_no_bar_switch.setChecked(self.config.get("auto_hide_no_bar", False))
        self.hide_anim_combo.setCurrentIndex(0 if self.config.get("hide_animation", "fade") == "fade" else 1)
        self.fade_dur_slider.setValue(self.config.get("fade_duration", 300))
        self.fade_dur_edit.setText(str(self.config.get("fade_duration", 300)))
        self.style_combo.setCurrentIndex(style_map.get(self.config.get("overlay_style", "bar"), 0))
        self.dir_combo.setCurrentIndex(0 if self.config.get("overlay_direction") == "horizontal" else 1)
        self.bar_orient_combo.setCurrentIndex(0 if self.config.get("bar_orientation", "horizontal") == "horizontal" else 1)
        
        self.opacity_slider.setValue(self.config.get("overlay_opacity", 80))
        self.opacity_edit.setText(str(self.config.get("overlay_opacity", 80)))
        self.bg_slider.setValue(self.config.get("bg_opacity", 0))
        self.bg_edit.setText(str(self.config.get("bg_opacity", 0)))
        self.bg_corner_slider.setValue(self.config.get("bg_corner_radius", 0))
        self.bg_corner_edit.setText(str(self.config.get("bg_corner_radius", 0)))
        self.bar_corner_slider.setValue(self.config.get("bar_corner_radius", 0))
        self.bar_corner_edit.setText(str(self.config.get("bar_corner_radius", 0)))
        self.margin_slider.setValue(self.config.get("window_margin", 35))
        self.margin_edit.setText(str(self.config.get("window_margin", 35)))
        self.unavail_slider.setValue(self.config.get("unavailable_opacity", 30))
        self.unavail_edit.setText(str(self.config.get("unavailable_opacity", 30)))
        self.border_switch.setChecked(self.config.get("border_enabled", False))
        self.border_width_slider.setValue(self.config.get("border_width", 2))
        self.border_width_edit.setText(str(self.config.get("border_width", 2)))
        
        self.rc_enabled_switch.setChecked(self.config.get("role_color_enabled", False))
        for i in range(4):
            color = self.config.get(f"role_color_{i+1}", "#FFFFFF")
            self.rc_btns[i].setText(color)
        
        self.hl_switch.setChecked(self.config.get("highlight_enabled", True))
        self.hl_thresh_slider.setValue(self.config.get("highlight_threshold", 50))
        self.hl_thresh_edit.setText(str(self.config.get("highlight_threshold", 50)))
        self.hl_width_slider.setValue(self.config.get("highlight_width", 2))
        self.hl_width_edit.setText(str(self.config.get("highlight_width", 2)))
        self.hl_layers_slider.setValue(self.config.get("highlight_layers", 2))
        self.hl_layers_edit.setText(str(self.config.get("highlight_layers", 2)))
        
        self.num_visible_switch.setChecked(self.config.get("number_visible", True))
        self.num_pos_combo.setCurrentIndex(pos_map.get(self.config.get("number_position", "left"), 3))
        self.num_offset_slider.setValue(self.config.get("number_offset", 5))
        self.num_offset_edit.setText(str(self.config.get("number_offset", 5)))
        self.num_font_slider.setValue(self.config.get("number_font_size", 9))
        self.num_font_edit.setText(str(self.config.get("number_font_size", 9)))
        nw = self.config.get("number_font_weight", 700)
        self.num_weight_combo.setCurrentIndex(1 if nw >= 700 else 0)
        
        self.pct_visible_switch.setChecked(self.config.get("percentage_visible", True))
        self.pct_pos_combo.setCurrentIndex(pos_map.get(self.config.get("percentage_position", "right"), 4))
        self.pct_offset_slider.setValue(self.config.get("percentage_offset", 5))
        self.pct_offset_edit.setText(str(self.config.get("percentage_offset", 5)))
        self.pct_font_slider.setValue(self.config.get("percentage_font_size", 8))
        self.pct_font_edit.setText(str(self.config.get("percentage_font_size", 8)))
        pw = self.config.get("percentage_font_weight", 400)
        self.pct_weight_combo.setCurrentIndex(1 if pw >= 700 else 0)
        
        self.debug_switch.setChecked(self.config.get("debug_mode", False))
        self.log_switch.setChecked(self.config.get("log_enabled", False))
        self.log_file_switch.setChecked(self.config.get("log_to_file", False))
        
        for w in widgets:
            try:
                w.blockSignals(False)
            except:
                pass
        
        self.update_color_btn()
        self.update_num_color_btn()
        self.update_pct_color_btn()
        self.update_hl_color_btn()
        
        self.rebuild_size_widgets()
        self._update_orient_visibility()
        self._update_anim_visibility()
        self._update_role_color_visibility()
        self._update_fill_dir_options()
    
    def on_size_changed(self, key, value):
        self.config[key] = value
        save_config(self.config)
        self.apply_overlay_config()
    
    def set_config(self, key, value):
        self.config[key] = value
        save_config(self.config)
        self.apply_overlay_config()
    
    def on_count_changed(self, index):
        self.config["character_count"] = index + 1
        save_config(self.config)
        self._update_role_color_visibility()
        self.apply_overlay_config()
        if self.main_window:
            self.main_window.home_page.config = self.config
            self.main_window.home_page.rebuild_cards()
    
    def on_role_color_enabled_changed(self, checked):
        self.set_config("role_color_enabled", checked)
    
    def on_role_color_changed(self, idx, color):
        key = f"role_color_{idx + 1}"
        self.config[key] = color
        save_config(self.config)
        self.apply_overlay_config()
    
    def on_style_changed(self, index):
        style_map = ["bar", "ring", "pie", "solid"]
        self.config["overlay_style"] = style_map[index]
        save_config(self.config)
        self.rebuild_size_widgets()
        self._update_orient_visibility()
        self._update_fill_dir_options()
        self.apply_overlay_config()
    
    def on_direction_changed(self, index):
        direction = "horizontal" if index == 0 else "vertical"
        self.config["overlay_direction"] = direction
        save_config(self.config)
        self.rebuild_size_widgets()
        self._update_fill_dir_options()
        self.apply_overlay_config()
    
    def on_bar_orient_changed(self, index):
        orient = "horizontal" if index == 0 else "vertical"
        self.config["bar_orientation"] = orient
        save_config(self.config)
        self._update_fill_dir_options()
        self.apply_overlay_config()
    
    def on_fill_dir_changed(self, index):
        options = getattr(self, '_fill_dir_options', ["from-bottom"])
        if index < len(options):
            self.set_config("fill_direction", options[index])
    
    def on_hide_anim_changed(self, index):
        anim = "fade" if index == 0 else "instant"
        self.config["hide_animation"] = anim
        save_config(self.config)
        self._update_anim_visibility()
        self.apply_overlay_config()
    
    def on_num_pos_changed(self, index):
        pos_map = ["center", "top", "bottom", "left", "right", "none"]
        self.set_config("number_position", pos_map[index])
    
    def on_pct_pos_changed(self, index):
        pos_map = ["center", "top", "bottom", "left", "right", "none"]
        self.set_config("percentage_position", pos_map[index])
    
    def on_num_weight_changed(self, index):
        weight = 700 if index == 1 else 400
        self.set_config("number_font_weight", weight)
    
    def on_pct_weight_changed(self, index):
        weight = 700 if index == 1 else 400
        self.set_config("percentage_font_weight", weight)
    
    def on_debug_changed(self, checked):
        self.set_config("debug_mode", checked)
        logger.configure(debug_mode=checked)
    
    def on_log_enabled_changed(self, checked):
        self.set_config("log_enabled", checked)
        logger.configure(log_enabled=checked)
        if self.main_window and hasattr(self.main_window, 'log_page'):
            self.main_window.log_page.sync_log_switch(checked)
    
    def sync_log_switch(self, checked):
        self.log_switch.setChecked(checked)
    
    def on_log_file_changed(self, checked):
        self.set_config("log_to_file", checked)
        logger.configure(log_to_file=checked)
    
    def on_theme_changed(self, checked):
        theme = "dark" if checked else "light"
        self.config["theme"] = theme
        save_config(self.config)
        setTheme(Theme.DARK if checked else Theme.LIGHT)
    
    def pick_border_color(self):
        color = QColorDialog.getColor(QColor(self.config.get("border_color", "#00C8FF")), self)
        if color.isValid():
            self.config["border_color"] = color.name()
            save_config(self.config)
            self.update_color_btn()
            self.apply_overlay_config()
    
    def update_color_btn(self):
        self.color_btn.setText(f"边框颜色 {self.config.get('border_color', '#00C8FF')}")
    
    def pick_number_color(self):
        color = QColorDialog.getColor(QColor(self.config.get("number_color", "#FFFFFF")), self)
        if color.isValid():
            self.config["number_color"] = color.name()
            save_config(self.config)
            self.update_num_color_btn()
            self.apply_overlay_config()
    
    def update_num_color_btn(self):
        self.num_color_btn.setText(f"序号颜色 {self.config.get('number_color', '#FFFFFF')}")
    
    def pick_percentage_color(self):
        color = QColorDialog.getColor(QColor(self.config.get("percentage_color", "#E6E6EB")), self)
        if color.isValid():
            self.config["percentage_color"] = color.name()
            save_config(self.config)
            self.update_pct_color_btn()
            self.apply_overlay_config()
    
    def update_pct_color_btn(self):
        self.pct_color_btn.setText(f"百分比颜色 {self.config.get('percentage_color', '#E6E6EB')}")
    
    def pick_highlight_color(self):
        color = QColorDialog.getColor(QColor(self.config.get("highlight_color", "#00FFFF")), self)
        if color.isValid():
            self.config["highlight_color"] = color.name()
            save_config(self.config)
            self.update_hl_color_btn()
            self.apply_overlay_config()
    
    def update_hl_color_btn(self):
        self.hl_color_btn.setText(f"高亮颜色 {self.config.get('highlight_color', '#00FFFF')}")
    
    def reset_position(self):
        self.config["horizontal_pos"] = {"x": None, "y": None}
        self.config["vertical_pos"] = {"x": None, "y": None}
        save_config(self.config)
        InfoBar.success(title="已重置位置", content="下次启动悬浮窗将使用默认位置",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=2000, parent=self)
    
    def reset_config(self):
        box = MessageBox("恢复默认设置", "确定要恢复所有设置为默认值吗？", self)
        if box.exec():
            save_config(DEFAULT_CONFIG)
            self.config = load_config()
            InfoBar.success(title="已重置", content="请重启软件以应用所有设置",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self)
    
    def export_config(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出配置", "config_backup.json", "JSON (*.json)")
        if path:
            try:
                shutil.copy("config.json", path)
                InfoBar.success(title="导出成功", content=path,
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=3000, parent=self)
            except Exception as e:
                InfoBar.error(title="导出失败", content=str(e),
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=3000, parent=self)
    
    def import_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入配置", "", "JSON (*.json)")
        if path:
            try:
                shutil.copy(path, "config.json")
                self.config = load_config()
                InfoBar.success(title="导入成功", content="请重启软件以应用所有设置",
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=3000, parent=self)
            except Exception as e:
                InfoBar.error(title="导入失败", content=str(e),
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=3000, parent=self)
    
    def apply_overlay_config(self):
        if self.main_window and self.main_window.home_page.overlay:
            self.main_window.home_page.overlay.apply_config(self.config)


# ============================================================
# 日志页
# ============================================================
class LogPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("log_page")
        self.config = load_config()
        self.main_window = parent
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        title = SubtitleLabel("日志", self)
        layout.addWidget(title)
        
        toolbar = QHBoxLayout()
        toolbar.addWidget(BodyLabel("启用日志记录", self))
        self.log_enabled_switch = SwitchButton(self)
        self.log_enabled_switch.setOnText("是")
        self.log_enabled_switch.setOffText("否")
        self.log_enabled_switch.setChecked(self.config.get("log_enabled", False))
        self.log_enabled_switch.checkedChanged.connect(self.on_log_enabled_changed)
        toolbar.addWidget(self.log_enabled_switch)
        toolbar.addSpacing(20)
        clear_btn = PushButton("清空日志", self)
        clear_btn.clicked.connect(self.clear_logs)
        toolbar.addWidget(clear_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self.text_edit = TextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 9))
        layout.addWidget(self.text_edit)
        
        logger.add_listener(self.refresh)
        self.refresh()
    
    def on_log_enabled_changed(self, checked):
        self.config["log_enabled"] = checked
        save_config(self.config)
        logger.configure(log_enabled=checked)
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.settings_page.sync_log_switch(checked)
    
    def sync_log_switch(self, checked):
        self.log_enabled_switch.setChecked(checked)
    
    def refresh(self):
        logs = logger.get_logs()
        self.text_edit.setPlainText("\n".join(logs))
        self.text_edit.verticalScrollBar().setValue(
            self.text_edit.verticalScrollBar().maximum())
    
    def clear_logs(self):
        logger.clear()


# ============================================================
# 关于页
# ============================================================
class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("about_page")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        title = SubtitleLabel("关于", self)
        layout.addWidget(title)
        
        layout.addWidget(StrongBodyLabel(f"终末地连携监测 v{VERSION}", self))
        
        desc = BodyLabel(
            "一个基于屏幕识别的连携监测工具。\n"
            "不修改游戏文件、不读取游戏内存。\n"
            "仅供个人学习使用，所有代码来源DeepSeek。", self
        )
        layout.addWidget(desc)
        
        # GitHub 仓库
        repo_url = "https://github.com/YuumiSama/EndfieldHUD"
        repo_card = CardWidget(self)
        repo_layout = QHBoxLayout(repo_card)
        repo_layout.setContentsMargins(20, 15, 20, 15)
        
        repo_icon = BodyLabel(self)
        repo_icon.setPixmap(FluentIcon.GITHUB.icon().pixmap(32, 32))
        repo_layout.addWidget(repo_icon)
        
        repo_text_layout = QVBoxLayout()
        repo_text_layout.addWidget(StrongBodyLabel("GitHub 仓库", repo_card))
        repo_text_layout.addWidget(BodyLabel(repo_url, repo_card))
        repo_layout.addLayout(repo_text_layout, 1)
        
        repo_btn = PushButton("打开", repo_card)
        repo_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(repo_url)))
        repo_layout.addWidget(repo_btn)
        
        layout.addWidget(repo_card)
        
        # 更新页面
        update_url = "https://github.com/YuumiSama/EndfieldHUD/releases"
        update_card = CardWidget(self)
        update_layout = QHBoxLayout(update_card)
        update_layout.setContentsMargins(20, 15, 20, 15)
        
        update_icon = BodyLabel(self)
        update_icon.setPixmap(FluentIcon.UPDATE.icon().pixmap(32, 32))
        update_layout.addWidget(update_icon)
        
        update_text_layout = QVBoxLayout()
        update_text_layout.addWidget(StrongBodyLabel("更新页面", update_card))
        update_text_layout.addWidget(BodyLabel(update_url, update_card))
        update_layout.addLayout(update_text_layout, 1)
        
        update_btn = PushButton("打开", update_card)
        update_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(update_url)))
        update_layout.addWidget(update_btn)
        
        layout.addWidget(update_card)
        
        # 哔哩哔哩
        bilibili_url = "https://space.bilibili.com/89139193"
        bilibili_card = CardWidget(self)
        bilibili_layout = QHBoxLayout(bilibili_card)
        bilibili_layout.setContentsMargins(20, 15, 20, 15)
        
        bilibili_icon = BodyLabel(self)
        bilibili_icon.setPixmap(FluentIcon.LINK.icon().pixmap(32, 32))
        bilibili_layout.addWidget(bilibili_icon)
        
        bilibili_text_layout = QVBoxLayout()
        bilibili_text_layout.addWidget(StrongBodyLabel("哔哩哔哩", bilibili_card))
        bilibili_text_layout.addWidget(BodyLabel(bilibili_url, bilibili_card))
        bilibili_layout.addLayout(bilibili_text_layout, 1)
        
        bilibili_btn = PushButton("打开", bilibili_card)
        bilibili_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(bilibili_url)))
        bilibili_layout.addWidget(bilibili_btn)
        
        layout.addWidget(bilibili_card)
        
        layout.addStretch()

# ============================================================
# 主窗口
# ============================================================
class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"终末地连携监测 v{VERSION}")
        self.resize(1280, 720)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        icon_path = resource_path("assets/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.config = load_config()
        if self.config.get("theme", "dark") == "dark":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)
        logger.configure(
            log_to_file=self.config.get("log_to_file", False),
            log_max_lines=self.config.get("log_max_lines", 500),
            log_file_max_lines=self.config.get("log_file_max_lines", 1000),
            debug_mode=self.config.get("debug_mode", False),
            log_enabled=self.config.get("log_enabled", False)
        )
        logger.info(f"软件启动 v{VERSION}")
        
        self.home_page = HomePage(self)
        self.settings_page = SettingsPage(self)
        self.log_page = LogPage(self)
        self.about_page = AboutPage(self)
        
        self.home_page.settings_page_ref = self.settings_page
        
        self.addSubInterface(self.home_page, FluentIcon.HOME, "主页")
        self.addSubInterface(self.settings_page, FluentIcon.SETTING, "设置")
        self.addSubInterface(self.log_page, FluentIcon.HISTORY, "日志")
        self.addSubInterface(self.about_page, FluentIcon.INFO, "关于", NavigationItemPosition.BOTTOM)
        
        self.stackedWidget.currentChanged.connect(self.on_page_changed)
        
        for attr in ['slideAni', 'ani', 'animation']:
            if hasattr(self.navigationInterface, attr):
                a = getattr(self.navigationInterface, attr)
                if a and hasattr(a, 'setDuration'):
                    a.setDuration(80)
        for child in self.navigationInterface.findChildren(QPropertyAnimation):
            child.setDuration(80)
        self._create_tray()
    
    def on_page_changed(self, index):
        current_widget = self.stackedWidget.widget(index)
        if current_widget == self.settings_page:
            self.settings_page.reload_from_config()
    
    def _create_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = resource_path("assets/icon.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip(f"终末地连携监测 v{VERSION}")
        menu = QMenu()
        a1 = QAction("显示主界面", self)
        a1.triggered.connect(self.show_window)
        menu.addAction(a1)
        menu.addSeparator()
        a2 = QAction("启动悬浮窗", self)
        a2.triggered.connect(self.home_page.start_overlay)
        menu.addAction(a2)
        a3 = QAction("停止悬浮窗", self)
        a3.triggered.connect(self.home_page.stop_overlay)
        menu.addAction(a3)
        menu.addSeparator()
        a4 = QAction("退出", self)
        a4.triggered.connect(self.quit_app)
        menu.addAction(a4)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
    
    def show_window(self):
        self.show()
        self.activateWindow()
    
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()
    
    def quit_app(self):
        logger.info("软件退出")
        if self.home_page.overlay:
            self.home_page.overlay.stop()
        QApplication.quit()
    
    def closeEvent(self, event):
        config = load_config()
        
        if not config.get("close_choice_made", False):
            from qfluentwidgets import (
                MessageBoxBase, SubtitleLabel, RadioButton,
                CheckBox, BodyLabel
            )
            
            class CloseDialog(MessageBoxBase):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.titleLabel = SubtitleLabel("关闭窗口", self)
                    self.viewLayout.addWidget(self.titleLabel)
                    
                    self.viewLayout.addWidget(BodyLabel("关闭窗口时，你希望：", self))
                    
                    self.rb_tray = RadioButton("最小化到托盘", self)
                    self.rb_tray.setChecked(True)
                    self.rb_exit = RadioButton("直接退出", self)
                    self.viewLayout.addWidget(self.rb_tray)
                    self.viewLayout.addWidget(self.rb_exit)
                    
                    self.cb_remember = CheckBox("记住我的选择（下次不再提示）", self)
                    self.cb_remember.setChecked(False)
                    self.viewLayout.addWidget(self.cb_remember)
                    
                    self.yesButton.setText("确定")
                    self.cancelButton.setText("取消")
                    
                    self.widget.setMinimumWidth(420)
            
            dialog = CloseDialog(self)
            if not dialog.exec():
                event.ignore()
                return
            
            choose_tray = dialog.rb_tray.isChecked()
            remember = dialog.cb_remember.isChecked()
            
            config["close_to_tray"] = choose_tray
            if remember:
                config["close_choice_made"] = True
            save_config(config)
            
            if choose_tray:
                event.ignore()
                self.hide()
                self.tray_icon.showMessage(
                    "终末地连携监测",
                    "软件已最小化到托盘，双击托盘图标可重新打开。",
                    QSystemTrayIcon.Information,
                    2000
                )
            else:
                event.accept()
                self.quit_app()
            return
        
        if config.get("close_to_tray", True):
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "终末地连携监测",
                "软件已最小化到托盘，双击托盘图标可重新打开。",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            event.accept()
            self.quit_app()


if __name__ == "__main__":
    _config = load_config()
    if _config.get("theme", "dark") == "dark":
        setTheme(Theme.DARK)
    else:
        setTheme(Theme.LIGHT)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())