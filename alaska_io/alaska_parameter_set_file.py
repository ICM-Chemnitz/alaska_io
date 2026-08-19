
from . import alaska_xml_helper

from .alaska_xml_reader import parse_xml_table_str
from .alaska_xml_writer import write_parameter_set_file

class AlaskaParameterSetFile:
    """
    alaska Parameter Set File wrapper.
    Holds parameter set tables as a list of dict and provides access utilities.
    Parameter set file contains parameter set tables, which store parameter data sets (as lines over all tables)
    
    Attributes
    ----------
        filename : str | None
            filename of alaska xml parameter set file
        
        tables : list[dict] 
            list of parameter set tables stored as dicts

    """

    filename : str | None
    tables : list[dict]

    def __init__(self, filename : str = None, tables : list = None) -> None:
    
        self.tables = []
        self.filename = None
        
        # read from file 
        if filename is not None:
            self.read(filename)
            self.filename = filename
        
        # use passed data
        elif tables is not None:
            self.tables = tables
            self._build_index()
        
        # create empty
        else:
            return

    def _build_index(self) -> None:

        self._index = {
            t.get("Name"): t
            for t in self.tables
            if "Name" in t
        }


    # -------------------------
    # basic access
    # -------------------------

    def __len__(self) -> int:
        return len(self.tables)

    def __getitem__(self, idx: int) :
        return self.tables[idx]

    # -------------------------
    # name-based access
    # -------------------------

    def get(self, name : str) -> dict:
        """Return parameter set table by name or None.

        Parameters
        ----------
        name    
            name of table.
            
        Returns
        -------
        dict
            table with name 'name' or None
        """
        
        return self._index.get(name)

    def get_index(self, name : str) -> int:
        """
        get parameter set table index by name
        
        Parameters
        ----------
        name    
            name of table.
            
        Returns
        -------
        int
            index of table or None if table not found
        """
        
        for i, t in enumerate(self.tables):
            if t.get("Name") == name:
                return i
        return None

    # -------------------------
    # convenience
    # -------------------------

    def names(self) -> list:
        """
        get list of names of all parameter set tables
        
        Returns
        -------
        list[str]
            list of names of all parameter set tables
        """

        return list(self._index.keys())


    # -------------------------
    # read and write
    # -------------------------

    def read(self, filename: str) -> None:
        """
        read parameter set file from file
        
        Parameters
        ----------
        filename    
            name of parameter set file.
        """    
        
        other = read_parameter_set_file(filename, precision = 8)
        if other.tables is not None:
            self.filename = filename
            self.tables = other.tables
            self._build_index()
        

    def write(self, filename: str = None) -> None:
        """
        writes parameter set file to alaska xml file
        
        Parameters
        ----------
        filename    
            file name of parameter set file, if 'None' original file name of parameter set file is used (AlaskaParameterSetFile.filename).
        """    
    
        if filename is None:
            write_parameter_set_file(self.filename, self)
        else: 
            write_parameter_set_file(filename, self)

    # -------------------------
    # consistency check 
    # -------------------------

    def validate(self, verbose=True) -> None:
        return validate(self, verbose)

    # -------------------------
    # parameter data set manipulation
    # -------------------------

    def get_parameter_data_set_by_id(self, id_value: str = None):
        """
        Extract one parameter dataset (row across all tables) by ID.
    
        Parameters
        ----------
        id_value 
            ID of the dataset. If empty string, first dataset is returned.
    
        Returns
        -------
        tuple
            (PDS, row_id)
            PDS: list of row data per table
            row_id: 0-based index , 0 if not found
        """
        return alaska_xml_helper.get_parameter_data_set_by_id(self, id_value)

    def add_parameter_data_set( self, parameter_data_set, newname : str = None) -> None:
        """
        Add a parameter dataset (row across all tables) to parameter_set_file.
    
        Parameters
        ----------
        parameter_data_set : list
            One dataset (list of rows per table).
            
        newname : str, optional
            New ID for the dataset.
    
        """
        alaska_xml_helper.add_parameter_data_set(self, parameter_data_set, newname)

    def delete_all_parameter_data_sets(self) -> None:
        """
        Delete all parameter datasets (rows) from parameter_set_file.
        Keeps table structure (attributes).
    
        """
        alaska_xml_helper.delete_all_parameter_data_set(self)

    # -------------------------
    # table manipulation
    # -------------------------

    def append_table(self, table_name : str) -> None:
        """
        Add a new table (parameter set table) to parameter_set_file.
    
        Parameters
        ----------
        table_name : str
            name of new table
        """
    
        alaska_xml_helper.append_parameter_set_table(self, table_name)
        self._build_index()

    
    # -------------------------
    # variable manipulation
    # -------------------------

    def get_variable_names(self):
        """
        get variable names of all variables in all parameter set tables in parameter set file 
        function will remove duplicate entries of parameter set ID (or Lc_ID for loadcases)
    
    
        Returns
        -------
        : list[str]
            list of variables names
        """
        return alaska_xml_helper.get_variable_names(self)
    
    def find_variable(self, variable_name: str):
        """
        Find parameter set variable (column) in parameter_set_file tables.
    
        Parameters
        ----------
        variable_name
            name of variable
    
        Returns
        -------
        tuple (table_ind, column_ind) 
            index of table containing variable and index of column of variable in corresponding table
        """
        return alaska_xml_helper.find_parameter_set_variable(self, variable_name)
        

    def delete_variable(self, variable_name: str) -> None:
        """
        Delete a variable (column) from parameter set file
    
        Parameters
        ----------
        variable_name
            name of variable to be deleted from parameter set file
        """
        alaska_xml_helper.delete_parameter_set_variable(self, variable_name)        
        
    def add_variable(self, table_name, variable_name, data_column = None, variable_type : str = "STRING", unit : str = "-") -> None:
        """
        Add a parameter set variable (column) to specific parameter set table.
    
        Parameters
        ----------
        table_name : str
            name of table

        variable_name : str
            Name of new variable
            
        data_column : list, optional
            Column data (length must match number of rows in parameter set file)
            
        variable_type : str , optional
            Variable type (STRING, REAL, INT), default STRING
            
        unit : str , optional
            Unit of variable ("-" if None)
        """
        alaska_xml_helper.add_parameter_set_variable(self, table_name, variable_name, data_column, variable_type, unit)        

    def add_select_variable(self, table_name, variable_name, data_column = None, switches : str = "") -> None:
        """
        Add a parameter set variable (column) to specific parameter set table.
    
        Parameters
        ----------
        table_name : str
            name of table

        variable_name : str
            Name of new variable
            
        data_column : list, optional
            Column data (length must match number of rows in parameter set file)
            
        switches : str
            switches of the SELECT variable, must be separated by "/" , and passed as one str: eg: switches = "ON/OFF"       
        """
        alaska_xml_helper.add_parameter_set_select_variable(self, table_name, variable_name, data_column, switches)        

    def set_variable_value(self, variable_name : str, variable_value, parameter_data_set_id : str = None) -> None:
        """
        Set value of a variable in a specific parameter dataset.
        - If parameter_data_set_id is None and variable_value is scalar , the variable is changed in the first parameter data set (top-row of each table)
        - If parameter_data_set_id is None and variable_value is not scalar, the values will be put in variable column (if len() does match)
        
        Parameters
        ----------
        variable_name 
            Variable name (column)
    
        variable_value : any
            New value (will be written as string)
        
        parameter_data_set_id : str , optional
            ID of parameter dataset (corresponds to specific row in all parameter set tables)
        """
        alaska_xml_helper.set_parameter_data_set_variable_value(self, variable_name, variable_value, parameter_data_set_id)

    def get_variable(self, variable_name : str, parameter_data_set_id : str = None):
        """
        Set value of a variable in a specific parameter dataset.
        if parameter_data_set_id is None, the full columns of the parameter set variable is retrieved
    
        Parameters
        ----------
        variable_name 
            Variable name (column)
    
        parameter_data_set_id : str , optional
            ID of parameter dataset (corresponds to specific row in all parameter set tables) or None 
    
        Returns
        -------
        str or numpy.ndarray[str]
        """
        return alaska_xml_helper.get_parameter_data_set_variable(self, variable_name, parameter_data_set_id)


        
        
def validate(parameter_set_file : AlaskaParameterSetFile, verbose = True) -> bool:
    """
    Validate AlaskaParameterSetFile consistency.

    Parameters
    ----------
    parameter_set_file
        parameter set file to be validated

    Returns
    -------
    bool
        True if valid, False otherwise
    """

    ok = True

    if not parameter_set_file.tables:
        print("Parameter set file is empty")
        return False

    # --- reference row count
    ref_rows = int(parameter_set_file.tables[0]["no_rows"])

    for ti, table in enumerate(parameter_set_file.tables):

        name = table.get("Name", f"Table_{ti}")

        try:
            no_rows = int(table["no_rows"])
            no_cols = int(table["no_cols"])
            no_cells = int(table["no_cells"])
        except Exception:
            print(f"[{name}] invalid numeric fields")
            ok = False
            continue

        content = table["Content"]

        # --- check shape
        if content.shape != (no_rows, no_cols):
            print(f"[{name}] Content shape mismatch: {content.shape} vs ({no_rows},{no_cols})")
            ok = False

        # --- check cells
        if no_rows * no_cols != no_cells:
            print(f"[{name}] no_cells mismatch")
            ok = False

        # --- check head
        head = None
        for n, v in zip(table["AttNames"], table["AttContent"]):
            if n == "head":
                head = v
                break

        if head:
            heads = head.replace("'", "").strip().split()
            if len(heads) != no_cols:
                print(f"[{name}] head length mismatch")
                ok = False

        # --- check row consistency across tables
        if no_rows != ref_rows:
            print(f"[{name}] row count differs from first table")
            ok = False

    if verbose:
        if ok:
            print("AlaskaParameterSetFile validation: OK")
        else:
            print("AlaskaParameterSetFile validation: FAILED")

    return ok

    
def read_parameter_set_file(filename: str, precision: int = 8) -> AlaskaParameterSetFile:
    """
    Read parameter set file and extract all tables.
    
    Parameters
    ----------
    filename 
        file name of parameter set file
        
    precision 
        number of digits for number-string conversion
        
    Returns
    -------
    AlaskaParameterSetFile 
        list of tables of parameter set file 
    """

    parameter_set_file = []

    try:
        with open(filename, "r", encoding="iso-8859-1") as f:
            
            print(f"Reading parameter set file with file name {filename}.")        
            
            line = f.readline()
                
            while line and "</IFM:data>" not in line:

                if "<TABLE" in line:
                    pt = line

                    while "</TABLE>" not in line:
                        line = f.readline()
                        if not line:
                            break
                        pt += line

                    parameter_set_file.append(parse_xml_table_str(pt, precision))

                line = f.readline()

    except FileNotFoundError:
        print(f"ParameterSet file: {filename} can not be found!")
        return AlaskaParameterSetFile(None)

    return AlaskaParameterSetFile(  tables = parameter_set_file)
