import asyncio
import json
import re
from contextlib import suppress
from pathlib import Path

import serial
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

SERIAL_PORT = "COM5"
BAUD_RATE = 115200
SERIAL_RETRY_SECONDS = 2
SERVER_PORT = 8000

app = FastAPI()

clients: set[WebSocket] = set()
latest_payload: str | None = None
serial_connected = False
serial_last_error: str | None = None
serial_task: asyncio.Task | None = None


def parse_data(line: bytes) -> tuple[float | None, float | None]:
    try:
        line_str = line.decode("utf-8", errors="ignore").strip()
        numbers = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line_str)
        if len(numbers) >= 2:
            return float(numbers[0]), float(numbers[1])
    except Exception:
        pass
    return None, None


async def broadcast(payload: str) -> None:
    stale_clients: list[WebSocket] = []

    for client in tuple(clients):
        try:
            await client.send_text(payload)
        except Exception:
            stale_clients.append(client)

    for client in stale_clients:
        clients.discard(client)


async def serial_reader_loop() -> None:
    global latest_payload
    global serial_connected
    global serial_last_error

    ser: serial.Serial | None = None

    while True:
        try:
            if ser is None or not ser.is_open:
                ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
                serial_connected = True
                serial_last_error = None
                print(f"[serial] connected to {SERIAL_PORT}")

            if ser.in_waiting > 100:
                ser.reset_input_buffer()

            if ser.in_waiting:
                line = ser.readline()
                weight, vib = parse_data(line)

                if weight is not None:
                    latest_payload = json.dumps({"w": weight, "v": vib})
                    await broadcast(latest_payload)

            await asyncio.sleep(0.01)
        except serial.SerialException as exc:
            serial_connected = False
            serial_last_error = str(exc)
            if ser is not None and ser.is_open:
                ser.close()
            ser = None
            print(f"[serial] unavailable: {serial_last_error}")
            await asyncio.sleep(SERIAL_RETRY_SECONDS)
        except Exception as exc:
            serial_connected = False
            serial_last_error = str(exc)
            if ser is not None and ser.is_open:
                ser.close()
            ser = None
            print(f"[serial] unexpected error: {serial_last_error}")
            await asyncio.sleep(SERIAL_RETRY_SECONDS)


@app.on_event("startup")
async def startup_event() -> None:
    global serial_task

    if serial_task is None or serial_task.done():
        serial_task = asyncio.create_task(serial_reader_loop())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global serial_task

    if serial_task is not None:
        serial_task.cancel()
        with suppress(asyncio.CancelledError):
            await serial_task
        serial_task = None


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "port": SERVER_PORT,
            "serialPort": SERIAL_PORT,
            "serialConnected": serial_connected,
            "clientCount": len(clients),
            "lastError": serial_last_error,
        }
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    clients.add(websocket)
    print(f"[ws] frontend connected, clients={len(clients)}")

    if latest_payload is not None:
        await websocket.send_text(latest_payload)

    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
    finally:
        clients.discard(websocket)
        print(f"[ws] frontend disconnected, clients={len(clients)}")


dist_dir = Path(__file__).resolve().parent / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
