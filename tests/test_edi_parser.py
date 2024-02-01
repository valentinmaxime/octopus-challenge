"""Test module"""

import pytest

from edi_reader import main
from edi_reader.exception.error import ConfigError, DataError, FileError
from edi_reader.logger import logger
from edi_reader.database import Database
from edi_reader.conf.edi_config import EDIConf
from edi_reader.edi_parser import EDIParser
from edi_reader.logger import configure_logging

configure_logging()

@pytest.fixture(scope="session",name="configuration_singleton")
def config_singleton(request):
    """Singleton fixture to provide a single configuration instance for all tests."""
    if not hasattr(request.session, "configuration_singleton"):
        # EDIConf is a class that loads configuration from a json file
        config = EDIConf.load_conf_model_from_file("tests\\input\\conf")
        request.session.configuration_singleton = config
    return request.session.configuration_singleton

@pytest.fixture(scope="session",name="wrong_configuration_singleton")
def wrong_config_singleton(request):
    """Singleton fixture to provide a single configuration instance for all tests."""
    if not hasattr(request.session, "wrong_configuration_singleton"):
        # EDIConf is a class that loads configuration from a json file
        config = EDIConf.load_conf_model_from_file("tests\\input\\wrong_conf")
        request.session.wrong_configuration_singleton = config
    return request.session.wrong_configuration_singleton


@pytest.fixture(scope='module',name="setup_database")
def setup_db():
    """Setup Database

    Returns:
        Object: Database Instance
    """
    return Database()

def test_bad_conf():
    """Folder and path verification
    """
    with pytest.raises(FileNotFoundError):
        main.main(['edi_reader\\conf\\cozefzefnf_mode','tests\\input\\input\\867_02_ex_01.edi'])

def test_bad_edi_file_or_folder():
    """Folder and path verification
    """
    with pytest.raises(FileError):
        main.main(['tests\\input\\conf','edi_reader\\input\\867_02_ex_01'])

def test_bad_edi_nothing_in_folder():
    """Folder and path verification
    """
    with pytest.raises(FileError) as exc_info:
        main.main(['tests\\input\\conf','edi_reader\\exception'])
    assert "does not contain any .edi files" in str(exc_info.value)


def test_parse_a_file(configuration_singleton):
    """File parsing / format verification - Test case for the EDI parser

    Args:
        configuration_singleton (Fixture): instanciated configuration
    """
    edi_file_path = 'tests\\input\\input\\867_02_ex_01.edi'
    parser = EDIParser(configuration_singleton,edi_file_path,
                       segment_terminator='\n', element_separator='~')
    parser.parse(handle_segment)

def test_incorrect_length(configuration_singleton):
    """File parsing / format verification - Test case with incorrect data length

    Args:
        configuration_singleton (Fixture): instanciated configuration
    """
    edi_file_path = 'tests\\input\\input\\incorrect_length.edi'
    with pytest.raises(DataError) as exc_info:
        parser = EDIParser(configuration_singleton,edi_file_path,
                            segment_terminator='\n', element_separator='~')
        parser.parse(handle_segment)
    assert " incorrect data length" in str(exc_info.value)

def test_bad_id_value(configuration_singleton):
    """File parsing / format verification - Test case with incorrect id/value couple

    Args:
        configuration_singleton (Fixture): instanciated configuration
    """
    edi_file_path = 'tests\\input\\input\\bad_id.edi'
    with pytest.raises(DataError) as exc_info:
        parser = EDIParser(configuration_singleton,edi_file_path,
                            segment_terminator='\n', element_separator='~')
        parser.parse(handle_segment)
    assert "impossible to find data with id" in str(exc_info.value)

def test_bad_model_conf(wrong_configuration_singleton):
    """File parsing / format verification - Test case with incorrect model
    Args:
        configuration_singleton (Fixture): instanciated configuration
    """
    edi_file_path = 'tests\\input\\input\\867_02_ex_01.edi'
    with pytest.raises(ConfigError) as exc_info:
        parser = EDIParser(wrong_configuration_singleton,edi_file_path,
                           segment_terminator='\n', element_separator='~')
        parser.parse(handle_segment)
    assert "Wrong config : Definition of element " in str(exc_info.value)

def test_database(setup_database):
    """Database Check

    Args:
        setup_database (fixture): database singleton
    """
    setup_database.create_table()

def test_database_insertion(configuration_singleton,setup_database):
    """Database insertion Check

    Args:
        configuration_singleton (fixture): configuration singleton
        setup_database (fixture): database singleton
    """
    setup_database.create_table()
    edi_file_path = 'tests\\input\\input\\867_02_ex_02.edi'
    parser = EDIParser(configuration_singleton,edi_file_path,
                        segment_terminator='\n', element_separator='~')
    data = parser.parse(handle_segment)
    setup_database.insert_data(data)
    setup_database.display_table()
    setup_database.save_database()
    setup_database.close()


def handle_segment(segment):
    """helper to pretty print info

    Args:
        segment (object): segment
    """
    logger.info(f"Level: {segment.hierarchical_level}, "
                f"Segment ID: {segment.id}, "
                f"Data: {segment.data['text_value']}\n --------------------------------")
