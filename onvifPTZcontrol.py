from onvif import ONVIFCamera
import time
import keyboard

# Camera config
ip = '172.16.0.223'
port = 80
user = 'onvifuser'
passwd = 'onvif1234'
wsdl_path = r'C:\Users\md\PycharmProjects\HLSServer\wsdlFile\wsdl'

# Connect to camera
cam = ONVIFCamera(ip, port, user, passwd, wsdl_dir=wsdl_path)
media = cam.create_media_service()
ptz = cam.create_ptz_service()
profile = media.GetProfiles()[0]

def move_camera(pan=0, tilt=0, zoom=0, duration=0.5):
    req = ptz.create_type('ContinuousMove')
    req.ProfileToken = profile.token
    req.Velocity = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': {'x': zoom}}
    ptz.ContinuousMove(req)
    time.sleep(duration)
    ptz.Stop({'ProfileToken': profile.token})

print("""
🎮 ONVIF PTZ Control Started
Use arrow keys for Pan/Tilt
Press 'z' to Zoom In, 'x' to Zoom Out
Press ESC to exit
""")

while True:
    try:
        if keyboard.is_pressed('up'):
            print("⬆️ Tilt Up")
            move_camera(tilt=0.3)
        elif keyboard.is_pressed('down'):
            print("⬇️ Tilt Down")
            move_camera(tilt=-0.3)
        elif keyboard.is_pressed('left'):
            print("⬅️ Pan Left")
            move_camera(pan=-0.3)
        elif keyboard.is_pressed('right'):
            print("➡️ Pan Right")
            move_camera(pan=0.3)
        elif keyboard.is_pressed('z') or keyboard.is_pressed('+'):
            print("🔍 Zoom In")
            move_camera(zoom=0.3)
        elif keyboard.is_pressed('x') or keyboard.is_pressed('-'):
            print("🔎 Zoom Out")
            move_camera(zoom=-0.3)
        elif keyboard.is_pressed('esc'):
            print("🛑 Exiting PTZ Control")
            break
        time.sleep(0.1)
    except Exception as e:
        print("⚠️ Error:", e)
        break
