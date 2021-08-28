from __future__ import print_function
from is_wire.core import Channel, Subscription, Message,  StatusCode, Status
from is_wire.rpc import ServiceProvider, LogInterceptor
from is_msgs.common_pb2 import Phrase, Position 
from google.protobuf.empty_pb2 import Empty
from loguru import logger
from time import sleep
from random import randint
from RequisicaoRobo_pb2 import RequisicaoRobo

channel = Channel("amqp://guest:guest@localhost:5672")
subscription = Subscription(channel)

def turn_on_system():
    number = randint(0,100)
    if number >=50:
        return True
    else:
        return False
    
def create_message(text):
    phrase = Phrase()
    phrase.content.extend(text)
    return phrase

def start_system(*args):
    logger.info("Trying to start the controller...")
    if turn_on_system():
        logger.info("Controller started successfuly!")
        return Status(StatusCode.OK, "System up and running!")
    else:
        logger.warning("Controller failled to start...")
        return Status(StatusCode.INTERNAL_ERROR, "The process failed due to an internal crash.")

def execute_function(*args):

    if args[0].function == "move_robot":
        logger.info("Got a request to move the robot.")
        position = Position(x=args[0].positions.x, y=args[0].positions.y)
        req_robo = Message(content=position, reply_to=subscription)
        logger.info("Sending request to the Robot...")
        channel.publish(req_robo, topic="Control.Robot")
        logger.info("Waiting for an answer from the robot")
        reply = channel.consume(timeout=1.0)
        if reply.status.code == StatusCode.OK:
            return Status(StatusCode.OK, f'The robot changed its position.')
        else:
            return Status(StatusCode.INTERNAL_ERROR, f'The robot failed to move. Reason:{reply.status.why}')

    elif args[0].function == "get_position":
        logger.info("Got a request to locate the robot.")
        logger.info("Sending request to the Robot...")
        empty = Empty()
        req_robo = Message(content=empty, reply_to=subscription)
        channel.publish(req_robo, topic="Locate.Robot")
        logger.info("Waiting for an answer from the robot")
        reply = channel.consume(timeout=1.0)
        position = reply.unpack(Position)
        return Status(StatusCode.OK, f'The robot is located at: ({position.x}, {position.y}).')

    else:
        return Status(StatusCode.UNIMPLEMENTED, "This function is not implemented.")

provider = ServiceProvider(channel)

provider.delegate(
    topic="Controller.Console",
    function=start_system,
    request_type=Phrase,
    reply_type=Empty) 

provider.delegate(
    topic="Requisicao.Robo",
    function=execute_function,
    request_type=RequisicaoRobo,
    reply_type=Empty)

logger.info("Provider is running and waiting for messages...")
provider.run()