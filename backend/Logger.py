import os
import yaml
import logging
import logging.handlers as handler
import datetime

class CustomTimedRotatingFileHandler(handler.TimedRotatingFileHandler):
    def __init__(self, base_log_path, when="midnight", interval=1, backupCount=30):
        self.base_log_path = base_log_path
        super().__init__(self._get_log_file(), when, interval, backupCount)
    
    def _get_log_file(self):
        current_time = datetime.datetime.now()
        month_folder = current_time.strftime("%b")
        log_dir = os.path.join(self.base_log_path, month_folder)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, current_time.strftime("%d-%m-%Y.log"))
        return log_file

    def doRollover(self):
        self.baseFilename = self._get_log_file()
        super().doRollover()

class Logger:
    
    def __init__(self) -> None:
        with open(os.path.join("PATH_TO_YAML_FILE", "paths.yaml"), "r") as file:
            content = yaml.safe_load(file)
            
        # Access specific paths
        self.base_log_path = content["log"]["base"]
        
        # Set up logger
        self.setup_logger()
        
    def setup_logger(self):
        logger = logging.getLogger("debug_logger")
        logger.setLevel(logging.DEBUG)
        
        # Define a CustomTimedRotatingFileHandler
        handler = CustomTimedRotatingFileHandler(
            self.base_log_path, when="midnight", interval=1, backupCount=30
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
        
        # Setup werkzeug to use this logger
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.INFO)
        werkzeug_logger.addHandler(handler)
    
    def get_logger(self):
        return logging.getLogger("debug_logger")

    def log_debug(self, message):
        logger = self.get_logger()
        logger.debug(message)