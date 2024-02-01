"""Parser module"""

from pathlib import Path
from edi_reader.exception.error import DataError,ConfigError
from edi_reader.logger import logger


class EDIParser():
    """Parser Class to handle file data
    """

    def __init__(self,configuration_singleton, file_path,
                 hierarchical_separator='\t', segment_terminator='\n',
                 element_separator='^', data_separator=">>"):
        # initialize line position in order to generate a file from database
        self.line_position = 0
        self.hierarchical_level = 0
        self.file_path = file_path
        self.hierarchical_separator = hierarchical_separator
        self.segment_terminator = segment_terminator
        self.element_separator = element_separator
        self.data_separator = data_separator
        self.conf = configuration_singleton

    def get_element_by_id_and_first_value(self,elements, target_id, target_first_value):
        """ Get element by id and first value

        Args:
            elements (List): List of elements
            target_id (string): id to search
            target_first_value (string): value to search

        Returns:
            object: Found element
        """
        for element in elements:
            if (element["id"] == target_id and element["first_value"] == target_first_value):
                return element
        return None

    def get_element_by_id(self,elements, target_id):
        """ Get element by id

        Args:
            elements (List): List of elements
            target_id (string): id to search

        Returns:
            object: Found element
        """
        for element in elements:
            if element["id"] == target_id:
                return element
        return None

    def get_segment_data(self,segment):
        """ Get segment data

        Args:
            segment (object): Segment

        Raises:
            DataError: Error with data input
            ConfigError: Error with input config

        Returns:
            object: Segment data
        """

        if segment:

            # Retrieve elements
            elements = segment.split(self.element_separator)

            # Get segment identifier
            segment_id = elements.pop(0)

            # Clean hierarchical_separator in segment_id to have a proper wording
            segment_id = segment_id.replace('\t','')

            # Get the first value to find it later in the model
            element_first_value = next((element for element in elements if element != ''), '')
            while elements and elements[0] == '':
                elements.pop(0)

            # Get Segment format
            model_format = self.get_element_by_id_and_first_value(self.conf.model,
                                                                  segment_id,
                                                                  element_first_value)

            # Handle footer and Begin case
            if (segment_id == "SE" or segment_id == "BPT"):
                model_format = self.get_element_by_id(self.conf.model,segment_id)


            # Get Segment entity
            if model_format:

                logger.debug(f"Segment found : id = {segment_id}")

                # Loop inside elements in the model in order to find details about fields
                for index, header_element in enumerate(model_format['elements']):

                    detail_element = self.get_element_by_id(self.conf.elements,header_element['id'])

                    if detail_element is not None:

                        if (index < len(elements)) and (elements[index] != '') :

                            # Validate length format of data as defined in specification
                            if (detail_element['length']['min'] <= len(elements[index])
                                and len(elements[index]) <= detail_element['length']['max']):

                                # Set field value to the datamodel
                                detail_element['value'] = elements[index]

                                if 'data' in detail_element:
                                    for i, data in enumerate(
                                        elements[index].split(self.data_separator)):

                                        detail_element['data'][i]['value'] = data

                                    model_format['elements'][index]['data'] = detail_element['data']

                                # Assign elements with new assigned value
                                model_format['elements'][index] = detail_element

                            else:
                                raise DataError(f"Wrong data : incorrect data length "
                                                f" element id : {detail_element['id']},"
                                                f" min : {detail_element['length']['min']},"
                                                f" max : {detail_element['length']['max']},"
                                                f" value : {elements[index]},")
                    else:
                        raise ConfigError(f"Wrong config : "
                                          f"Definition of element {header_element['id']} missing")

                return model_format
            else:
                raise DataError(f"Wrong data : "
                                f"impossible to find data with id = {segment_id} "
                                f"and value = {element_first_value}")

        else:
            raise DataError("Wrong segment data : impossible to find segment")

    def parse(self, callback):
        """Parse segments from a file

        Args:
            callback (function): User for each segment treated

        Returns:
            object: Object file description
        """

        parsed_data = []

        # initialize line position in order to generate a file from database
        self.line_position = 0

        with open(self.file_path, 'r', encoding="utf-8") as file:
            edi_data = file.read()

        segments = edi_data.split(self.segment_terminator)

        # Get segment data
        logger.debug('Segments processing')

        for segment in segments:

            if segment:

                # Get line position in file
                self.line_position +=1

                # Get Segment id
                segment_id = segment.split(self.element_separator)[0]

                # Count number of hierarchical_separator to get hierarchical level
                self.hierarchical_level = len(segment_id)-len(
                    segment_id.lstrip(self.hierarchical_separator))

                # Clean hierarchical_separator in segment_id to have a proper wording
                segment_id = segment_id.replace(self.hierarchical_separator,'')

                # Handle segment data
                segment_data = self.get_segment_data(segment)

                # Keep original text
                segment_data["text_value"] = segment

                # Keep line position in order to generate a file from database
                segment_data['line_position'] = self.line_position

                # Keep line position in order to know parents
                segment_data['hierarchical_level'] = self.hierarchical_level

                callback(EdiSegment(segment_id, segment_data, self.hierarchical_level))

                parsed_data.append(segment_data)

        return {"file_name" : Path(self.file_path).name, "content": parsed_data }

class EdiSegment:
    """Helper Class to represent segment
    """
    def __init__(self, segment_id, data, hierarchical_level):
        self.id = segment_id
        self.data = data
        self.hierarchical_level = hierarchical_level
