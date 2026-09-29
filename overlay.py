import mss
import numpy as np
import keyboard
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import QTimer, Qt, QPoint, QRectF, QPropertyAnimation
from capture import capture_all, find_game_window, is_game_foreground, get_actual_areas
from logger import logger
from config import save_config


BG_AUTO_CORNER = 8


class Overlay(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.percentages = [0.0] * config.get("character_count", 4)
        self.available = [True] * config.get("character_count", 4)
        self.running = False
        self.paused = False
        self._sampling_counter = 0
        self._ui_check_counter = 0
        self._game_missing_logged = False
        self._hidden_by_auto = False
        self._hidden_by_no_bar = False
        self._no_bar_counter = 0
        self._last_pos = None
        self._fade_anim = None
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        self.dragging = False
        self.drag_position = QPoint()
        self.ctrl_pressed = False
        
        # 首次启动时，清空 _last_pos 和窗口尺寸，强制走默认位置
        self._last_pos = None
        # 临时设置窗口尺寸为 0，让 apply_config 走 else 分支
        self._first_apply = True
        self.apply_config(config)
        self._first_apply = False
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)
        
        self.key_timer = QTimer()
        self.key_timer.timeout.connect(self.check_ctrl)
        self.key_timer.start(50)
    
    # ==================== 显示/隐藏 ====================
    def _set_visible(self, visible):
        if visible:
            opacity = self.config.get("overlay_opacity", 80) / 100.0
            self.setWindowOpacity(opacity)
        else:
            self.setWindowOpacity(0.0)
    
    def _fade_in(self):
        duration = self.config.get("fade_duration", 300)
        target = self.config.get("overlay_opacity", 80) / 100.0
        self._fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self._fade_anim.setDuration(duration)
        self._fade_anim.setStartValue(self.windowOpacity())
        self._fade_anim.setEndValue(target)
        self._fade_anim.start()
    
    def _fade_out(self):
        duration = self.config.get("fade_duration", 300)
        self._fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self._fade_anim.setDuration(duration)
        self._fade_anim.setStartValue(self.windowOpacity())
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.start()
    
    def _show_with_animation(self):
        if self.config.get("hide_animation", "fade") == "fade":
            self._fade_in()
        else:
            opacity = self.config.get("overlay_opacity", 80) / 100.0
            self.setWindowOpacity(opacity)
    
    def _hide_with_animation(self):
        if self.config.get("hide_animation", "fade") == "fade":
            self._fade_out()
        else:
            self.setWindowOpacity(0.0)
    
    # ==================== UI 检测 ====================
    def _check_all_ui(self):
        from capture import check_ui_available
        return check_ui_available(self.config)
    
    # ==================== 尺寸参数 ====================
    def _get_bar_params(self, config):
        direction = config.get("overlay_direction", "vertical")
        if direction == "horizontal":
            return {
                "length": config.get("size_h_bar_length", 200),
                "thickness": config.get("size_h_bar_thickness", 10),
                "gap": config.get("size_h_bar_gap", 8),
            }
        else:
            return {
                "length": config.get("size_v_bar_length", 200),
                "thickness": config.get("size_v_bar_thickness", 10),
                "gap": config.get("size_v_bar_gap", 8),
            }
    
    def _get_circle_params(self, config):
        direction = config.get("overlay_direction", "vertical")
        if direction == "horizontal":
            return {
                "diameter": config.get("size_h_circle_diameter", 60),
                "thickness": config.get("size_h_circle_thickness", 6),
                "gap": config.get("size_h_circle_gap", 8),
            }
        else:
            return {
                "diameter": config.get("size_v_circle_diameter", 60),
                "thickness": config.get("size_v_circle_thickness", 6),
                "gap": config.get("size_v_circle_gap", 8),
            }
    
    # ==================== 窗口大小 ====================
    def _calc_window_size(self, config):
        count = config.get("character_count", 4)
        margin = config.get("window_margin", 35)
        style = config.get("overlay_style", "bar")
        direction = config.get("overlay_direction", "vertical")
        bar_orient = config.get("bar_orientation", "horizontal")
        
        if style == "bar":
            p = self._get_bar_params(config)
            length = p["length"]
            thickness = p["thickness"]
            gap = p["gap"]
            
            if direction == "horizontal":
                if bar_orient == "horizontal":
                    w = margin * 2 + length * count + gap * (count - 1)
                    h = margin * 2 + thickness + 40
                else:
                    w = margin * 2 + thickness * count + gap * (count - 1)
                    h = margin * 2 + length + 40
            else:
                if bar_orient == "horizontal":
                    w = margin * 2 + length + 120
                    h = margin * 2 + thickness * count + gap * (count - 1)
                else:
                    w = margin * 2 + thickness + 120
                    h = margin * 2 + length * count + gap * (count - 1)
        else:
            p = self._get_circle_params(config)
            d = p["diameter"]
            gap = p["gap"]
            if direction == "horizontal":
                w = margin * 2 + d * count + gap * (count - 1)
                h = margin * 2 + d + 40
            else:
                w = margin * 2 + d + 120
                h = margin * 2 + d * count + gap * (count - 1)
        
        return max(50, int(w)), max(30, int(h))
    
    # ==================== 配置应用 ====================
    def apply_config(self, config):
        self.config = config
        count = config.get("character_count", 4)
        
        if len(self.percentages) < count:
            self.percentages.extend([0.0] * (count - len(self.percentages)))
        self.percentages = self.percentages[:count]
        
        if len(self.available) < count:
            self.available.extend([True] * (count - len(self.available)))
        self.available = self.available[:count]
        
        if not self._hidden_by_auto and not self._hidden_by_no_bar:
            opacity = config.get("overlay_opacity", 80) / 100.0
            self.setWindowOpacity(opacity)
        
        old_pos = self.pos()
        old_w, old_h = self.width(), self.height()
        
        # 首次应用时，强制 old_w/old_h 为 0
        if getattr(self, '_first_apply', False):
            old_w = 0
            old_h = 0
        
        w, h = self._calc_window_size(config)
        
        # 计算新位置（保持底部中心不变）
        if old_w > 0 and old_h > 0:
            old_center_x = old_pos.x() + old_w // 2
            old_bottom = old_pos.y() + old_h
            new_x = old_center_x - w // 2
            new_y = old_bottom - h
            screen = QApplication.primaryScreen().geometry()
            new_x = max(0, min(new_x, screen.width() - w))
            new_y = max(0, min(new_y, screen.height() - h))
            self._last_pos = QPoint(new_x, new_y)
        
        self.resize(w, h)
        
        if self._last_pos is not None:
            self.move(self._last_pos)
        else:
            direction = config.get("overlay_direction", "vertical")
            pos_key = "horizontal_pos" if direction == "horizontal" else "vertical_pos"
            pos = config.get(pos_key, {"x": None, "y": None})
            if pos.get("x") is not None and pos.get("y") is not None:
                self._apply_saved_position(pos)
                self._last_pos = self.pos()
            else:
                screen = QApplication.primaryScreen().geometry()
                x = (screen.width() - w) // 2
                y = int(screen.height() * 0.82)
                # 防止超出屏幕底部
                if y + h > screen.height():
                    y = screen.height() - h
                self.move(x, y)
                self._last_pos = self.pos()
        
        self.update()
    
    def _apply_saved_position(self, pos):
        x = pos.get("x")
        y = pos.get("y")
        if x is None or y is None:
            return
        screen = QApplication.primaryScreen().geometry()
        w, h = self.width(), self.height()
        x = max(0, min(x, screen.width() - w))
        y = max(0, min(y, screen.height() - h))
        self.move(x, y)
    
    def _save_current_position(self):
        pos = self.pos()
        self._last_pos = pos
        direction = self.config.get("overlay_direction", "vertical")
        pos_key = "horizontal_pos" if direction == "horizontal" else "vertical_pos"
        self.config[pos_key] = {"x": pos.x(), "y": pos.y()}
        save_config(self.config)
    
    def start(self):
        self.running = True
        direction = self.config.get("overlay_direction", "vertical")
        pos_key = "horizontal_pos" if direction == "horizontal" else "vertical_pos"
        pos = self.config.get(pos_key, {"x": None, "y": None})
        if pos.get("x") is not None and pos.get("y") is not None:
            self._apply_saved_position(pos)
        self._last_pos = self.pos()
        self._hidden_by_auto = False
        self._hidden_by_no_bar = False
        self._no_bar_counter = 0
        self._ui_check_counter = 0
        
        self.available = self._check_all_ui()
        any_ui = any(self.available)
        if any_ui:
            self.percentages = capture_all(self.config)
        else:
            self.percentages = [0.0] * len(self.percentages)
        
        self.show()
        if self.config.get("auto_hide_no_bar", False) and not any_ui:
            self._set_visible(False)
            self._hidden_by_no_bar = True
        else:
            self._set_visible(True)
        
        logger.info("悬浮窗已启动")
    
    def stop(self):
        self.running = False
        self._save_current_position()
        self.hide()
        logger.info("悬浮窗已停止")
    
    def pause(self):
        """暂停：冻结数值，不再刷新"""
        self.paused = True
        logger.info("悬浮窗已暂停")
    
    def resume(self):
        """恢复：重新开始刷新"""
        self.paused = False
        logger.info("悬浮窗已恢复")
    
    def check_ctrl(self):
        is_pressed = keyboard.is_pressed('ctrl')
        if is_pressed and not self.ctrl_pressed:
            self.ctrl_pressed = True
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.setCursor(Qt.OpenHandCursor)
        elif not is_pressed and self.ctrl_pressed:
            self.ctrl_pressed = False
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.setCursor(Qt.ArrowCursor)
            if self.dragging:
                self.dragging = False
                self._save_current_position()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.ctrl_pressed:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)
    
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.OpenHandCursor)
            self._save_current_position()
    
    def update_data(self):
        if not self.running:
            return
        
        # 暂停：只重绘，不更新数据
        if self.paused:
            self.update()
            return
        
        hwnd = find_game_window()
        is_fg = is_game_foreground()
        
        if self.config.get("auto_hide_when_no_game", False):
            if hwnd is None or not is_fg:
                if not self._hidden_by_auto:
                    self._save_current_position()
                    self._hide_with_animation()
                    self._hidden_by_auto = True
                return
            else:
                if self._hidden_by_auto:
                    self._show_with_animation()
                    self._hidden_by_auto = False
        else:
            if self._hidden_by_auto:
                self._show_with_animation()
                self._hidden_by_auto = False
        
        self._ui_check_counter += 1
        if self._ui_check_counter >= 5:
            self._ui_check_counter = 0
            self.available = self._check_all_ui()
        
        any_ui = any(self.available)
        
        if self.config.get("auto_hide_no_bar", False):
            if any_ui:
                self._no_bar_counter = 0
                if self._hidden_by_no_bar:
                    self._show_with_animation()
                    self._hidden_by_no_bar = False
            else:
                self._no_bar_counter += 1
                if self._no_bar_counter >= 5 and not self._hidden_by_no_bar:
                    self._save_current_position()
                    self._hide_with_animation()
                    self._hidden_by_no_bar = True
        else:
            if self._hidden_by_no_bar:
                self._show_with_animation()
                self._hidden_by_no_bar = False
        
        if hwnd is None:
            if not self._game_missing_logged:
                logger.warning("未找到游戏窗口，请确保游戏已启动")
                self._game_missing_logged = True
        else:
            self._game_missing_logged = False
        
        if any_ui:
            self.percentages = capture_all(self.config)
        else:
            self.percentages = [0.0] * len(self.percentages)
        
        if self.config.get("debug_mode", False):
            self._sampling_counter += 1
            if self._sampling_counter >= 50:
                self._sampling_counter = 0
                p = [int(x) for x in self.percentages]
                logger.debug(f"识别采样: {p}")
        
        self.update()
    
    def get_fill_color(self, percentage, role_index=0):
        """获取填充色。如果启用了角色独立颜色，用角色颜色"""
        if self.config.get("role_color_enabled", False):
            color_key = f"role_color_{role_index + 1}"
            color_str = self.config.get(color_key, "#FFFFFF")
            return QColor(color_str)
        return QColor(230, 230, 235, 230)
    
    def _effective_fill_direction(self):
        style = self.config.get("overlay_style", "bar")
        fill_dir = self.config.get("fill_direction", "from-bottom")
        if fill_dir:
            return fill_dir
        if style in ("ring", "pie"):
            return "clockwise"
        if style == "bar":
            bar_orient = self.config.get("bar_orientation", "horizontal")
            return "from-left" if bar_orient == "horizontal" else "from-bottom"
        if style == "solid":
            return "from-bottom"
        return "from-bottom"
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bg_alpha = self.config.get("bg_opacity", 0)
        bg_corner = self._get_bg_corner()
        border_enabled = self.config.get("border_enabled", False)
        border_color = QColor(self.config.get("border_color", "#00C8FF"))
        border_width = self.config.get("border_width", 2)
        
        if bg_alpha > 0:
            painter.setBrush(QBrush(QColor(20, 20, 25, bg_alpha)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(0, 0, self.width(), self.height(), bg_corner, bg_corner)
        
        if border_enabled or self.ctrl_pressed:
            if self.ctrl_pressed:
                pen = QPen(QColor(0, 200, 255, 200), 2, Qt.DashLine)
            else:
                pen = QPen(border_color, border_width)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                border_width // 2, border_width // 2,
                self.width() - border_width, self.height() - border_width,
                bg_corner, bg_corner
            )
        
        style = self.config.get("overlay_style", "bar")
        direction = self.config.get("overlay_direction", "vertical")
        
        if style == "bar":
            bar_orient = self.config.get("bar_orientation", "horizontal")
            if direction == "horizontal" and bar_orient == "horizontal":
                self._paint_h_h(painter)
            elif direction == "horizontal" and bar_orient == "vertical":
                self._paint_h_v(painter)
            elif direction == "vertical" and bar_orient == "horizontal":
                self._paint_v_h(painter)
            else:
                self._paint_v_v(painter)
        else:
            if direction == "horizontal":
                self._paint_circle_horizontal(painter, style)
            else:
                self._paint_circle_vertical(painter, style)
    
    def _get_bg_corner(self):
        val = self.config.get("bg_corner_radius", 0)
        if val <= 0:
            return BG_AUTO_CORNER
        return val
    
    def _get_bar_corner(self, thickness):
        val = self.config.get("bar_corner_radius", 0)
        if val <= 0:
            return thickness // 2
        return min(val, thickness // 2)
    
    # ==================== 文字 ====================
    def _draw_number(self, painter, rect, num, unavailable=False):
        if not self.config.get("number_visible", True):
            return
        if self.config.get("number_position", "left") == "none":
            return
        font_size = self.config.get("number_font_size", 9)
        weight = self.config.get("number_font_weight", 700)
        color = QColor(self.config.get("number_color", "#FFFFFF"))
        if unavailable:
            color.setAlpha(80)
        painter.setPen(QPen(color))
        font = QFont("Microsoft YaHei", font_size)
        font.setWeight(weight)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, str(num))
    
    def _draw_percentage(self, painter, rect, pct, unavailable=False):
        if not self.config.get("percentage_visible", True):
            return
        if self.config.get("percentage_position", "right") == "none":
            return
        font_size = self.config.get("percentage_font_size", 8)
        weight = self.config.get("percentage_font_weight", 400)
        color = QColor(self.config.get("percentage_color", "#E6E6EB"))
        if unavailable:
            color.setAlpha(80)
        painter.setPen(QPen(color))
        font = QFont("Microsoft YaHei", font_size)
        font.setWeight(weight)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{int(pct)}%")
    
    def _draw_number_percent(self, painter, area_rect, num, pct, unavailable=False):
        num_pos = self.config.get("number_position", "left")
        pct_pos = self.config.get("percentage_position", "right")
        num_offset = self.config.get("number_offset", 5)
        pct_offset = self.config.get("percentage_offset", 5)
        
        x, y, w, h = area_rect.x(), area_rect.y(), area_rect.width(), area_rect.height()
        
        if num_pos != "none" and self.config.get("number_visible", True):
            if num_pos == "center":
                r = QRectF(x, y, w, h)
            elif num_pos == "top":
                r = QRectF(x, y - num_offset - 16, w, 16)
            elif num_pos == "bottom":
                r = QRectF(x, y + h + num_offset, w, 16)
            elif num_pos == "left":
                r = QRectF(x - num_offset - 30, y, 30, h)
            elif num_pos == "right":
                r = QRectF(x + w + num_offset, y, 30, h)
            else:
                r = None
            if r:
                self._draw_number(painter, r, num, unavailable)
        
        if pct_pos != "none" and self.config.get("percentage_visible", True):
            if pct_pos == "center":
                r = QRectF(x, y, w, h)
            elif pct_pos == "top":
                r = QRectF(x, y - pct_offset - 16, w, 16)
            elif pct_pos == "bottom":
                r = QRectF(x, y + h + pct_offset, w, 16)
            elif pct_pos == "left":
                r = QRectF(x - pct_offset - 40, y, 40, h)
            elif pct_pos == "right":
                r = QRectF(x + w + pct_offset, y, 40, h)
            else:
                r = None
            if r:
                self._draw_percentage(painter, r, pct, unavailable)
    
    # ==================== 高亮 ====================
    def _draw_highlight(self, painter, x, y, w, h, corner, pct):
        if not self.config.get("highlight_enabled", True):
            return
        threshold = self.config.get("highlight_threshold", 50)
        if pct < threshold:
            return
        
        color = QColor(self.config.get("highlight_color", "#00FFFF"))
        base_width = self.config.get("highlight_width", 2)
        layers = self.config.get("highlight_layers", 2)
        
        for i in range(layers):
            alpha = int(200 * (1 - i / max(layers, 1)) + 50)
            c = QColor(color)
            c.setAlpha(alpha)
            pen = QPen(c, base_width + i * 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            offset = base_width // 2 + i
            painter.drawRoundedRect(
                int(x - offset), int(y - offset),
                int(w + offset * 2), int(h + offset * 2),
                corner + offset, corner + offset
            )
    
    # ==================== 4 种条绘制 ====================
    def _paint_h_h(self, painter):
        count = len(self.percentages)
        p = self._get_bar_params(self.config)
        margin = self.config.get("window_margin", 35)
        length = p["length"]
        thickness = p["thickness"]
        gap = p["gap"]
        corner = self._get_bar_corner(thickness)
        y = (self.height() - thickness) // 2
        unavail_opacity = self.config.get("unavailable_opacity", 30) / 100.0
        fill_dir = self._effective_fill_direction()
        
        for i, pct in enumerate(self.percentages):
            x = margin + i * (length + gap)
            rect = QRectF(x, y, length, thickness)
            avail = self.available[i] if i < len(self.available) else True
            alpha = 1.0 if avail else unavail_opacity
            
            painter.setBrush(QBrush(QColor(30, 30, 35, int(200 * alpha))))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x), int(y), int(length), thickness, corner, corner)
            fill = int(length * (pct / 100.0))
            if fill > 0:
                c = self.get_fill_color(pct, i)
                c.setAlpha(int(230 * alpha))
                painter.setBrush(QBrush(c))
                if fill_dir == "from-right":
                    painter.drawRoundedRect(int(x) + int(length) - fill, int(y), fill, thickness, corner, corner)
                else:
                    painter.drawRoundedRect(int(x), int(y), fill, thickness, corner, corner)
            self._draw_number_percent(painter, rect, i + 1, pct, not avail)
            if avail:
                self._draw_highlight(painter, x, y, length, thickness, corner, pct)
    
    def _paint_h_v(self, painter):
        count = len(self.percentages)
        p = self._get_bar_params(self.config)
        margin = self.config.get("window_margin", 35)
        length = p["length"]
        thickness = p["thickness"]
        gap = p["gap"]
        corner = self._get_bar_corner(thickness)
        y = (self.height() - length) // 2
        unavail_opacity = self.config.get("unavailable_opacity", 30) / 100.0
        fill_dir = self._effective_fill_direction()
        
        for i, pct in enumerate(self.percentages):
            x = margin + i * (thickness + gap)
            rect = QRectF(x, y, thickness, length)
            avail = self.available[i] if i < len(self.available) else True
            alpha = 1.0 if avail else unavail_opacity
            
            painter.setBrush(QBrush(QColor(30, 30, 35, int(200 * alpha))))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x), int(y), thickness, int(length), corner, corner)
            fill = int(length * (pct / 100.0))
            if fill > 0:
                c = self.get_fill_color(pct, i)
                c.setAlpha(int(230 * alpha))
                painter.setBrush(QBrush(c))
                if fill_dir == "from-top":
                    painter.drawRoundedRect(int(x), int(y), thickness, fill, corner, corner)
                else:
                    painter.drawRoundedRect(int(x), int(y) + int(length) - fill, thickness, fill, corner, corner)
            self._draw_number_percent(painter, rect, i + 1, pct, not avail)
            if avail:
                self._draw_highlight(painter, x, y, thickness, length, corner, pct)
    
    def _paint_v_h(self, painter):
        count = len(self.percentages)
        p = self._get_bar_params(self.config)
        margin = self.config.get("window_margin", 35)
        length = p["length"]
        thickness = p["thickness"]
        gap = p["gap"]
        corner = self._get_bar_corner(thickness)
        x = (self.width() - length) // 2
        unavail_opacity = self.config.get("unavailable_opacity", 30) / 100.0
        fill_dir = self._effective_fill_direction()
        
        for i, pct in enumerate(self.percentages):
            y = margin + i * (thickness + gap)
            rect = QRectF(x, y, length, thickness)
            avail = self.available[i] if i < len(self.available) else True
            alpha = 1.0 if avail else unavail_opacity
            
            painter.setBrush(QBrush(QColor(30, 30, 35, int(200 * alpha))))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x), int(y), int(length), thickness, corner, corner)
            fill = int(length * (pct / 100.0))
            if fill > 0:
                c = self.get_fill_color(pct, i)
                c.setAlpha(int(230 * alpha))
                painter.setBrush(QBrush(c))
                if fill_dir == "from-right":
                    painter.drawRoundedRect(int(x) + int(length) - fill, int(y), fill, thickness, corner, corner)
                else:
                    painter.drawRoundedRect(int(x), int(y), fill, thickness, corner, corner)
            self._draw_number_percent(painter, rect, i + 1, pct, not avail)
            if avail:
                self._draw_highlight(painter, x, y, length, thickness, corner, pct)
    
    def _paint_v_v(self, painter):
        count = len(self.percentages)
        p = self._get_bar_params(self.config)
        margin = self.config.get("window_margin", 35)
        length = p["length"]
        thickness = p["thickness"]
        gap = p["gap"]
        corner = self._get_bar_corner(thickness)
        x = (self.width() - thickness) // 2
        unavail_opacity = self.config.get("unavailable_opacity", 30) / 100.0
        fill_dir = self._effective_fill_direction()
        
        for i, pct in enumerate(self.percentages):
            y = margin + i * (length + gap)
            rect = QRectF(x, y, thickness, length)
            avail = self.available[i] if i < len(self.available) else True
            alpha = 1.0 if avail else unavail_opacity
            
            painter.setBrush(QBrush(QColor(30, 30, 35, int(200 * alpha))))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x), int(y), thickness, int(length), corner, corner)
            fill = int(length * (pct / 100.0))
            if fill > 0:
                c = self.get_fill_color(pct, i)
                c.setAlpha(int(230 * alpha))
                painter.setBrush(QBrush(c))
                if fill_dir == "from-top":
                    painter.drawRoundedRect(int(x), int(y), thickness, fill, corner, corner)
                else:
                    painter.drawRoundedRect(int(x), int(y) + int(length) - fill, thickness, fill, corner, corner)
            self._draw_number_percent(painter, rect, i + 1, pct, not avail)
            if avail:
                self._draw_highlight(painter, x, y, thickness, length, corner, pct)
    
    # ==================== 圆环 / 饼图 / 实心圆 ====================
    def _paint_circle_horizontal(self, painter, style):
        count = len(self.percentages)
        p = self._get_circle_params(self.config)
        margin = self.config.get("window_margin", 35)
        d = p["diameter"]
        gap = p["gap"]
        y = (self.height() - d) // 2
        unavail_opacity = self.config.get("unavailable_opacity", 30) / 100.0
        
        for i, pct in enumerate(self.percentages):
            x = margin + i * (d + gap)
            circle_rect = QRectF(x, y, d, d)
            avail = self.available[i] if i < len(self.available) else True
            alpha = 1.0 if avail else unavail_opacity
            
            if style == "ring":
                self._draw_ring(painter, circle_rect, pct, p["thickness"], alpha, i)
            elif style == "pie":
                self._draw_pie(painter, circle_rect, pct, alpha, i)
            else:
                self._draw_solid(painter, circle_rect, pct, alpha, i)
            self._draw_number_percent(painter, circle_rect, i + 1, pct, not avail)
            if avail:
                self._draw_highlight(painter, x, y, d, d, d // 2, pct)
    
    def _paint_circle_vertical(self, painter, style):
        count = len(self.percentages)
        p = self._get_circle_params(self.config)
        margin = self.config.get("window_margin", 35)
        d = p["diameter"]
        gap = p["gap"]
        x = (self.width() - d) // 2
        unavail_opacity = self.config.get("unavailable_opacity", 30) / 100.0
        
        for i, pct in enumerate(self.percentages):
            y = margin + i * (d + gap)
            circle_rect = QRectF(x, y, d, d)
            avail = self.available[i] if i < len(self.available) else True
            alpha = 1.0 if avail else unavail_opacity
            
            if style == "ring":
                self._draw_ring(painter, circle_rect, pct, p["thickness"], alpha, i)
            elif style == "pie":
                self._draw_pie(painter, circle_rect, pct, alpha, i)
            else:
                self._draw_solid(painter, circle_rect, pct, alpha, i)
            self._draw_number_percent(painter, circle_rect, i + 1, pct, not avail)
            if avail:
                self._draw_highlight(painter, x, y, d, d, d // 2, pct)
    
    def _draw_ring(self, painter, rect, pct, thickness, alpha=1.0, role_idx=0):
        bg = QColor(30, 30, 35, int(200 * alpha))
        pen_bg = QPen(bg, thickness)
        pen_bg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(rect, 0, 360 * 16)
        c = self.get_fill_color(pct, role_idx)
        c.setAlpha(int(230 * alpha))
        pen_fg = QPen(c, thickness)
        pen_fg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_fg)
        span = -int(360 * 16 * (pct / 100.0))
        fill_dir = self._effective_fill_direction()
        if fill_dir == "counterclockwise":
            painter.drawArc(rect, 90 * 16, -span)
        else:
            painter.drawArc(rect, 90 * 16, span)
    
    def _draw_pie(self, painter, rect, pct, alpha=1.0, role_idx=0):
        bg = QColor(30, 30, 35, int(200 * alpha))
        painter.setBrush(QBrush(bg))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)
        c = self.get_fill_color(pct, role_idx)
        c.setAlpha(int(230 * alpha))
        painter.setBrush(QBrush(c))
        span = -int(360 * 16 * (pct / 100.0))
        fill_dir = self._effective_fill_direction()
        if fill_dir == "counterclockwise":
            painter.drawPie(rect, 90 * 16, -span)
        else:
            painter.drawPie(rect, 90 * 16, span)
    
    def _draw_solid(self, painter, rect, pct, alpha=1.0, role_idx=0):
        bg = QColor(30, 30, 35, int(200 * alpha))
        painter.setBrush(QBrush(bg))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)
        
        if pct <= 0:
            return
        
        c = self.get_fill_color(pct, role_idx)
        c.setAlpha(int(230 * alpha))
        painter.setBrush(QBrush(c))
        
        painter.save()
        from PyQt5.QtGui import QRegion
        from PyQt5.QtCore import QRect
        clip_region = QRegion(
            QRect(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height())),
            QRegion.Ellipse
        )
        painter.setClipRegion(clip_region)
        
        fill_dir = self._effective_fill_direction()
        fill_height = rect.height() * (pct / 100.0)
        if fill_dir == "from-top":
            fill_rect = QRectF(rect.x(), rect.y(), rect.width(), fill_height)
        else:
            fill_rect = QRectF(rect.x(), rect.y() + rect.height() - fill_height,
                               rect.width(), fill_height)
        painter.drawRect(fill_rect)
        painter.restore()