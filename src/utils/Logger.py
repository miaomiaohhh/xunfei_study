import logging

# 配置日志记录
logging.basicConfig(level=logging.DEBUG,
                    format='ilp:%(asctime)s - %(levelname)s - %(message)s')

# 创建日志记录器
logger = logging.getLogger(__name__)

def debug(message):
    logger.debug(message)
    
def info(message):
    logger.info(message)
    
def warning(message):
    logger.warning(message)

def error(message):
    logger.error(message)
    
def critical(message):
    logger.critical(message)
