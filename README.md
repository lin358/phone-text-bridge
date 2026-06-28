# Phone Text Bridge

一个很小的本地工具：把手机网页里的文本，一键发送到电脑当前光标位置。

它适合这样的场景：你想在电脑上输入一段较长文字，但手机上的语音输入法、输入体验或临时编辑更方便。电脑运行本地服务后，手机打开网页，输入或语音转文字，点一下按钮，文字就会粘贴到电脑当前光标所在的位置。

这个项目不做语音识别，不调用任何云端 ASR，也不需要安装手机 App。语音输入交给手机输入法，这个工具只负责把手机里的文本送到电脑。

## 功能

- 手机浏览器打开局域网网页即可使用
- 文本发送到电脑当前光标位置
- 电脑端通过剪贴板和 `Ctrl+V` 完成粘贴
- 发送成功后自动清空手机文本框
- 如果电脑端无法确认文本光标，会尝试发送但保留手机文本
- 手机页面保留手动清空按钮，方便处理特殊软件识别不到输入框的情况
- 支持 HTTP 或本地自签名 HTTPS
- 适合 Windows 自用小工具

## 使用方式

安装依赖：

```powershell
pip install -r requirements.txt
```

如需 HTTPS，先生成本地自签名证书：

```powershell
python -m phone_text_bridge.make_https_cert
```

然后参考 `.env.example` 创建 `.env`，填写证书路径。例如：

```env
BRIDGE_HOST=0.0.0.0
BRIDGE_PORT=8766
BRIDGE_SSL_CERTFILE=certs/bridge-cert.pem
BRIDGE_SSL_KEYFILE=certs/bridge-key.pem
```

启动服务：

```powershell
start_visible.bat
```

启动后窗口里会显示手机访问地址，例如：

```text
https://192.168.31.122:8766
```

电脑和手机连接同一个 Wi-Fi 或同一个手机热点后，用手机浏览器打开这个地址。

使用时，先把电脑光标放到要输入的文字框里，再从手机页面发送文本。电脑端会先尝试粘贴；如果 Windows 明确报告了文本光标，发送后手机文本框会自动清空。如果电脑端无法确认文本光标，手机文本会保留；你可以确认是否已经粘贴成功，再手动清空。

停止服务：关闭启动窗口，或在窗口里按 `Ctrl+C`。手机关掉网页只会关闭手机页面，不会停止电脑上的服务。

如果需要强制停止占用 `8766` 端口的服务，可以运行：

```powershell
powershell -ExecutionPolicy Bypass -File stop.ps1
```

第一次访问自签名 HTTPS 地址时，手机浏览器可能会提示证书不受信任。这个证书只用于本地局域网访问，确认地址是自己的电脑后，选择继续访问即可。

如果校园网、公司 Wi-Fi 或公共网络禁止设备互相访问，可以改用手机热点：让电脑连接手机热点后再打开网页。

## 安全边界和风险

这个工具默认面向自用和可信局域网，不适合直接暴露到公网。

需要注意：

- 局域网内能访问这个服务的人，理论上都可以向你的电脑当前光标位置发送文本。
- 粘贴动作发生在电脑当前焦点所在位置。使用前先确认电脑光标确实在你想输入的文字框里。
- 当前版本会尝试粘贴；只有 Windows 明确报告了文本插入光标时，才会自动清空手机文本。某些特殊软件可能可以粘贴，但无法被确认。
- HTTPS 使用的是本地自签名证书，只解决浏览器访问 HTTPS 的基础需求，不等于公网级安全部署。
- `.env`、证书私钥和日志不应提交到 GitHub。

建议：

- 只在自己的家庭网络、个人热点等可信环境下使用。
- 不要在公共网络、公司网络或不可信局域网中长期运行。
- 如需更强保护，可以后续增加访问口令或一次性 token。

## 设计取舍

这个项目故意保持简单：

- 不内置语音识别
- 不调用豆包、火山或其他云端 ASR API
- 不做跨设备账号系统
- 不同步剪贴板历史
- 不安装手机端 App

手机输入法已经能很好地完成语音输入、联想和文本编辑。这个工具只补上最后一步：把手机上的文本送到电脑当前光标处。

## English

Phone Text Bridge is a tiny local tool that sends text from a phone web page to the active cursor position on a Windows PC.

Run the FastAPI service on your computer, open `http://<your-lan-ip>:8766` or `https://<your-lan-ip>:8766` on your phone, type or dictate text with your phone keyboard, then tap the send button. The PC copies the text to the clipboard and presses `Ctrl+V`, so the text appears wherever the current cursor is.

If the PC does not report an active text caret, the app still attempts to paste, but keeps the phone text instead of clearing it.

It does not include speech recognition, does not call any cloud ASR API, and does not require a mobile app. Speech input is handled by your phone keyboard or input method.

Security notes:

- Use it only on trusted local networks.
- Anyone who can access the service may be able to paste text into your active PC window.
- Check the active cursor position before sending text.
- Do not expose the service to the public internet.
- Do not commit `.env`, private certificate keys, or logs.

## License

MIT
