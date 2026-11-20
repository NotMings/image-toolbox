# Image Toolbox

[English](README.md) | [简体中文](README.zh_CN.md) | [繁體中文](README.zh_TW.md)

基於 Python + PySide6 的圖片批次處理工具，支援圖形介面與命令列兩種模式。

## 執行

執行打包後的程式 `dist/image-toolbox.exe`：

```powershell
.\dist\image-toolbox.exe
```

雙擊啟動圖形介面；帶參數執行命令列模式（命令列介面為英文，無桌面環境同樣可用）：

```powershell
.\dist\image-toolbox.exe --help
.\dist\image-toolbox.exe -i .\photos -o .\out --format jpeg --recursive --threads 8
.\dist\image-toolbox.exe -i .\photos -o .\out --compress 100
```

查看全部參數（英文）：`--help`（也支援 `-h`）；`--version` 查看版本。

命令列結束碼：`0` 成功，`1` 參數或執行錯誤，`2` 有圖片失敗/略過，`3` 已取消。

## 功能

- 格式轉換：JPEG / PNG / WebP
- 壓縮：壓縮到目標 KB，必要時自動裁切
- 重新命名：UUID / MD5 / 自動遞增序號
- 多執行緒：1-128 個執行緒
- 暫停 / 取消（正在處理的圖片完成後停止）
- 透明圖片轉 JPEG、輸出名稱重複時彈窗詢問處理方式
- 介面依系統語言自動選擇（簡體中文 / 繁體中文，其他語言預設英文），可在「語言」選單修改；命令列介面為英文

## 編譯

```powershell
pip install pillow pyside6 pyinstaller
pyinstaller image-toolbox.spec
```

產生的執行檔是 `dist/image-toolbox.exe`。`image-toolbox.spec` 已包含單檔、主控台、圖示、`assets` 與翻譯檔設定。

翻譯檔位於 `app/locales/zh_CN` 與 `app/locales/zh_TW`，msgid 為英文；修改後先執行 `python tools/build_catalogs.py` 重新產生 `.mo` 再打包。

## 注意

- 輸出檔與現有檔名重複時會詢問處理方式，建議輸出到空資料夾。
- 壓縮率有限，目標過小時會裁切圖片。
- 請確認您有權修改原始檔案，並尊重版權。
