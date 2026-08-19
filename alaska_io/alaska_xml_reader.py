
import numpy as np
from io import StringIO

from .alaska_strings import parse_str_of_strings
from .alaska_xml_helper import get_ala_xml_var_type, get_attribute_by_name, parse_attribute_dict


def parse_xml_variable(xml_variable_str : str) -> dict:
    """
    Parses string of alaska xml variable 
    xml_variable_str look like (e.g. <INT name = "my_name"> 42 </INT>)
    
    Parameters
    ----------
    xml_variable_str    
        full xml element of an alaska xml variable 
        
    Returns
    -------
    xml_variable
        dict corresponding to an alaska xml variable
    """

    xml_variable = {}

    # find all opening '<' and closing '>'
    t_s = [i for i, c in enumerate(xml_variable_str) if c == '<']
    t_e = [i for i, c in enumerate(xml_variable_str) if c == '>']

    if len(t_s) < 2:
        print('Failed to parse alaska xml variable! Did not find two "<" characters!')
        return None

    # head of the XML variable
    varhead = xml_variable_str[t_s[0]:t_e[0]+1].strip()

    # content between first '>' and second '<'
    varcontent = xml_variable_str[t_e[0]+1:t_s[1]].strip()

    # parse attributes 
    attr = parse_attribute_dict(xml_variable_str)

    xml_variable.update({
        'AttNames': list(attr.keys()),
        'AttContent':list(attr.values()),
        'Name': get_attribute_by_name(attr, 'name'),
        'Content': varcontent,
        'Type': get_ala_xml_var_type(xml_variable_str)
    })

    return xml_variable
    
def parse_xml_table_str(xml_table_str: str, precision) -> dict:
    """
    Parses string of alaska xml table 
    xml_variable_str look like (e.g. <INT name = "my_name"> 42 </INT>)
    
    Parameters
    ----------
    parse_xml_table_str    
        full xml element of an alaska xml variable 
        
    Returns
    -------
    table
        dict corresponding to an alaska xml variable
    """

    t_s = [i for i, c in enumerate(xml_table_str) if c == '<']
    t_e = [i for i, c in enumerate(xml_table_str) if c == '>']

    tablehead    = xml_table_str[t_s[0]:t_e[0] + 1].strip()
    tablecontent = xml_table_str[t_e[0] + 1:t_s[1]].strip()

    tc = parse_str_of_strings(tablecontent)
    attrs = parse_attribute_dict(tablehead)

    # rows attribute must not be present (in all cases)
    str_rows = get_attribute_by_name(attrs, "rows")
    no_rows = -1
    if str_rows:
        no_rows = int(str_rows)
    
    table = {
        "AttNames": list(attrs.keys()),
        "AttContent": list(attrs.values()),
        "Name": get_attribute_by_name(attrs, "name"),
        "Type": get_ala_xml_var_type(xml_table_str),
        "no_cols": int(get_attribute_by_name(attrs, "cols")),
        "no_rows": no_rows,
        "no_cells": len(tc),
        "precision": precision,
    }

    # reshape logic 
    cols = table["no_cols"]
    rows = table["no_rows"]

    if cols and rows:
        arr = np.array(tc, dtype=object).reshape(( table["no_rows"], table["no_cols"])) # this is magic and works as intended even when no_rows = -1 (not present in xml) , then retrieves rows by cells / cols
        table["Content"] = arr
    else:
        table["Content"] = tc

    if table["no_rows"] == -1:
        table["no_rows"] = arr.shape[0]
    
    return table


def parse_xml_file(file_path : str = None, xml_text : str = None):
    """
    Parses XML content of input, which may be file handle or StringIO
    - if file_path is not None xml is read from file contained in file_path
    - if file_path is None xml is read from str xml_text
    
    Parameters
    ----------
    infile : file handle or StrinIO
        path and file name of xml file

    xml_text : file handle or StrinIO
        content of xml file as str

    """
    if file_path is not None:
        with open(file_path, 'r', encoding='iso-8859-1') as infile:
            return parse_xml_file_from_stream(infile)
    elif xml_text is not None:
        with StringIO(xml_text) as infile:
            return parse_xml_file_from_stream(infile)
    else: 
        print("xml file can not be read in. Input variable is None")

def parse_xml_file_from_stream(infile):
    """
    Parses XML content of input, which may be file handle or StringIO
    
    Parameters
    ----------
    infile : file handle or StringIO
        path and file name of xml file
        
    Returns
    -------
        parsed xml file
    """

    xml_variables = []
    xml_tables = []

    precision = 8
   
    line = infile.readline()

    while line and "</IFM:data>" not in line:
        xmlvar = False
        line = infile.readline()

        if not line:
            break

        # --- detect TABLE ---
        if "<TABLE" in line:
            pt = line

            while "</TABLE>" not in line:
                line = infile.readline()
                if not line:
                    break
                pt += line

            xml_tables.append(parse_xml_table_str(pt, precision))
        

        # --- detect XML variables ---
        if 'INT' in line:
            xmlvar = True
        elif 'REAL' in line:
            xmlvar = True
        elif 'STRING' in line:
            xmlvar = True

        #  if line contains alaska xml variable : parse line and store XML variable
        if xmlvar:
            l = line

            # XML variable need two closing '>'
            while l.count('>') < 2:
                next_line = infile.readline()
                if not next_line:
                    break
                l += next_line

            curxmlvar = parse_xml_variable(l)
            xml_variables.append(curxmlvar)

    return xml_tables, xml_variables 