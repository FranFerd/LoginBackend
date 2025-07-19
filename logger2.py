import logging

logging.basicConfig(level=logging.INFO, filename='log.log', filemode='w',
                    format="%(asctime)s - %(levelname)s - %(message)s") 
# Log messages with severity level of INFO and beyound (No debug)
# Put all messages in file 'log.log' and overwrite it every time ('w')

logging.debug('debug')
logging.info('info')
logging.warning('warning')
logging.error('error')
logging.critical('critical')

logger = logging.getLogger(__name__)

handler = logging.FileHandler('test.log', 'w')
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info('test the custom logger')