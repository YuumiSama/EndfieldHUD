# 终末地连携监测

> 一个基于屏幕识别的《明日方舟：终末地》连携状态监测工具。

🌟 点一下右上角的 **Star**，就能收到软件更新通知了哦~

简体中文 | [English](README_EN.md) | [繁體中文](README_TW.md)

## 功能简介

- **悬浮窗**：实时监测 4 个角色的连携状态，显示在游戏上方
- **多样式**：支持长条、圆环、饼图、实心圆
- **高自定义**：透明度、圆角、边框、字体、颜色等，均可自由调节
- **角色独立配色**：每个角色的进度条可以设置不同的颜色
- **充能高亮**：充能满时，进度条会显示光晕效果
- **预设系统**：保存/加载多套样式，支持导入导出
- **智能检测**：自动检测游戏窗口，仅在战斗时显示悬浮窗
- **系统托盘**：最小化到托盘，支持双击恢复

## 界面展示

<img width="1280" height="720" alt="悬浮窗效果" src="https://github.com/user-attachments/assets/a68c0372-0c9c-4bcc-ac47-2034649ac5a0" />
<img width="388" height="116" alt="样式1" src="https://github.com/user-attachments/assets/7ee556e3-067f-4074-b7a8-680434ef98d4" />
<img width="388" height="116" alt="样式2" src="https://github.com/user-attachments/assets/6aef6ea9-6909-4d2f-8347-1b68a1296ce9" />

## 下载安装

前往 [Releases](https://github.com/YuumiSama/EndfieldHUD/releases) 下载后，解压双击 `EndfieldHUD.exe` 即可运行。

**无需安装 Python 或其他依赖。**

## 快速上手

1. 启动软件
2. 主页点 **“启动悬浮窗”**
3. 切到游戏，进入战斗
4. 悬浮窗自动显示在屏幕上

**调整位置**：按住 `Ctrl` + 鼠标拖动悬浮窗

## 源码运行

需要 **Python 3.12** 或更高版本。

```bash
# 克隆仓库
git clone https://github.com/YuumiSama/EndfieldHUD
cd EndfieldHUD

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

## 注意事项

- 遇到问题请在 [Issues](https://github.com/YuumiSama/EndfieldHUD/issues) 反馈
- 纯 Python 图像识别，**不修改游戏文件、不读取游戏内存**
- 请勿遮挡左下角，会影响识别精度
- 识别过程中会占用少量系统资源

## 免责声明

本工具仅供个人学习使用，不修改游戏文件、不读取游戏内存。使用本工具产生的任何问题，与开发者无关。

## License

MIT

---

如果觉得这个项目有帮助，可以点个 Star ⭐ 支持一下~
