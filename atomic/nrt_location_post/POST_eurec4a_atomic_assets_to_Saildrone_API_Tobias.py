#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import time
import json
import numpy as np
import requests
global saildrone_key

def get_key(file_name):
    myvars = {}
    with open(file_name) as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            myvars[name.strip()] = str(var).rstrip()
    return myvars

file_key = "C:/Users/gentemann/Google Drive/f_drive/secret_keys/tobias_login_eurec4a_v2.txt"
mqtt_key = get_key(file_key)
MQTT_USER = mqtt_key['username']
MQTT_PASSWORD = mqtt_key['password']

file_key = "C:/Users/gentemann/Google Drive/f_drive/secret_keys/saildrone_eurec4a_v2.txt"
saildrone_key = get_key(file_key)

def _main():
    import paho.mqtt.client as mqtt
    global saildrone_key
    
    def on_connect(client, userdata, flags, rc):
        print("MQTT: connected with result code {}".format(rc))
        client.subscribe("platform/+/location")
    def on_disconnect(client, userdata, rc):
        print("MQTT: disonnected with result code {}".format(rc))
    def on_message(client, userdata, msg):
        global saildrone_key
        def convertunix(date):
            #we don't need the Z at the end
            date = np.datetime64(date.replace('Z', ''))
            timestamp = (date - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')
            return timestamp

        topic = msg.topic.split("/")
        if topic[0] != "platform" or topic[2] != "location":
            return
        short_name = topic[1]
#        print("{}: {}".format(short_name, msg.payload))
        save_name=short_name.replace(" ", "") 
        save_msg = json.loads(msg.payload)
     #   save_msg["name"]=save_name
        save_msg["mmsi"]=save_name
        save_msg["latitude"]=save_msg["lat"]
        save_msg["longitude"]=save_msg["lon"]
        save_msg["timestamp"]=convertunix(save_msg["time"]) 
        if save_msg.get('ground_speed', 0):
            save_msg["sog"]=save_msg["ground_speed"]
            del save_msg["ground_speed"]
        if save_msg.get('heading', 0):
            save_msg["hdg"]=save_msg["heading"]
            del save_msg["heading"]
        del save_msg["ground_speed"]
        del save_msg["lat"]
        del save_msg["lon"]
        del save_msg["time"]

        print('save_msg',save_msg)
        #POST TO SAILDRONE
        payload=save_msg 
        headers={'Content-Type':'application/json', 'Accept':'application/json','authorization':saildrone_key['token']}
        url = 'https://developer-mission.saildrone.com/v1/ais'
        res = requests.post(url, json=payload, headers=headers)
        print('POST',res.status_code, res.reason)
    def on_log(client, userdata, level, buf):
        print("#LOG: {} {}".format(level, buf))

    
    client = mqtt.Client()
#    client.tls_set(ca_certs=os.path.join(os.path.dirname(__file__), "trustid-x3-root.pem.txt"))
    client.tls_set(ca_certs=os.path.join('C:/Users/gentemann/Google Drive/f_drive/secret_keys/', "trustid-x3-root.pem.txt"))
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_log = on_log
    print("initial connect: {}".format(client.connect("mqtt.eurec4a.eu", 8883, 60)))
    client.loop_forever()
    
if __name__ == "__main__":
    _main()


# In[ ]:




