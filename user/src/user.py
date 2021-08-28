# You'll always  have to import these components
from is_wire.core import Channel, Subscription, Message, StatusCode
from is_msgs.common_pb2 import Phrase, Position 
from RequisicaoRobo_pb2 import RequisicaoRobo
from google.protobuf.empty_pb2 import Empty
from loguru import logger
from time import sleep
import socket
import os
import json

def read_configuration(config_path):
  with open(config_path) as f:
    return json.load(f)

config_path = os.getenv('CONFIG_PATH', './conf/config.json')
configs = read_configuration(config_path)

AMQ_HOST = os.getenv('AMQ_HOST', configs["amq_host"])
MOVE_ROBOT_FUNCTION_NAME = os.getenv('MOVE_ROBOT_FUNCTION_NAME', configs["move_robot_function_name"])
LOCATE_ROBOT_FUNCTION_NAME = os.getenv('LOCATE_ROBOT_FUNCTION_NAME', configs["locate_robot_function_name"])
TOPIC_TO_CONTROL_ROBOT = os.getenv('TOPIC_TO_CONTROL_ROBOT', configs["topic_to_control_the_robot"])
MESSAGE_TO_START_CONTROLLER = os.getenv('MESSAGE_TO_START_CONTROLLER', configs["message_to_start_the_controller"])
TOPIC_TO_START_CONTROLLER = os.getenv('TOPIC_TO_START_CONTROLLER', configs["topic_to_start_the_controller"])
START_ROBOT_POSITION_X = os.getenv('START_ROBOT_POSITION_X', configs["start_robot_in_position_x"])
START_ROBOT_POSITION_Y = os.getenv('START_ROBOT_POSITION_Y', configs["start_robot_in_position_y"])

channel = Channel(AMQ_HOST)
subscription = Subscription(channel)

phrase = Phrase()
phrase.content.extend(MESSAGE_TO_START_CONTROLLER)
message = Message(content=phrase, reply_to=subscription)

while True:
    logger.info("Starting the Controller")
    channel.publish(message, topic=TOPIC_TO_START_CONTROLLER)
    reply = channel.consume(timeout=1.0)
    if reply.status.code == StatusCode.OK:
        logger.info("The Controller is up and running!")
        break
    else:
        logger.info("The controller failled to start. Trying again in 2 seconds...")
        sleep(2)

x = START_ROBOT_POSITION_X
y = START_ROBOT_POSITION_Y

while True:

    logger.info(f'Moving Robot to ({x},{y}) ')
    position = Position(x=x, y=y)
    req_robo = RequisicaoRobo(id=1, function=MOVE_ROBOT_FUNCTION_NAME, positions=position)
    message =  Message(content=req_robo, reply_to=subscription)
    channel.publish(message, topic=TOPIC_TO_CONTROL_ROBOT)
    reply = channel.consume(timeout=1.0)

    sleep(1)

    logger.info("Getting Robot's location")
    position = Position(x=0, y=0)
    req_robo = RequisicaoRobo(id=1, function=LOCATE_ROBOT_FUNCTION_NAME, positions=position)
    message =  Message(content=req_robo, reply_to=subscription)
    channel.publish(message, topic=TOPIC_TO_CONTROL_ROBOT)
    reply = channel.consume(timeout=1.0)
    logger.info(f'{reply.status.why}')

    x += 1
    y += 1




