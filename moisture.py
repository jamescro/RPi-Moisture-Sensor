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
import RPi.GPIO as GPIO # This is the GPIO library we need to use the GPIO pins on the Raspberry Pi
import logging
import time
import argparse
import json
from datetime import datetime


# Custom MQTT message callback
        
def publishMessage(channel):
	if GPIO.input(channel):
		print "LED off"
        if currentLEDValue == 'on':
            global currentLEDValue
            currentLEDValue = 'off'
            myAWSIoTMQTTClient.connectAsync(ackCallback=conackCallback)
            timestamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
            message = {}
            message['timestamp'] = timestamp
            message['LED'] = currentLEDValue
            #Publish to the topic
            messageJson = json.dumps(message)
            print (publishTopic)
            print (messageJson)
            myAWSIoTMQTTClient.publishAsync(publishTopic, str(messageJson), 1, pubackCallback)
            print('Published topic %s: %s\n' % (publishTopic, messageJson))
	else:
		print "LED on"
        if currentLEDValue == 'off':
            global currentLEDValue
            currentLEDValue = 'on'
            myAWSIoTMQTTClient.connectAsync(ackCallback=conackCallback)
            timestamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
            message = {}
            message['timestamp'] = timestamp
            message['LED'] = currentLEDValue
            #Publish to the topic
            messageJson = json.dumps(message)
            print (publishTopic)
            print (messageJson)
            myAWSIoTMQTTClient.publishAsync(publishTopic, str(messageJson), 1, pubackCallback)
            print('Published topic %s: %s\n' % (publishTopic, messageJson))
  
def pubackCallback(self, mid):
    print("Received PUBACK packet id: ")
    print(mid)
    print("++++++++++++++\n\n")

def conackCallback(self, mid):
    print("Received CONNACK packet id: ")
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
parser.add_argument("-t", "--topic", action="store", dest="publishTopic", default="things/moisturesensor/plant", help="Topic to publish")
#parser.add_argument("-s", "--stopic", action="store", dest="subscribeTopic", default="things/moisture/moisturetrigger", help="Topic to subscribe")
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    help="Message to publish")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
publishTopic = args.publishTopic
#subscribeTopic = args.subscribeTopic
clientId = args.clientId
global currentLEDValue
currentLEDValue = 'on'

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

# Set our GPIO numbering to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin that we have our digital output from our sensor connected to
channel = 17
# Set the GPIO pin to an input
GPIO.setup(channel, GPIO.IN)
# This line tells our script to keep an eye on our gpio pin and let us know when the pin goes HIGH or LOW
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
# This line asigns a function to the GPIO pin so that when the above line tells us there is a change on the pin, run this function
GPIO.add_event_callback(channel, publishMessage)

try:
    while True:
        time.sleep(1)
 
except KeyboardInterrupt:
    print "exiting"
    client.disconnect()
    client.loop_stop()

