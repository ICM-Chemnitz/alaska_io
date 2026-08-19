from .alaska_xml_reader import parse_xml_file
from .alaska_xml_writer import write_xml

class AlaskaXmlFile:
    """
    simple class as alaska XML File wrapper.
    Holds parsed tables and variables and provides access utilities.
    Limitations: currently ignores hierarchy (Container)

    Attributes
    ----------
        filename : str | None
            filename of alaska xml parameter set file
        
        xml_tables : list[dict] 
            list of alaska xml tables stored as dicts

        xml_variables : list[dict] 
            list of alaska xml parameters stored as dicts

    """

    filename : str | None
    xml_tables : list[dict]
    xml_variables : list[dict]


    def __init__(self, filename : str = None, tables: list = None, variables : list = None) -> None:
        
        
        self.xml_tables = []
        self.xml_variables = []
        
        # read from file 
        if filename is not None:
            self.read(filename)
        
        # use passed data
        elif tables is not None or variables is not None:
            self.xml_tables    = tables
            self.xml_variables = variables
            self._build_index()   
            
        # create empty 
        else: 
            return 


    def _build_index(self) -> None:

        self._index_table = {
            t.get("Name"): t
            for t in self.xml_tables
            if "Name" in t
        }

        self._index_variable = {
            t.get("Name"): t
            for t in self.xml_variables
            if "Name" in t
        }

    def get_table(self, name: str) -> dict:
        """
        Return table by name or None.
        
        Parameters
        ----------
        name 
            name of table
        
        Returns
        -------
        : dict or None
        """
        return self._index_table.get(name)

    def get_variable(self, name: str) -> dict:
        """
        Return variable by name or None.
        
        Parameters
        ----------
        name 
            variable name
        
        Returns
        -------
        : dict or None
        """
        return self._index_variable.get(name)

    # -------------------------
    # convenience
    # -------------------------

    def names_table(self) -> list[str]:
        """
        get list of names of all xml tables
        
        Returns
        -------
        : list[str]
            list of names of all xml tables
        """
        return list(self._index_table.keys())

    def names_variable(self) -> list[str]:
        """
        get list of names of all xml variables
        
        Returns
        -------
        : list[str]
            list of names of all xml variables
        """
        return list(self._index_variable.keys())

    # -------------------------
    # read and write
    # -------------------------



    def read(self, filename : str) -> None:
        """
        read xml file from file
        
        Parameters
        ----------
        filename    
            name of parameter set file.
        """    
        tables , variables = parse_xml_file(file_path = filename, xml_text = None)
        
        self.xml_tables = tables
        self.xml_variables = variables
        self._build_index()        
        

    def read_from_str(self, str_file_content: str) -> None:
        """
        read xml file from string
        
        Parameters
        ----------
        str_file_content    
            file content in string
        """    
        tables, variables = parse_xml_file(file_path = None, xml_text = str_file_content)

        self.xml_tables = tables
        self.xml_variables = variables
        self._build_index()        
        

    def write(self, filename: str) -> None:
        """
        write xml file to file
        
        Parameters
        ----------
        filename    
            file content in string
        """    
        return write_xml(self.xml_tables, self.xml_variables, filename)
        
    def write_to_str(self) -> str:
        """
        write xml file to str
        
        Returns
        -------
         : str
            xml file content
        """
        return write_xml(self.xml_tables, self.xml_variables, filename = None)
        
    def add_real_variable(self, variable_name : str, value , unit : str = None) -> None:
        """
        add REAL xml variable to AlaskaXmlFile
        
        Parameters
        ----------
        variable_name
            name of variable
            
        value : float
            value of REAL variable
            
        unit : str , optional
            unit of REAL variable
        """
        variable = {
            'AttNames': ['name'],
            'AttContent': [variable_name],
            'Name': variable_name,
            'Content': str(value),
            'Type': 'REAL'
        }
        if unit is not None:
            variable['AttNames'].append('unit')
            variable['AttContent'].append(unit)
        self.xml_variables.append(variable)
        self._build_index()          

    def add_string_variable(self, variable_name : str , value : str) -> None:
        """
        add STRING xml variable to AlaskaXmlFile
        
        Parameters
        ----------
        variable_name
            name of variable
            
        value : str
            value of STRING variable
        """
        # put value in '...' if value contains space
        value = f"'{value}'" if " " in value else value
        self.xml_variables.append(
            {
                'AttNames': ['name'],
                'AttContent': [variable_name],
                'Name': variable_name,
                'Content': value,
                'Type': 'STRING'
                }
            )
        self._build_index()          

    def set_variable_value(self, variable_name : str, value) -> None:    
        """
        set xml variable value
        
        Parameters
        ----------
        variable_name
            name of variable
            
        value : str or float
            new value of variable
        """
        var = self.get_variable(variable_name) 
        var["Content"] = str(value)

