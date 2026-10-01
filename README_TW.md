\# 終末地連攜監測



> 一個基於螢幕辨識的《明日方舟：終末地》連攜狀態監測工具。



🌟 點一下右上角的 \*\*Star\*\*，就能收到軟體更新通知了哦\~



\[简体中文](README.md) | \[English](README\_EN.md) | \[繁體中文](README\_TW.md)



\## 功能簡介



\- \*\*懸浮窗\*\*：即時監測 4 個角色的連攜狀態，顯示在遊戲上方

\- \*\*多樣式\*\*：支援長條、圓環、餅圖、實心圓

\- \*\*高自訂\*\*：透明度、圓角、邊框、字體、顏色等，均可自由調節

\- \*\*角色獨立配色\*\*：每個角色的進度條可以設定不同的顏色

\- \*\*充能高亮\*\*：充能滿時，進度條會顯示光暈效果

\- \*\*預設系統\*\*：儲存/載入多套樣式，支援匯入匯出

\- \*\*智慧偵測\*\*：自動偵測遊戲視窗，僅在戰鬥時顯示懸浮窗

\- \*\*系統托盤\*\*：最小化到托盤，支援雙擊恢復



\## 介面展示



<img width="1280" height="720" alt="懸浮窗效果" src="https://github.com/user-attachments/assets/a68c0372-0c9c-4bcc-ac47-2034649ac5a0" />

<img width="388" height="116" alt="樣式1" src="https://github.com/user-attachments/assets/7ee556e3-067f-4074-b7a8-680434ef98d4" />

<img width="388" height="116" alt="樣式2" src="https://github.com/user-attachments/assets/6aef6ea9-6909-4d2f-8347-1b68a1296ce9" />



\## 下載安裝



前往 \[Releases](https://github.com/YuumiSama/EndfieldHUD/releases) 下載後，解壓縮並雙擊 `EndfieldHUD.exe` 即可執行。



\*\*無需安裝 Python 或其他依賴。\*\*



\## 快速上手



1\. 啟動軟體

2\. 主頁點 \*\*「啟動懸浮窗」\*\*

3\. 切到遊戲，進入戰鬥

4\. 懸浮窗自動顯示在螢幕上



\*\*調整位置\*\*：按住 `Ctrl` + 滑鼠拖動懸浮窗



\## 原始碼執行



需要 \*\*Python 3.12\*\* 或更高版本。



```bash

\# 複製倉庫

git clone https://github.com/YuumiSama/EndfieldHUD

cd EndfieldHUD



\# 安裝依賴

pip install -r requirements.txt



\# 執行

python main.py

```



\## 注意事項



\- 遇到問題請在 \[Issues](https://github.com/YuumiSama/EndfieldHUD/issues) 回報

\- 純 Python 圖像辨識，\*\*不修改遊戲檔案、不讀取遊戲記憶體\*\*

\- 請勿遮擋左下角，會影響辨識精度

\- 辨識過程中會佔用少量系統資源



\## 免責聲明



本工具僅供個人學習使用，不修改遊戲檔案、不讀取遊戲記憶體。使用本工具產生的任何問題，與開發者無關。



\## License



MIT



\---



如果覺得這個專案有幫助，可以點個 Star ⭐ 支持一下\~

