from fastapi import FastAPI, WebSocket, Response
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse 
import asyncio
import json
import datetime as dt
import cv2
from ultralytics import YOLO
import threading
import serial

model = YOLO('yolov8n.pt')  
PORT = '/dev/ttyACM0'
LAT,LON = 0.0,0.0
detected = False
u_id = 0

GPIO = True
if GPIO:
    import RPi.GPIO as gpio

movement_lock = threading.Lock()

current_movement = None

def ser_thread():
    global detected, u_id
    ser = serial.Serial(PORT, 9600)
    ser.reset_input_buffer()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith('motion detected') and not detected:
                detected = True
                u_id += 1
            elif line.startswith('motion ended') and detected:
                detected = False
                u_id += 1


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

def generate_camera_stream(camera_index: int,run_inference=False):
    cap = cv2.VideoCapture(camera_index)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        if run_inference:
            results = model(frame)
            annotated_frame = results[0].plot()
            _, jpeg = cv2.imencode('.jpg', annotated_frame)
        else:
            _, jpeg = cv2.imencode('.jpg', frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")
    cap.release()



# CAMERAS and DATA
@app.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    global detected, u_id
    
    await websocket.accept()
    try:
        last_id = None
        while True:
            if last_id != u_id:
                data = {
                    "timestamp": dt.datetime.now().isoformat(),
                    "cameraId": '1', 
                    "gasConcentration": 23,
                    "personDetected": detected,
                    "coordinates": {
                        "lat": LAT,
                        "lng": LON,
                    }
                }
                await websocket.send_text(json.dumps(data))
                last_id = u_id
                await asyncio.sleep(1)
            else:
                print("No new data")
                await asyncio.sleep(0.1)

                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# ROVER CAMERA, change index when connecting to rpi as needed
@app.get("/camera1")
def camera1(): 
    return StreamingResponse(generate_camera_stream(1,run_inference=True), media_type="multipart/x-mixed-replace; boundary=frame")

# DRONE CAMERA, change index when connecting to rpi as needed
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
    
if __name__ == "__main__":
    t = threading.Thread(target=ser_thread)
    t.start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",port=7090)