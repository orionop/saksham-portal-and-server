from fastapi import FastAPI, WebSocket, Response
from fastapi.responses import StreamingResponse
import asyncio
import json
import datetime as dt
import cv2

app = FastAPI()

def generate_camera_stream(camera_index: int):
    cap = cv2.VideoCapture(camera_index)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")
    cap.release()

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
    return StreamingResponse(generate_camera_stream(1), media_type="multipart/x-mixed-replace; boundary=frame")
