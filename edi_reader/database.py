"""Database module"""
import sqlite3
from edi_reader.logger import logger

class Database:
    """Database class to represent EDI files
    """

    def __init__(self, db_path=":memory:"):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """sqlite 3 Table creation
        """

        logger.debug("Creation of sqlite tables")

        # database table creation SQL
        sql_create_table_file =  f'''
        CREATE TABLE IF NOT EXISTS FILE (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        '''

        sql_create_table_element =  f'''
        CREATE TABLE IF NOT EXISTS SEGMENT (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            req TEXT NOT NULL,
            max_uses INTEGER NOT NULL,
            notes TEXT,
            hierarchical_level INTEGER NOT NULL,
            file_id INTEGER,  -- Foreign key column referencing FILE.id
            FOREIGN KEY (file_id) REFERENCES FILE(id)
        )
        '''

        sql_create_table_element_detail = f'''
        CREATE TABLE IF NOT EXISTS ELEMENT_DETAIL (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            req TEXT NOT NULL,
            data_type TEXT NOT NULL,
            length_min INTEGER NOT NULL,
            length_max INTEGER NOT NULL,
            segment_id INTEGER,  -- Foreign key column referencing SEGMENT.id
            FOREIGN KEY (segment_id) REFERENCES SEGMENT(id)
        )
        '''

        sql_create_table_element_data = f'''
        CREATE TABLE IF NOT EXISTS ELEMENT_DATA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            req TEXT NOT NULL,
            data_type TEXT NOT NULL,
            length_min INTEGER NOT NULL,
            length_max INTEGER NOT NULL,
            element_detail_id INTEGER,  -- Foreign key column referencing ELEMENT_DETAIL.id
            FOREIGN KEY (element_detail_id) REFERENCES ELEMENT_DETAIL(id)
        )
        '''

        self.cursor.execute(sql_create_table_file)
        self.cursor.execute(sql_create_table_element)
        self.cursor.execute(sql_create_table_element_detail)
        self.cursor.execute(sql_create_table_element_data)

        self.connection.commit()


    def insert_data(self, data):
        """Insert data in database

        Args:
            data (object): Object file description
        """


        # logic to insert data into the database
        logger.debug("Insert data in database")

        # Insert the filename into the FILE table
        self.cursor.execute("INSERT INTO FILE (name) VALUES (?)", (data['file_name'],))

        # Get the ID of the last inserted row
        file_id = self.cursor.lastrowid

        for segment in data['content']:

            # Insert the element data into the SEGMENT table
            self.cursor.execute("""
                INSERT INTO SEGMENT (type, name, req, max_uses, notes,hierarchical_level, file_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (segment['type'], segment['name'], segment['req'],
                segment['max_uses'], segment.get('notes', ''),segment.get('hierarchical_level', ''),
                segment.get('file_id', file_id)))

            segment_id = self.cursor.lastrowid

            for element_detail in segment['elements']:

                if 'data_type' not in element_detail:
                    continue

                # Insert the element detail data into the ELEMENT_DETAIL table
                self.cursor.execute("""
                    INSERT INTO ELEMENT_DETAIL (type, name, req, data_type, length_min, length_max, segment_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (element_detail['data_type'], element_detail['name'], element_detail['req'],
                    element_detail['data_type'], element_detail['length']['min'],
                    element_detail['length']['max'], element_detail.get('segment_id', segment_id)))

                element_detail_id = self.cursor.lastrowid

                if 'data' in element_detail:
                    for element_data in element_detail['data']:
                        self.cursor.execute("""
                        INSERT INTO ELEMENT_DATA (type, name, req, data_type, length_min, length_max, element_detail_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (element_data['type'], element_data['name'], element_data['req'],
                        element_data['data_type'], element_data['length']['min'],
                        element_data['length']['max'], element_data.get('element_detail_id', element_detail_id)))

        self.connection.commit()

    def display_table(self):
        """ Print SEGMENT database table
        """
        logger.debug("display segment table")
        # Query the data and display it
        self.cursor.execute('SELECT * FROM SEGMENT')
        result = self.cursor.fetchall()

        # Print the result
        for row in result:
            print(row)

    def save_database(self):
        """ Save database with backup function
        """
        # Save the in-memory database to a file using backup
        logger.debug("Backup database into database_dump.db")
        with sqlite3.connect('database_dump.db') as file_conn:
            self.connection.backup(file_conn)

    def close(self):
        """Close database
        """
        logger.debug("Close database")
        self.connection.commit()
        self.connection.close()
