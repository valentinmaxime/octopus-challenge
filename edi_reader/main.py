"""Main module"""

import argparse
import json
import os
from edi_reader.conf.edi_config import EDIConf
from edi_reader.exception.error import FileError
from edi_reader.logger import logger
from edi_reader.edi_parser import EDIParser
from edi_reader.database import Database


def main(argv=None):
    """Main function

    Args:
        argv (File, optional): Defaults to None.

    Raises:
        FileError: Wrong parameters
    """
    logger.info('Starting the application')

    parser = argparse.ArgumentParser(description="Parse and store EDI 867_02 data in a database.")
    parser.add_argument("edi_config", help="EDI config folder")
    parser.add_argument("file_or_folder_path",
                        help="Path to the EDI file or directory containing files.")

    args,_ = parser.parse_known_args(argv)
    config = args.edi_config
    path = args.file_or_folder_path

    # Load configuration files
    config = EDIConf.load_conf_model_from_file(args.edi_config)

    # Check if the argument is a file
    if os.path.isfile(path):
        logger.info(f"{path} is a file. -- Processing file")
        # Use process_file function to handle file parsing
        data = process_file(config,path)
        save_data(data)
    # Check if the argument is a folder
    elif os.path.isdir(path):
        logger.info(f"{path} is a directory. -- Processing files")
        number_edi_files = 0
        # Take only files with edi extension
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(".edi"):
                logger.info(f"Processing file : {file_name}")
                number_edi_files+=1
                data = process_file(config,file_path)
                save_data(data)
        if number_edi_files == 0:
            raise FileError(f"{path} does not contain any .edi files")
    else:
        raise FileError(f"{path} is not a valid file or directory")

    logger.info('Shutting down the application')

def process_file(config,path):
    """File processing

    Args:
        config (object): configuration singleton
        path (string): file path

    Returns:
        object: data with segments and detail
    """
    edi_parser = EDIParser(config,path,segment_terminator='\n', element_separator='~')
    data = edi_parser.parse(handle_segment)
    return data

def save_data(data):
    """Save data into database

    Args:
        data (object): file object description
    """
    db = Database()
    db.insert_data(data)
    db.save_database()
    db.close()

def handle_segment(segment):
    """helper to pretty print info

    Args:
        segment (object): segment
    """
    logger.info(f"Level: {segment.hierarchical_level}, "
                f"Segment ID: {segment.id}, "
                f"Text: {segment.data['text_value']},\n "
                f"Data : {json.dumps(segment.data, indent=4)}"
                f"\n --------------------------------")

if __name__ == "__main__":
    main()
