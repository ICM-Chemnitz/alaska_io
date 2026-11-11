import numpy as np
import re

def parse_attribute_dict(attributes: str) -> dict:
    """
    Parse XML-like attribute string into a dictionary.
    """
    result = {}

    parts = attributes.split('"')

    for i in range(1, len(parts), 2):
        value = parts[i]
        prefix = parts[i - 1]

        name = prefix
        for token in ['<TABLE', '<Container', '<REAL', '<INT', '<STRING', '=']:
            name = name.replace(token, '')

        name = name.strip()

        if name:
            result[name] = value

    return result


def get_attribute_by_name(attributes: dict, name: str) -> str:
    """
    Return attribute value by key.
    """
    return attributes.get(name, "")


def get_ala_xml_var_type(s: str) -> str:
    s_upper = s.upper()
    for t in ("STRING", "REAL", "INT"):
        if t in s_upper:
            return t
    return ""

# ----- functions to manipulate parameter date sets in parameter set files 

def get_parameter_data_set_by_id(parameter_set_file , id_value: str = None):
    """
    Extract one parameter dataset (row across all tables) by ID.

    Parameters
    ----------
    parameter_set_file : AlaskaParameterSetFile or list[dict]
        Parameter set file 
        
    id_value 
        ID of the dataset. If empty string, first dataset is returned.

    Returns
    -------
    tuple
        (PDS, row_id)
        PDS: list of row data per table
        row_id: 0-based index , 0 if not found
    """

    if not parameter_set_file.tables:
        print("Parameter set file is empty!")
        return [], 0

    # --- first table defines IDs
    pst1 = parameter_set_file.tables[0]

    # convert rows safely
    try:
        no_rows = int(pst1["no_rows"])
    except (TypeError, ValueError):
        print("Invalid no_rows in first table")
        return [], 0

    content1 = pst1["Content"]

    # --- if id is empty take first row ID
    if not id_value:
        id_value = content1[0, 0]

    row_id = None

    # --- find matching row (MATLAB: last match wins)
    for i in range(no_rows):
        if content1[i, 0] == id_value:
            row_id = i 

    if row_id == None:
        print(f"parameter set with ID {id_value} not found!")
        return [], 0

    # --- extract row across all tables
    print(f"found parameter set with ID {id_value}.")
    parameter_data_set = []

    for table in parameter_set_file.tables:
        content = table["Content"]

        try:
            row = content[row_id , :]  
        except Exception:
            row = None

        parameter_data_set.append(row)

    return parameter_data_set, row_id
    
    

def add_parameter_data_set(parameter_set_file , parameter_data_set : list, newname: str = None):
    """
    Add a parameter dataset (row across all tables) to parameter_set_file.

    Parameters
    ----------
    parameter_set_file : AlaskaParameterSetFile or list[dict]
        Parameter set file object.
        
    parameter_data_set : list
        One dataset (list of rows per table).
        
    newname : str, optional
        New ID for the dataset.

    Returns
    -------
    parameter_set_file
        Modified parameter_set_file (in-place).
    """

    # --- check if name already exists
    if newname:
        _, row_id = parameter_set_file.get_parameter_data_set_by_id(newname)
        if row_id != 0:
            print(f"parameter data set with name {newname} already exists and will not be added!")
            return parameter_set_file
        else:
            print(f"parameter data set with ID {newname} will be added")

    # --- append to each table
    for i, table in enumerate(parameter_set_file.tables):

        content = table["Content"]

        # ensure numpy array
        if not isinstance(content, np.ndarray):
            content = np.array(content, dtype=object)

        new_row = parameter_data_set[i]

        # ensure row is array
        new_row = np.array(new_row, dtype=object).reshape(1, -1)

        # append row
        content = np.vstack([content, new_row])

        table["Content"] = content

        # --- update counters 
        no_cols = table["no_cols"]
        no_rows = table["no_rows"]

        no_rows += 1
        no_cells = no_rows * no_cols

        table["no_rows"] = no_rows
        table["no_cells"] = no_cells  

        # --- overwrite ID if requested
        if newname:
            table["Content"][-1, 0] = newname

        # --- update attribute "rows"
        # equivalent to setPSTAttbyName
        updated = False
        for j, name in enumerate(table["AttNames"]):
            if name == "rows":
                table["AttContent"][j] = str(no_rows)
                updated = True

        if not updated:
            table["AttNames"].append("rows")
            table["AttContent"].append(str(no_rows))

    return parameter_set_file    
    
    
def delete_all_parameter_data_set(parameter_set_file):
    """
    Delete all parameter datasets (rows) from parameter_set_file.
    Keeps table structure (attributes).

    Parameters
    ----------
    parameter_set_file : parameter_set_file

    Returns
    -------
    parameter_set_file
    """

    for table in parameter_set_file.tables:

        no_cols = table["no_cols"]

        # --- clear content (keep correct shape!)
        table["Content"] = np.empty((0, no_cols), dtype=object)

        # --- reset counters
        table["no_rows"] = 0 
        table["no_cells"] = 0

        # --- update attribute "rows"
        updated = False
        for i, name in enumerate(table["AttNames"]):
            if name == "rows":
                table["AttContent"][i] = "0"
                updated = True

        if not updated:
            table["AttNames"].append("rows")
            table["AttContent"].append("0")
        
    print("All parameter data sets were deleted from current parameter set file.")    
        
    return parameter_set_file    


# ----- functions to manipulate xml tables in parameter set files and simple xml files
    
def find_table(tables : list, tablename: str) -> int:
    """
    Find index of a table in an alaska xml file by name.

    Parameters
    ----------
    tables : list[dict]
        List of parsed xml tables.
    tablename : str
        Name of the table to search for.

    Returns
    -------
    int
        Index of the table (0-based), or None if not found.
    """

    for i, table in enumerate(tables):
        if table.get("Name") == tablename:
            return i

    return None    
    
    
def append_parameter_set_table(parameter_set_file, table_name : str):
    """
    Add a new table (parameter set table) to parameter_set_file.

    Parameters
    ----------
    parameter_set_file : AlaskaParameterSetFile
        
    table_name : str
        name of new table

    Returns
    -------
    parameter_set_file : AlaskaParameterSetFile
    """

    if not parameter_set_file.tables:
        print("PSF is empty - cannot add new table!")
        return parameter_set_file

    # --- reference first table
    pst1 = parameter_set_file.tables[0]

    # --- build attributes
    att_names = []
    att_content = []

    # name
    att_names.append("name")
    att_content.append(table_name)

    # type
    att_names.append("type")
    att_content.append("STRING")

    # cols
    att_names.append("cols")
    att_content.append("1")

    # head → first column name from first table
    head_str = None
    for name, val in zip(pst1["AttNames"], pst1["AttContent"]):
        if name == "head":
            head_str = val
            break

    if head_str:
        first_head = head_str.strip().split()[0]
    else:
        first_head = "ID"

    att_names.append("head")
    att_content.append(first_head)

    # units
    att_names.append("units")
    att_content.append("-")

    # colTypes
    att_names.append("colTypes")
    att_content.append("ID")

    # colDescription
    att_names.append("colDescriptions")
    att_content.append("'Loadcases ID'")

    # --- table structure
    no_rows = pst1["no_rows"]
    no_cols = 1
    no_cells = no_rows * no_cols

    # --- copy first column (ID)
    content1 = pst1["Content"]

    new_content = content1[:, 0].reshape(no_rows, 1)

    # --- build table dict
    table = {
        "AttNames": att_names,
        "AttContent": att_content,
        "Name": table_name,
        "Type": "STRING",
        "no_rows": no_rows,
        "no_cols": no_cols,
        "no_cells": no_cells,
        "Content": new_content,
        "precision": pst1.get("precision"),
    }

    # --- append to parameter_set_file
    parameter_set_file.tables.append(table)

    return parameter_set_file    
    
# ----- functions to manipulate variables in parameter set files 

def get_variable_names(parameter_set_file) -> list:
    """
    get variable names of all variables in all parameter set tables in parameter set file 
    function will remove duplicate entries of parameter set ID (or Lc_ID for loadcases)

    Parameters
    ----------
    parameter_set_file : AlaskaParameterSetFile 
        parameter set file or list[dict] containing xml tables
        

    Returns
    -------
     : list[str]
        list of variables names
    """

    var_names = list()
    
    for ti, table in enumerate(parameter_set_file.tables):

        # --- get head attribute
        head_str = None
        for name, val in zip(table["AttNames"], table["AttContent"]):
            if name == "head":
                head_str = val
                break

        if head_str is None:
            continue

        # --- remove quotes and split
        head_str = head_str.replace("'", "")
        heads = head_str.strip().split()

        var_names.extend(heads)
        
    #return var_names without duplicate entries of parameter set ID (or Lc_ID for loadcases)

    return list(dict.fromkeys(var_names))

def find_parameter_set_variable(
    parameter_set_file, variable_name: str
) -> tuple[list[int], list[int]]:
    """
    Find parameter set variable (column) in parameter_set_file tables.

    Parameters
    ----------
    parameter_set_file : PSF
        AlaskaParameterSetFile or list[dict] of tables containing parameter set file content
    variable_name
        name of variable

    Returns
    -------
    tuple (table_inds, column_inds)
        Parallel lists of table and column indices for every matching variable.
    """

    table_inds = []
    column_inds = []

    if ' ' in variable_name:
        print(f'parameter set variables must not have spaces: find_variable "{variable_name}"')
        return table_inds, column_inds

    for ti, table in enumerate(parameter_set_file.tables):

        # --- get head attribute
        head_str = None
        for name, val in zip(table["AttNames"], table["AttContent"]):
            if name == "head":
                head_str = val
                break

        if head_str is None:
            continue

        # --- remove quotes and split
        head_str = head_str.replace("'", "")
        heads = head_str.strip().split()

        # --- consistency check
        try:
            no_cols = table["no_cols"]
        except (TypeError, ValueError):
            print(f"Invalid no_cols in table {table.get('Name')}")
            return [], []

        if len(heads) != no_cols:
            print(f'error in parsing head attribute of table {table.get("Name")}')
            return [], []

        # --- search variable
        for ci, h in enumerate(heads):
            if variable_name == h:
                table_inds.append(ti)
                column_inds.append(ci)

                print(
                    f'found variable {variable_name} in table with name = "{table.get("Name")}"'
                )
                print(
                    f"index of table: {ti} index of column: {ci}"
                )
            
    if not table_inds:
        print(f"Variable with name {variable_name} can not be found in parameter set file")


    return table_inds, column_inds


def delete_parameter_set_variable(parameter_set_file, variable_name: str):
    """
    Delete a variable (column) from parameter set file

    Parameters
    ----------
    parameter_set_file : AlaskaParameterSetFile or list[dict]
        parameter set file to be manipulated
    
    
    variable_name
        name of variable to be deleted from parameter set file
    
    Returns
    -------
    parameter_set_file
        manipulated parameter set file
    """

    table_inds, col_inds = find_parameter_set_variable(parameter_set_file, variable_name)
    
    for table_ind, col_ind in sorted(zip(table_inds, col_inds), reverse=True):
        table = parameter_set_file[table_ind]
        # --- update counters
        no_rows = table["no_rows"]
        no_cols = int(table["no_cols"])

        table["no_cols"] = no_cols -1
        table["no_cells"] = no_rows * (no_cols - 1)

        # --- helper to update attribute lists
        def update_attr(attr_name, value = None, replace = False):
            for i, name in enumerate(table["AttNames"]):
                if name == attr_name:
                    if replace:
                        table["AttContent"][i] = str(value)
                    else:
                        val = table["AttContent"][i]
                        parts = re.findall(r"'[^']*'|\\S+", val)
                        if len(parts) >= col_ind + 1:
                            parts.pop(col_ind)
    
                        # rejoin WITHOUT quotes (like MATLAB)
                        table["AttContent"][i] = " ".join(parts)

        # --- update relevant attributes
        update_attr("head")
        update_attr("units")
        update_attr("colTypes")
        update_attr("colDescriptions")
        update_attr("cols", no_cols-1 , True)

        # --- remove column from content
        content = table["Content"]
        table["Content"] = np.delete(content, col_ind, axis=1)


    return parameter_set_file
        


def add_parameter_set_variable(parameter_set_file, table_name: str, variable_name: str, new_data_column = None, variable_type : str = "STRING", unit : str = "-"):
    """
    Add a parameter set variable (column) to specific parameter set table.

    Parameters
    ----------
    parameter_set_file : parameter_set_file

    table_name : str
        name of table
        
    variable_name : str
        name of new variable
        
    new_data_column : list, optional
        Column data (length must match number of rows in parameter set file)
        
    variable_type : str , optional
        Variable type (STRING, REAL, INT), default STRING
        
    unit : str , optional
        Unit of variable ("-" if None)

    Returns
    -------
    parameter_set_file
    """

    table_inds, _ = find_parameter_set_variable(parameter_set_file, variable_name)
    if table_inds:
        print(f'Variable with name {variable_name} already found in parameter set file - can not be added')


    for table in parameter_set_file.tables:

        if table.get("Name") != table_name:
            continue

        no_rows = table["no_rows"]
        no_cols = table["no_cols"]

        # --- create default column
        dummy_col = ["-"] * no_rows

        # --- validate / use provided column
        if new_data_column is None:
            
            col_data_str = list(dummy_col)

        else:
            if np.isscalar(new_data_column):
                new_data_column = [new_data_column]

            col_data = list(new_data_column)
            
            if len(col_data) != no_rows:
                print("new_data_column length is not correct!")
                return parameter_set_file
            
            col_data_str = [str(v) for v in col_data]

        # --- convert to numpy column
        col_array = np.array(col_data_str, dtype=object).reshape(no_rows, 1)

        # --- append column
        content = table["Content"]
        table["Content"] = np.hstack([content, col_array])

        # --- update counters
        no_cols_new = no_cols + 1
        table["no_cols"] = no_cols_new
        table["no_cells"] = no_rows * no_cols_new

        # --- helper to update attributes
        def append_attr(attr_name, value, replace = False):
            for i, name in enumerate(table["AttNames"]):
                if name == attr_name:
                    existing = table["AttContent"][i]
                    if existing:
                        if replace:
                            table["AttContent"][i] = value
                        else: 
                            table["AttContent"][i] = existing + "  " + value
                    else:
                        table["AttContent"][i] = value
                    return
            # if attribute does not exist → add it
            table["AttNames"].append(attr_name)
            table["AttContent"].append(value)

        # --- update attributes
        append_attr("cols", str(no_cols_new), True)
        append_attr("head", variable_name)
        append_attr("units", unit)
        append_attr("colTypes", variable_type)
        append_attr("colDescriptions", "-")

    return parameter_set_file    

def add_parameter_set_select_variable(parameter_set_file, table_name: str, variable_name: str, new_data_column = None,  switches : str = ""):
    """
    Add a parameter set variable (column) to specific parameter set table.

    Parameters
    ----------
    parameter_set_file : parameter_set_file

    table_name : str
        name of table
        
    variable_name : str
        name of new variable
        
    new_data_column : list, optional
        Column data (length must match number of rows in parameter set file)
        
    switches : str
        switches of the SELECT variable, must be separated by "/" , and passed as one str: eg: switches = "ON/OFF"       

    Returns
    -------
    parameter_set_file
    """
    
    variable_type = "SELECT"
    unit = "-"
    
    table_inds, _ = find_parameter_set_variable(parameter_set_file, variable_name)
    if table_inds:
        print(f'Variable with name {variable_name} already found in parameter set file - can not be added')


    for table in parameter_set_file.tables:

        if table.get("Name") != table_name:
            continue

        no_rows = table["no_rows"]
        no_cols = table["no_cols"]

        # --- create default column
        dummy_col = ["-"] * no_rows

        # --- validate / use provided column
        if new_data_column is None:
            
            col_data_str = list(dummy_col)

        else:
            if np.isscalar(new_data_column):
                new_data_column = [new_data_column]

            col_data = list(new_data_column)
            
            if len(col_data) != no_rows:
                print("new_data_column length is not correct!")
                return parameter_set_file
            
            col_data_str = [str(v) for v in col_data]

        # --- convert to numpy column
        col_array = np.array(col_data_str, dtype=object).reshape(no_rows, 1)

        # --- append column
        content = table["Content"]
        table["Content"] = np.hstack([content, col_array])

        # --- update counters
        no_cols_new = no_cols + 1
        table["no_cols"] = no_cols_new
        table["no_cells"] = no_rows * no_cols_new

        # --- helper to update attributes
        def append_attr(attr_name, value, replace = False):
            for i, name in enumerate(table["AttNames"]):
                if name == attr_name:
                    existing = table["AttContent"][i]
                    if existing:
                        if replace:
                            table["AttContent"][i] = value
                        else: 
                            table["AttContent"][i] = existing + "  " + value
                    else:
                        table["AttContent"][i] = value
                    return
            # if attribute does not exist → add it
            table["AttNames"].append(attr_name)
            table["AttContent"].append(value)

        # --- update attributes
        append_attr("cols", str(no_cols_new), True)
        append_attr("head", variable_name)
        append_attr("units", unit)
        append_attr("colTypes", variable_type)
        append_attr("colDescriptions", "["+switches +"]")

    return parameter_set_file    

def get_parameter_data_set_variable(parameter_set_file, variable_name: str, parameter_data_set_id : str = None):
    """
    Set value of a variable in a specific parameter dataset.
    if parameter_data_set_id is None, the full columns of the parameter set variable is retrieved

    Parameters
    ----------
    parameter_set_file : AlaskaParameterSetFile or list[dict]

    variable_name 
        Variable name (column)

    parameter_data_set_id : str , optional
        ID of parameter dataset (corresponds to specific row in all parameter set tables) or None 

    Returns
    -------
    str, numpy.ndarray[str], or list[str | numpy.ndarray[str]]
        A list is returned when the variable exists in multiple tables.
    """

    # --- find variable location
    table_inds, col_inds = find_parameter_set_variable(parameter_set_file, variable_name)

    # --- find dataset row
    row_ind = 0     # change first parameter data set , if parameter_data_set_id is None
    if parameter_data_set_id is not None:
        _, row_ind = parameter_set_file.get_parameter_data_set_by_id(parameter_data_set_id)

    # --- check indices
    if row_ind is None or not table_inds:
        print(
            f'variable {variable_name} which should be changed for '
            f'parameter data set ID {parameter_data_set_id} was not found'
        )
        return None

    content = []
    for table_ind, col_ind in zip(table_inds, col_inds):
        table_content = parameter_set_file.tables[table_ind]["Content"]
        if parameter_data_set_id is None:
            content.append(table_content[:, col_ind])
        else:
            content.append(table_content[row_ind, col_ind])

    return content[0] if len(content) == 1 else content
    
    
def set_parameter_data_set_variable_value(parameter_set_file, variable_name: str, variable_value, parameter_data_set_id : str = None):
    """
    Set value of a variable in a specific parameter dataset.
    - If parameter_data_set_id is None and variable_value is scalar, the variable is changed in the first parameter data set of every matching table.
    - If parameter_data_set_id is None and variable_value is not scalar, the values will be put in every matching variable column when the length matches.

    Parameters
    ----------
    parameter_set_file : AlaskaParameterSetFile or list[dict]

    variable_name 
        Variable name (column)

    variable_value : any
        New value (kept as-is, typically string)
    
    parameter_data_set_id : str , optional
        ID of parameter dataset (corresponds to specific row in all parameter set tables)

    Returns
    -------
    parameter_set_file
    """

    # --- do not write empty values 
    if variable_value is None or variable_value == "":
        return parameter_set_file

    # --- find variable location
    table_inds, col_inds = find_parameter_set_variable(parameter_set_file, variable_name)

    # --- find dataset row
    row_ind = 0     # change first parameter data set , if parameter_data_set_id is None
    if parameter_data_set_id is not None:
        _, row_ind = parameter_set_file.get_parameter_data_set_by_id(parameter_data_set_id)

    # --- check indices
    if row_ind is not None and table_inds:
        for table_ind, col_ind in zip(table_inds, col_inds):
            table = parameter_set_file.tables[table_ind]
            content = table["Content"]

            if np.isscalar(variable_value):
                content[row_ind, col_ind] = str(variable_value)
            elif len(variable_value) == table["no_rows"]:
                col_data_str = [str(v) for v in variable_value]
                col_array = np.array(col_data_str, dtype=object).reshape(table["no_rows"], 1)
                content[:, col_ind] = col_array[:, 0]
            else:
                print(f"length of {variable_value} does not fit size of table {table['no_rows']}")
            

    else:
        print(
            f'variable {variable_name} which should be changed for '
            f'parameter data set ID {parameter_data_set_id} was not found'
        )

    return parameter_set_file
    