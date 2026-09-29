import sys
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, NavigationItemPosition, SubtitleLabel

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("终末地状态监测")
        self.resize(900, 600)
        
        # 创建页面
        self.home_page = SubtitleLabel("主页内容", self)
        self.settings_page = SubtitleLabel("设置内容", self)
        self.about_page = SubtitleLabel("关于内容", self)
        
        # 给每个页面设置唯一的 objectName（必须！）
        self.home_page.setObjectName("home_page")
        self.settings_page.setObjectName("settings_page")
        self.about_page.setObjectName("about_page")
        
        # 添加到导航栏
        self.addSubInterface(self.home_page, "home", "主页")
        self.addSubInterface(self.settings_page, "settings", "设置")
        self.addSubInterface(self.about_page, "about", "关于", NavigationItemPosition.BOTTOM)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())