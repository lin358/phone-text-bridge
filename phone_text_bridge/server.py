"""Phone-to-PC text transfer server."""

from __future__ import annotations

import socket

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from phone_text_bridge.config import load_config
from phone_text_bridge.paste import paste_text


app = FastAPI(title="Phone Text Bridge")
config = load_config()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return PHONE_PAGE


@app.post("/api/paste-text")
async def paste_plain_text(payload: dict) -> JSONResponse:
    text = str(payload.get("text", "")).strip()
    if text:
        paste_text(text)
    return JSONResponse({"ok": bool(text)})


def get_lan_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    finally:
        sock.close()


def main() -> None:
    lan_ip = get_lan_ip()
    scheme = "https" if config.ssl_certfile and config.ssl_keyfile else "http"
    print("手机和电脑连接同一个 Wi-Fi 后，用手机浏览器打开：")
    print(f"{scheme}://{lan_ip}:{config.port}")
    print("电脑本机也可以打开：")
    print(f"{scheme}://127.0.0.1:{config.port}")
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        ssl_certfile=config.ssl_certfile or None,
        ssl_keyfile=config.ssl_keyfile or None,
    )


PHONE_PAGE = r"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>手机文本传到电脑</title>
  <style>
    :root {
      color-scheme: light dark;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body { margin: 0; min-height: 100vh; background: #f6f7f9; color: #16181d; }
    main { min-height: 100vh; padding: 22px 20px 150px; display: flex; flex-direction: column; gap: 14px; }
    h1 { font-size: 24px; margin: 0; }
    .hint { margin: 0; color: #687083; line-height: 1.55; }
    .status { min-height: 26px; font-weight: 700; color: #2454d6; }
    textarea {
      width: 100%; flex: 1; min-height: 320px; resize: none; border: 1px solid #d8dce5;
      border-radius: 8px; padding: 14px; font-size: 18px; line-height: 1.6; background: white; color: inherit;
    }
    .dock {
      position: fixed; left: 0; right: 0; bottom: 0; padding: 16px 18px calc(18px + env(safe-area-inset-bottom));
      background: rgba(246,247,249,.94); backdrop-filter: blur(14px); border-top: 1px solid #dfe3ec;
    }
    .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    button { height: 58px; border: 0; border-radius: 8px; font-size: 18px; font-weight: 800; }
    #send { background: #1f6feb; color: white; }
    #clear { background: #e7eaf1; color: #2f3748; }
    @media (prefers-color-scheme: dark) {
      body { background: #111318; color: #f2f4f8; }
      textarea { background: #181b22; border-color: #303642; }
      .dock { background: rgba(17,19,24,.92); border-top-color: #303642; }
      .hint { color: #a8b0c2; }
      #clear { background: #252a34; color: #f2f4f8; }
    }
  </style>
</head>
<body>
  <main>
    <h1>手机文本传到电脑</h1>
    <p class="hint">在下面输入文字，也可以直接使用手机上的语音输入法。点“发送到电脑”后，文字会粘贴到电脑当前光标位置。</p>
    <div class="status" id="status">准备好了</div>
    <textarea id="text" autofocus placeholder="在这里输入，或使用手机语音输入法"></textarea>
  </main>
  <div class="dock">
    <div class="actions">
      <button id="clear" type="button">清空</button>
      <button id="send" type="button">发送到电脑</button>
    </div>
  </div>

  <script>
    const textEl = document.querySelector("#text");
    const statusEl = document.querySelector("#status");
    const sendButton = document.querySelector("#send");
    const clearButton = document.querySelector("#clear");

    sendButton.addEventListener("click", async () => {
      const text = textEl.value.trim();
      if (!text) {
        statusEl.textContent = "没有可发送的文字";
        return;
      }
      sendButton.disabled = true;
      statusEl.textContent = "正在发送...";
      try {
        const response = await fetch("/api/paste-text", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text })
        });
        const data = await response.json();
        if (data.ok) {
          textEl.value = "";
          textEl.focus();
          statusEl.textContent = "已发送到电脑，文本已清空";
        } else {
          statusEl.textContent = "发送失败";
        }
      } catch (error) {
        statusEl.textContent = "发送失败：" + (error && error.message ? error.message : error);
      } finally {
        sendButton.disabled = false;
      }
    });

    clearButton.addEventListener("click", () => {
      textEl.value = "";
      textEl.focus();
      statusEl.textContent = "已清空";
    });
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
