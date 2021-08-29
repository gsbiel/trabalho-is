from is_wire.rpc import ServiceProvider, LogInterceptor
from is_wire.core import Channel, StatusCode, Status
from google.protobuf.empty_pb2 import Empty
from is_msgs.common_pb2 import Position
import time
from loguru import logger
import os
import json

class Robot():
    def init(self,id,x,y):
        self.id = id
        self.pos_x = x
        self.pos_y = y
        
    def get_id(self):
        return self.id

    def set_position(self,x,y):
        self.pos_x = x
        self.pos_y = y

    def get_position(self):
        return self.pos_x,self.pos_y

def read_configuration(config_path):
  with open(config_path) as f:
    return json.load(f)

def get_position(Empty, ctx):
    logger.info("get_position() has been called.")
    position = Position()
    position.x, position.y = robot.get_position()
    return position

def set_position(Position, ctx):
    logger.info("set_position has been called.")
    if Position.x < 0 or Position.y < 0:
        return Status(StatusCode.OUT_OF_RANGE, "The number must be positive")

    robot.set_position(x=Position.x, y=Position.y)
    return Empty()

config_path = os.getenv('CONFIG_PATH', './conf/config.json')
configs = read_configuration(config_path)

AMQ_HOST = os.getenv('AMQ_HOST', configs["amq_host"])
TOPIC_TO_CONTROL_ROBOT = os.getenv('TOPIC_TO_CONTROL_ROBOT', configs["topic_to_control_the_robot"])
TOPIC_TO_LOCATE_ROBOT = os.getenv('TOPIC_TO_LOCATE_ROBOT', configs["topic_to_locate_the_robot"]) 
START_ROBOT_POSITION_X = os.getenv('START_ROBOT_POSITION_X', configs["start_robot_in_position_x"]) 
START_ROBOT_POSITION_Y = os.getenv('START_ROBOT_POSITION_Y', configs["start_robot_in_position_y"])

logger.info("Configuration:")
logger.info(f'AMQ_HOST: {AMQ_HOST}')
logger.info(f'TOPIC_TO_CONTROL_ROBOT: {TOPIC_TO_CONTROL_ROBOT}')
logger.info(f'TOPIC_TO_LOCATE_ROBOT: {TOPIC_TO_LOCATE_ROBOT}')
logger.info(f'START_ROBOT_POSITION_X: {START_ROBOT_POSITION_X}')
logger.info(f'START_ROBOT_POSITION_Y: {START_ROBOT_POSITION_Y}')

robot = Robot() 
robot.id = 1
robot.pos_x = START_ROBOT_POSITION_X
robot.pos_y = START_ROBOT_POSITION_Y

channel = Channel(AMQ_HOST)
provider = ServiceProvider(channel)

# Os tipos das mensagens devem ser passados, tanto no request como no reply
provider.delegate(
    topic=TOPIC_TO_LOCATE_ROBOT,
    function=get_position,
    request_type=Empty,
    reply_type=Position) 

provider.delegate(
    topic=TOPIC_TO_CONTROL_ROBOT,
    function=set_position,
    request_type=Position,
    reply_type=Empty)

provider.run()