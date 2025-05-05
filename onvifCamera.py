from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError
import requests
import socket

try:
    cam = ONVIFCamera(
        '172.16.0.223',
        80,
        'onvifuser',
        'onvif1234',
        wsdl_dir=r'/wsdlFile/wsdl'
    )
    print("✅ Connected to Camera Successfully!")

except ONVIFError as e:
    print(f"⚠️ ONVIF Error: {e}")

except requests.exceptions.ConnectionError:
    print("⚠️ Network Error: Unable to connect to Camera (IP might be wrong or camera offline)")

except socket.timeout:
    print("⚠️ Timeout Error: Camera not responding")

except Exception as e:
    print(f"⚠️ Unexpected Error: {e}")
