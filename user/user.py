# You'll always  have to import these components
from is_wire.core import Channel, Subscription, Message
from is_msgs.common_pb2 import Phrase
from RequisicaoRobo_pb2 import RequisicaoRobo
from loguru import logger
from time import sleep

channel = Channel("amqp://guest:guest@localhost:5672")
subscription = Subscription(channel)
subscription.subscribe(topic="User.Console")
phrase = Phrase()
phrase.content.extend("Ligar Sistema")
message = Message(content=phrase)

while True:
    channel.publish(message, topic="Controller.Console")
    logger.info("Mensagem enviada!")
    logger.info("Aguardando resposta do controlador...")
    received_message = channel.consume()
    logger.info("O Controlador respondeu!")
    received_struct = received_message.unpack(Phrase)
    phrase_content = received_struct.content
    phrase_content = ''.join(str(e) for e in phrase_content)
    if phrase_content == "Sistema Ligado":
        logger.info("O sistema foi ligado!")
        logger.info("#TODO: Enviar mensagem para o robô...")
        break
    logger.info("O sistema não foi ligado.")
    logger.info("Mensagem recebida: {}".format(phrase_content))
    logger.info("Tentando novamente em 2 segundo...")
    sleep(2)