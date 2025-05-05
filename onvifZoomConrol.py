from onvif import ONVIFCamera
import time
import keyboard  # For capturing keypresses

# Replace with your camera details
ip = '172.16.0.223'
port = 80
user = 'onvifuser'
passwd = 'onvif1234'
wsdl_path = r'/wsdlFile/wsdl'

# Connect to camera
cam = ONVIFCamera(ip, port, user, passwd, wsdl_dir=wsdl_path)
media = cam.create_media_service()
ptz = cam.create_ptz_service()
profile = media.GetProfiles()[0]

# Zoom Function
def zoom_camera(speed):
    req = ptz.create_type('ContinuousMove')
    req.ProfileToken = profile.token
    req.Velocity = {'Zoom': {'x': speed}}
    ptz.ContinuousMove(req)
    time.sleep(1.5)
    ptz.Stop({'ProfileToken': profile.token})

print("🎮 Press UP to Zoom In | DOWN to Zoom Out | ESC to Exit")

while True:
    try:
        if keyboard.is_pressed('up'):
            print("🔍 Zooming In")
            zoom_camera(0.01)
            time.sleep(0.1)
        elif keyboard.is_pressed('down'):
            print("🔎 Zooming Out")
            zoom_camera(-0.01)
            time.sleep(0.01)
        elif keyboard.is_pressed('esc'):
            print("🛑 Exiting Zoom Control")
            break
    except Exception as e:
        print("⚠️ Error:", e)
        break
