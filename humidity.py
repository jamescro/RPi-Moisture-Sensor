'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from sense_hat import SenseHat
import logging
import time
import argparse
import json
from datetime import datetime


# Custom MQTT message callback
class CallbackContainer(object):

    def __init__(self, client):
        self._client = client
        
    def publishMessage(self, client, userdata, triggerMessage):
      print("Received a new message: ")
      print(triggerMessage.payload)
      print("from topic: ")
      print(triggerMessage.topic)
      print("--------------\n\n")    
      # Get humidity reading from SenseHat
      sense = SenseHat()
      sense.clear()
      humidity = sense.get_humidity()
      timestamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
      # Publish to the topic
      message = {}
      message['humidity'] = humidity
      message['timestamp'] = timestamp
      messageJson = json.dumps(message)
      print (publishTopic)
      print (messageJson)
      self._client.publishAsync(publishTopic, str(messageJson), 1, self.pubackCallback)
      print('Published topic %s: %s\n' % (publishTopic, messageJson))
      self._client.subscribeAsync(subscribeTopic, 1, self.subackCallback, self.publishMessage)
      
    def pubackCallback(self, mid):
        print("Received PUBACK packet id: ")
        print(mid)
        print("++++++++++++++\n\n")

    def subackCallback(self, mid, data):
        print("Received SUBACK packet id: ")
        print(mid)
        print("Granted QoS: ")
        print(data)
        print("++++++++++++++\n\n")

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", dest="host", default="a3w2lnng1ocxhu.iot.us-east-1.amazonaws.com", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", dest="rootCAPath", default= "rootCA.pem", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", default="b38ddbbc77-certificate.pem.crt", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", default="b38ddbbc77-private.pem.key", help="Private key file path")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="publishTopic", default="things/sensehat/humidity", help="Topic to publish")
parser.add_argument("-s", "--stopic", action="store", dest="subscribeTopic", default="things/sensehat/humiditytrigger", help="Topic to subscribe")
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    help="Message to publish")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
publishTopic = args.publishTopic
subscribeTopic = args.subscribeTopic
clientId = args.clientId


# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None

myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myCallbackContainer = CallbackContainer(myAWSIoTMQTTClient)
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(subscribeTopic, 1, myCallbackContainer.publishMessage)
time.sleep(2)

try:
    while True:
        time.sleep(1)
 
except KeyboardInterrupt:
    print "exiting"
    client.disconnect()
    client.loop_stop()

