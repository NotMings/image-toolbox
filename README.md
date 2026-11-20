# Image Toolbox

基于 Python + PySide6 的图片批量处理工具，支持图形界面和命令行两种模式。

## 运行

运行打包后的程序 `dist/main/main.exe`：

```powershell
.\dist\main\main.exe
```

双击启动图形界面；带参数运行命令行模式（无桌面环境同样可用）：

```powershell
.\dist\main\main.exe --help
.\dist\main\main.exe -i .\photos -o .\out --format jpeg --recursive --threads 8
.\dist\main\main.exe -i .\photos -o .\out --compress 100
```

查看全部参数：`--help`（也支持 `-h`）；`--version` 查看版本。

命令行退出码：`0` 成功，`1` 参数或运行错误，`2` 有图片失败/跳过，`3` 被取消。

## 功能

- 格式转换：JPEG / PNG / WebP
- 压缩：压缩到目标 KB，必要时自动裁剪
- 重命名：UUID / MD5 / 自增序号
- 多线程：1-128 个线程
- 暂停 / 取消（正在处理的图片完成后停止）
- 透明图片转 JPEG、输出重名时弹窗询问处理方式

## 编译

```powershell
pip install pillow pyside6 pyinstaller
pyinstaller main.py
```

生成的可执行文件在 `dist/main/`。

## 注意

- 输出文件与已有文件重名时会询问处理方式，建议输出到空文件夹。
- 压缩率有限，目标过小时会裁剪图片。
- 请确保您有权修改原始文件，尊重版权。
