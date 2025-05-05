import os
from flask import Flask, render_template, Response, request, jsonify
from onvif import ONVIFCamera
from lxml import etree
import zeep, cv2, time, threading

# ─── Zeep fix
zeep.xsd.simple.AnySimpleType.pythonvalue = lambda self, xmlvalue: xmlvalue

app = Flask(__name__)

# ─── Only initialize ONVIF once, in the real process ───────────────────────────
if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    # ─── CONFIG
    IP       = '172.16.0.223'
    PORT     = 80
    USER     = 'onvifuser'
    PASSWD   = 'onvif1234'
    WSDL_DIR = r'C:\Users\md\PycharmProjects\HLSServer\ONVIF\wsdlFile\wsdl'
    RTSP_URL = f'rtsp://admin:seera2014@{IP}:554/Streaming/Channels/102'

    # ─── Events service
    ev_cam         = ONVIFCamera(IP, PORT, USER, PASSWD, WSDL_DIR)
    events_service = ev_cam.create_events_service()
    sub            = events_service.CreatePullPointSubscription()
    pull_svc       = ev_cam.create_pullpoint_service(sub.SubscriptionReference.Address)

    # ─── Media & PTZ (unchanged) ────────────────────────────────────────────────
    media_cam      = ONVIFCamera(IP, PORT, USER, PASSWD, WSDL_DIR)
    media_svc      = media_cam.create_media_service()
    TOKEN          = media_svc.GetProfiles()[0].token

    ptz_cam        = ONVIFCamera(IP, PORT, USER, PASSWD, WSDL_DIR)
    ptz_svc        = ptz_cam.create_ptz_service()

    # ─── In-memory events list ──────────────────────────────────────────────────
    events = []

    def parse_event(msg):
        # one record per NotificationMessage
        record = {
            'time':   time.strftime('%Y-%m-%d %H:%M:%S'),
            'event_type': None,
            'object_id':  None,
            'status':     None
        }
        xml = getattr(msg.Message, '_value_1', None)
        if xml is None:
            return

        for item in xml.iterfind('.//{*}SimpleItem'):
            name = item.attrib['Name']
            val  = item.attrib['Value']

            if name == 'Rule':
                record['event_type'] = val
            elif name == 'ObjectId':
                record['object_id'] = val
            elif name == 'IsInside':
                # intrusion detector
                record['status'] = val == 'true' and 'Intrusion' or 'OK'
            elif name == 'RelayToken':
                record['event_type'] = val
            elif name == 'LogicalState':
                record['status'] = val

        # only keep if we have at least an event_type
        if record['event_type']:
            events.append(record)
            # cap at last 50
            if len(events) > 50:
                del events[:-50]

    def event_listener():
        while True:
            try:
                resp = pull_svc.PullMessages({'Timeout': 'PT10S', 'MessageLimit': 5})
                for nm in getattr(resp, 'NotificationMessage', []):
                    parse_event(nm)
            except Exception as e:
                print("⚠️ Pull error:", e)
            time.sleep(2)

    threading.Thread(target=event_listener, daemon=True).start()

# ─── VIDEO STREAM, PTZ ROUTES ───────────────────────────────────────────────────
def gen_frames():
    cap = cv2.VideoCapture(RTSP_URL)
    while True:
        ret, frame = cap.read()
        if not ret: break
        _, buf = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buf.tobytes() +
               b'\r\n')
    cap.release()

def ptz_move(pan=0, tilt=0, zoom=0, duration=1):
    try:
        req = ptz_svc.create_type('ContinuousMove')
        req.ProfileToken = TOKEN
        req.Velocity = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': {'x': zoom}}
        ptz_svc.ContinuousMove(req)
        time.sleep(duration)
        ptz_svc.Stop({'ProfileToken': TOKEN})
    except Exception as e:
        print("⚠️ PTZ error:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/ptz', methods=['POST'])
def ptz():
    action = request.json.get('action')
    moves = {
        'up': (0, 0.5, 0), 'down': (0, -0.5, 0),
        'left': (-0.5, 0, 0), 'right': (0.5, 0, 0),
        'zoomin': (0, 0, 0.5), 'zoomout': (0, 0, -0.5),
        'stop': (0, 0, 0)
    }
    if action in moves:
        threading.Thread(target=ptz_move, args=(*moves[action],)).start()
    return jsonify(status='OK')

@app.route('/events')
def get_events():
    resp = jsonify(events)
    resp.headers['Cache-Control'] = 'no-store'
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
