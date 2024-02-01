"""Logging module"""

import logging
import coloredlogs

logger = logging.getLogger(__name__)
logger.propagate = False

def configure_logging():
    """Color configuration
    """

    # Define a custom color map
    custom_color_map = {
        'critical': {'bold': True, 'color': 'red'}, 
        'debug': {'color': 'cyan'}, 
        'error': {'color': 'red'}, 
        'info': {'color': 'green'}, 
        'notice': {'color': 'magenta'}, 
        'spam': {'color': 'green', 'faint': True}, 
        'success': {'bold': True, 'color': 'green'}, 
        'verbose': {'color': 'blue'}, 
        'warning': {'color': 'yellow'}}

    field_styles={
        'asctime': {'color': 'white'}, 
        'levelname':  {'color': 'white'}, 
        'name':  {'color': 'white'}
    }

    # Create a file handler and set the formatter
    file_handler = logging.FileHandler("log_file.log")
    # Adjust the logging level as needed
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Configure the root logger with colored output
    coloredlogs.install(
        logger=logger,
        # Adjust the logging level as needed
        level='DEBUG',
        fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level_styles=custom_color_map,
        field_styles = field_styles
    )

configure_logging()
