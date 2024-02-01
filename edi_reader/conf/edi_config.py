""" Configuration module """
import json
import os
from edi_reader.exception.error import ConfigError

class EDIConf:
    """Configuration class
    """

    def __init__(self, header, model, elements):
        self.header = header
        self.model = model
        self.elements = elements


    @classmethod
    def load_conf_model_from_file(cls, folder_path):
        """ Load configuration models from afile

        Args:
            folder_path (string): folder path

        Raises:
            ConfigError: Wrong or missing Model files

        Returns:
            object: configuration model
        """
        header = None
        model = None
        elements = None
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                if "model" in filename:
                    with open(os.path.join(folder_path, filename),
                              'r',encoding="utf-8") as format_file:
                        model = json.load(format_file)
                elif "elements" in filename:
                    with open(os.path.join(folder_path, filename),
                              'r', encoding="utf-8") as format_file:
                        elements = json.load(format_file)
        if model and elements :
            return cls(header, model, elements)
        else:
            raise ConfigError("Wrong Model files, model or elements")
