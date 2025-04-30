from onvif import ONVIFCamera
from lxml import etree
import zeep
import time

zeep.xsd.simple.AnySimpleType.pythonvalue = lambda self, xmlvalue: xmlvalue

# Setup camera connection
cam = ONVIFCamera('172.16.0.64', 80, 'onvifuser', 'onvif1234',
                  wsdl_dir=r"C:\Users\md\PycharmProjects\HLSServer\wsdlFile\wsdl")

# Create the proper events service
events_service = cam.create_events_service()

# Create PullPointSubscription
print("🛠️ Creating PullPointSubscription...")
subscription = events_service.CreatePullPointSubscription()
pullpoint = subscription.SubscriptionReference.Address
print("📡 Subscription PullPoint URL:", pullpoint)

# Now bind to that PullPoint to pull messages
pullpoint_service = cam.create_pullpoint_service(pullpoint)

print("✅ Connected to PullPoint. Listening for events...\n")


def parse_event(msg):
    try:
        if hasattr(msg.Message, '_value_1'):
            xml = msg.Message._value_1
            xml_str = etree.tostring(xml, pretty_print=True).decode()
            print("\n📄 Full Event XML:")
            print(xml_str)

            event_time = xml.get('UtcTime') or 'No Timestamp'
            for node in xml.iter():
                if node.tag.endswith('SimpleItem'):
                    name = node.attrib.get('Name')
                    value = node.attrib.get('Value')
                    print(f"🔎 {name} = {value} at {event_time}")
    except Exception as e:
        print("⚠️ Parsing Error:", e)


while True:
    try:
        response = pullpoint_service.PullMessages({
            'Timeout': 'PT10S',
            'MessageLimit': 10
        })

        for msg in response.NotificationMessage:
            print("🔔 Raw Event Received")
            parse_event(msg)

    except Exception as e:
        print("⚠️ Error pulling messages:", e)
        break
    time.sleep(2)
