import serial
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
import re

# ================= 配置 =================
SERIAL_PORT = 'COM5'  # 🔴 改成你的端口
BAUD_RATE = 115200
# =======================================

app = FastAPI()

# 简单的 HTML 页面读取器
@app.get("/")
async def get():
    with open("dashboard.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(html_content)

# 数据解析函数
def parse_data(line):
    try:
        line_str = line.decode('utf-8', errors='ignore').strip()
        # 提取数字
        numbers = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line_str)
        if len(numbers) >= 2:
            return float(numbers[0]), float(numbers[1])
    except:
        pass
    return None, None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ 前端大屏已连接")
    
    try:
        # 打开串口
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01)
        
        while True:
            # 关键优化：非阻塞读取
            if ser.in_waiting:
                # 策略：如果缓冲区积压太多，直接读到最后一行，丢弃旧的，彻底消除延迟！
                if ser.in_waiting > 100: 
                    ser.reset_input_buffer() 
                
                line = ser.readline()
                weight, vib = parse_data(line)
                
                if weight is not None:
                    # 打包成 JSON 发送给前端
                    payload = json.dumps({"w": weight, "v": vib})
                    await websocket.send_text(payload)
            
            # 让出一点点 CPU 给 WebSocket 发送
            await asyncio.sleep(0.001)
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        await websocket.close()
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)