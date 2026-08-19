from .alaska_strings import print_string

from io import StringIO
from datetime import datetime


def write_xml_variable(file_handle, xml_variable: dict) -> None:

    """
    writes alaska xml variable to file_handle like object
        
    Parameters
    ----------
    file_handle
        file handle or StringIO
        
    xml_variable
        alaska xml variable dict
    """

    # don't write comments
    if any("<!--" in s for s in xml_variable.get("AttNames", [])):
        return
    
    print_string(file_handle, "<"+xml_variable['Type'], 1, 0)

    att_names   = xml_variable.get("AttNames", [])
    att_content = xml_variable.get("AttContent", [])

    # --- attributes
    for i, (name, value) in enumerate(zip(att_names, att_content)):
        closing = ">" if i == len(att_names) - 1 else ""
        print_string(file_handle, f' {name} = "{value}"{closing}', 2, 1)


    # --- content
    content = xml_variable["Content"]
    print_string(file_handle, content, 3, 1)

    # --- close xml variable
    print_string(file_handle, "</"+xml_variable['Type']+">", 1, 1)
    

    
def format_table(content, precision : int):
    """
    Format a 2D table (list-like or array-like) into aligned columns.
    - Converts values to strings
    - Adds quotes if a value contains spaces
    - Aligns all columns based on maximum width
    
    Parameters
    ----------
    content 
        table content as numpy ndarray
        
    precision
        number of digits for converting numbers to strings
    """
    rows = len(content)
    cols = len(content[0])

    # First pass: convert everything to strings
    str_table = []
    for ri in range(rows):
        row = []
        for ci in range(cols):
            c = content[ri][ci]

            if not isinstance(c, str):
                c = f"{c:.{precision}g}"

            if " " in c:
                c = f"'{c}'"

            row.append(c)
        str_table.append(row)

    # Determine max width per column
    col_widths = [
        max(len(str_table[ri][ci]) for ri in range(rows))
        for ci in range(cols)
    ]

    return str_table, col_widths    

def write_aligned_table(fh, content, precision : int , fronttabs_first_col : int = 4, fronttabs_other : int =1):
    str_table, col_widths = format_table(content, precision)

    for ri, row in enumerate(str_table):
        for ci, cell in enumerate(row):

            # choose indentation
            leading = fronttabs_first_col if ci == 0 else fronttabs_other

            fh.write("\t" * leading)

            # pad cell to column width
            padded = cell.ljust(col_widths[ci] + 2)
            fh.write(padded)

        fh.write("\n")    
        
def write_alaska_xml_table(fh, table: dict) -> None:
    """
    writes alaska xml table to file_handle
    
    Parameters
    ----------
    fh     
        file handle like object
    
    table 
        dict containing an alaska xml table element
    """

    # --- open TABLE
    print_string(fh, "<TABLE", 1, 0)

    att_names = table.get("AttNames", [])
    att_content = table.get("AttContent", [])

    # --- attributes
    for i, (name, value) in enumerate(zip(att_names, att_content)):
        closing = ">" if i == len(att_names) - 1 else ""
        print_string(fh, f' {name} = "{value}"{closing}', 2, 1)

    # --- consistency check
    if table["no_rows"] * table["no_cols"] != table["no_cells"]:
        print(
            f"Warning: number of table cells of table {table.get('Name')} "
            f"does not match rows*cols"
        )
        return

    # --- content
    content = table["Content"]
    
    write_aligned_table(fh, content, table['precision'])

    # --- close TABLE
    print_string(fh, "</TABLE>", 1, 1)


def write_xml(xml_tables : list, xml_variables : list, filename : str = None) -> str:
    """
    Write xml file to disk (filename) or str.
    - if filename is None return content as str

    Parameters
    ----------
    xml_tables _ list[dict]
        list of xml tables
     
    xml_variables : list[dict]
        list of xml variables
    
    filename : str or None
        Output file path.
        
    Returns
    -------
    : str 
        xml file content as str
    """
    xml_file_content = write_xml_2_str(xml_tables, xml_variables)
    
    if filename is not None:
        with open(filename, "w", encoding="iso-8859-1") as f:
            f.write(xml_file_content)
        return
    else: 
        return xml_file_content
        
def write_xml_2_str(xml_tables : list, xml_variables : list) -> str:
    """
    Write alaska xml file objects to string

    Parameters
    ----------
    xml_tables : list[dict]
        list of xml tables
        
    xml_variables : list[dict]
        list of xml variables
    

    Returns
    -------
    f.getvalue 
        str containing xml variables and xml tables
    """
    
    f = StringIO()

    # --- XML header
    print_string(f, '<?xml version="1.0" encoding="iso-8859-1"?>', 0, 1)

    print_string(f, '<IFM:data name="alaska" xmlns:IFM="http://www.icm-chemnitz.de">', 0,1)

    # --- timestamp comment 
    timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    print_string(f, f"<!-- {timestamp} -->", 1, 1)

    # --- write all tables
    for table in xml_tables:
        write_alaska_xml_table(f, table)

    # --- write all variables
    for xml_var in xml_variables:
        write_xml_variable(f, xml_var)

    # --- closing tag
    f.write("</IFM:data>\n")

    return f.getvalue()


def write_parameter_set_file(filename: str, parameter_set_file ) -> None:
    """
    Write full ParameterSetFile to disk.

    Parameters
    ----------
    filename : str
        Output file path.
        
    parameter_set_file : AlaskaParameterSetFile or list[dict]
        AlaskaParameterSetFile object or list of tables.
    """

    # allow both PSF class and raw list
    tables = parameter_set_file.tables if hasattr(parameter_set_file, "tables") else parameter_set_file

    if not tables:
        print(f"ParameterSet file {filename} is empty and can not be written!")
        return

    print(f"Writing parameter set file to file name {filename}.")        

    with open(filename, "w", encoding="iso-8859-1") as f:

        # --- XML header
        print_string(f, '<?xml version="1.0" encoding="iso-8859-1"?>', 0, 1)

        print_string(
            f,
            '<IFM:data name="alaska" xmlns:IFM="http://www.icm-chemnitz.de">',
            0,
            1,
        )

        # --- timestamp comment 
        timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        print_string(f, f"<!-- {timestamp} -->", 1, 1)

        # --- write all tables
        for table in tables:
            write_alaska_xml_table(f, table)

        # --- closing tag
        f.write("</IFM:data>\n")
