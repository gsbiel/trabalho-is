# You'll always  have to import these components
from is_wire.core import Channel, Subscription, Message, StatusCode
from is_msgs.common_pb2 import Phrase, Position 
from RequisicaoRobo_pb2 import RequisicaoRobo
from google.protobuf.empty_pb2 import Empty
from loguru import logger
from time import sleep
import socket

channel = Channel("amqp://guest:guest@localhost:5672")
subscription = Subscription(channel)

phrase = Phrase()
phrase.content.extend("Ligar Sistema")
message = Message(content=phrase, reply_to=subscription)

while True:
    logger.info("Starting the Controller")
    channel.publish(message, topic="Controller.Console")
    reply = channel.consume(timeout=1.0)
    if reply.status.code == StatusCode.OK:
        logger.info("The Controller is up and running!")
        break
    else:
        logger.info("The controller failled to start. Trying again in 2 seconds...")
        sleep(2)

x = 2
y = 3

while True:

    logger.info(f'Moving Robot to ({x},{y}) ')
    position = Position(x=x, y=y)
    req_robo = RequisicaoRobo(id=1, function="move_robot", positions=position)
    message =  Message(content=req_robo, reply_to=subscription)
    channel.publish(message, topic="Requisicao.Robo")
    reply = channel.consume(timeout=1.0)

    sleep(1)

    logger.info("Getting Robot's location")
    position = Position(x=0, y=0)
    req_robo = RequisicaoRobo(id=1, function="get_position", positions=position)
    message =  Message(content=req_robo, reply_to=subscription)
    channel.publish(message, topic="Requisicao.Robo")
    reply = channel.consume(timeout=1.0)
    logger.info(f'{reply.status.why}')

    x += 1
    y += 1




