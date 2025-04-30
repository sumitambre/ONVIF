from onvif import ONVIFCamera
from lxml import etree
import zeep
import time

# Fix for zeep compatibility
zeep.xsd.simple.AnySimpleType.pythonvalue = lambda self, xmlvalue: xmlvalue

# Camera Info (🔁 Replace with your values)
camera_ip = '172.16.0.64'
username = 'onvifuser'
password = 'onvif1234'
port = 80
wsdl_path = r'C:\Users\md\PycharmProjects\HLSServer\wsdlFile\wsdl'  # Replace with actual path

# Connect to camera
cam = ONVIFCamera(camera_ip, port, username, password, wsdl_dir=wsdl_path)

# Create Events Service
events_service = cam.create_events_service()

# Create PullPoint Subscription
print("🛠️ Creating PullPoint Subscription...")
sub = events_service.CreatePullPointSubscription()
pullpoint_address = sub.SubscriptionReference.Address
print("📡 PullPoint URL:", pullpoint_address)

# Create PullPoint binding
pullpoint_service = cam.create_pullpoint_service(pullpoint_address)
print("✅ Connected to PullPoint. Listening for events...\n")

# Function to parse event messages
def parse_event(msg):
    try:
        if hasattr(msg.Message, '_value_1'):
            xml = msg.Message._value_1
            xml_str = etree.tostring(xml, pretty_print=True).decode()
            print("📄 Full Event XML:\n", xml_str)

            for item in xml.iter():
                if item.tag.endswith("SimpleItem"):
                    name = item.attrib.get("Name")
                    value = item.attrib.get("Value")
                    print(f"🔔 {name} = {value}")
    except Exception as e:
        print("⚠️ Error parsing event:", e)

# Infinite loop to pull events
while True:
    try:
        res = pullpoint_service.PullMessages({
            'Timeout': 'PT10S',
            'MessageLimit': 5
        })
        for msg in res.NotificationMessage:
            parse_event(msg)
    except Exception as e:
        print("⚠️ Error pulling messages:", e)
        break
    time.sleep(2)
