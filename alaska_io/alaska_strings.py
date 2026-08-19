import shlex


def parse_str_of_strings(in_string: str) -> list:
    """
    Split string while respecting quoted sub-strings.
    - Keeps sub-strings enclosed in single quotes together
    - Preserves backslashes (e.g., Windows paths)    

    Parameters
    ----------
    in_string 
        input string
        
    Returns
    -------
        list of strings
    """
    lexer = shlex.shlex(in_string, posix=True)  
    # Split tokens on whitespace
    lexer.whitespace_split = True
    # Use only single quotes for grouping
    lexer.quotes = "'"
    
    # Disable escape character handling so backslashes are preserved
    lexer.escape = ''          
    lexer.escapechar = None    
    
    return list(lexer)
    
def print_string(file_handle, string_data: str, fronttabs: int = 0, linebreak: int = 1) -> None:
    """
    Write a string to file with optional front tabs and optional line break.

    Parameters
    ----------
    file_handle : file-like object
        File handle.
        
    string_data : 
        String to write.
        
    fronttabs : 
        Number of leading tabs.
        
    linebreak : 
        If 1, append newline.
    """

    # write leading tabs
    file_handle.write("\t" * fronttabs)

    # write main string
    file_handle.write(string_data)

    # optional newline
    if linebreak == 1:
        file_handle.write("\n")