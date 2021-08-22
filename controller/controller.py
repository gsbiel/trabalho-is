from is_wire.core import Channel, Subscription, Message
from is_wire.rpc import ServiceProvider
from is_msgs.common_pb2 import Phrase
from google.protobuf.empty_pb2 import Empty
from loguru import logger
from time import sleep
from random import randint

def turn_on_system():
    number = randint(0,100)
    if number >=90:
        return True
    else:
        return False
    
def create_message(text):
    phrase = Phrase()
    phrase.content.extend(text)
    message = Message(content=phrase)
    return message

channel = Channel("amqp://guest:guest@localhost:5672")
subscription = Subscription(channel)
subscription.subscribe(topic="Controller.Console")

while True:
    logger.info("Waiting for messages...")
    received_message = channel.consume()
    received_struct = received_message.unpack(Phrase)
    phrase_content = received_struct.content
    phrase_content = ''.join(str(e) for e in phrase_content)
    logger.info("Message received: {}".format(phrase_content))
    if phrase_content == "Ligar Sistema":
        logger.info("Trying to turn the Controller on...")
        if turn_on_system():
            logger.info("The controller is now up and running!")
            message = create_message("Sistema Ligado")
            channel.publish(message, topic="User.Console")
            break
        else:
            logger.warning("The controller failed to start...")
            message = create_message("Sistema Desligado")
            channel.publish(message, topic="User.Console")
