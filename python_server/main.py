from fastapi import FastAPI, WebSocket, Response
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse 
import asyncio
import json
import datetime as dt
import cv2
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  


GPIO = False
if GPIO:
    import RPi.GPIO as gpio
import time
from threading import Lock
movement_lock = Lock()
current_movement = None



pin_m1 = 5
pin_m2 = 6
pin_m3 = 26
pin_m4 = 16
if GPIO:
    def init():
        gpio.setmode(gpio.BCM)
        gpio.setup(pin_m1, gpio.OUT)
        gpio.setup(pin_m2, gpio.OUT)
        gpio.setup(pin_m3, gpio.OUT)
        gpio.setup(pin_m4, gpio.OUT)

    def set_motors(m1, m2, m3, m4):
        gpio.output(pin_m1, m1)
        gpio.output(pin_m2, m2)
        gpio.output(pin_m3, m3)
        gpio.output(pin_m4, m4)


app = FastAPI()

def generate_camera_stream(camera_index: int):
    cap = cv2.VideoCapture(camera_index)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        results = model(frame)
        annotated_frame = results[0].plot()
        _, jpeg = cv2.imencode('.jpg', annotated_frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")
    cap.release()



# CAMERAS and DATA
@app.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            
            data = {
                "timestamp": dt.datetime.now().isoformat(),
                "cameraId": '1', 
                "gasConcentration": 23,
                "personDetected": False,
                "coordinates": {
                    "lat": 0.0,
                    "lng": 0.0,
                }
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/camera1")
def camera1():
    return StreamingResponse(generate_camera_stream(0), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/camera2")
def camera2():
    return StreamingResponse(generate_camera_stream(0), media_type="multipart/x-mixed-replace; boundary=frame")


# MOTORS
if GPIO:
    @app.get("/start/{direction}")
    def start_movement(direction: str):
        global current_movement
        with movement_lock:
            init()
            current_movement = direction
            if direction == "forward":
                set_motors(False, True, True, False)
            elif direction == "reverse":
                set_motors(True, False, False, True)
            elif direction == "left":
                set_motors(True, False, True, False)
            elif direction == "right":
                set_motors(False, True, False, True)
        return {"status": "success", "action": f"started {direction}"}

    @app.get("/stop")
    def stop_movement():
        global current_movement
        with movement_lock:
            if current_movement is not None:
                current_movement = None
        return {"status": "success", "action": "stopped"}

    @app.get("/")
    async def read_index():
        return FileResponse('index.html')