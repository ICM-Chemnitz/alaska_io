from pathlib import Path
import numpy as np

#import alaska_io 
from alaska_io import AlaskaXmlFile

# routines for dict and table comparison

def deep_equal_dict(d1, d2):
    if d1.keys() != d2.keys():
        print("keys mismatch")
        print(f"{d1.keys()}")
        print(f"{d2.keys()}")
        return False

    for k in d1:
        v1, v2 = d1[k], d2[k]

        if isinstance(v1, np.ndarray) or isinstance(v2, np.ndarray):
            if not np.array_equal(v1, v2):
                print("error comparing the following two elements")
                print(f"{v1}")
                print(f"{v2}")
                return False
        else:
            if v1 != v2:
                print('element mismatch')
                print(f"{v1}")
                print(f"{v2}")
                
                return False

    return True

def deep_equal_tables(t1, t2):
    if len(t1) != len(t2):
        print("length mismatch")
        return False

    return all(deep_equal_dict(a, b) for a, b in zip(t1, t2))


# ----- start of tests

TEST_DATA = Path(__file__).parent / "data"

def test_create_xml_file():
    xml_file = AlaskaXmlFile()

    assert xml_file is not None

def test_read_write(tmp_path):
    output_file = tmp_path / "test.xml"
    xml_file = AlaskaXmlFile(str(TEST_DATA / 'Blade.xml'))

    xml_file.write(output_file)

    xml_file_expected = AlaskaXmlFile(output_file)

    assert deep_equal_tables(xml_file.xml_tables, xml_file_expected.xml_tables) and deep_equal_tables(xml_file.xml_variables, xml_file_expected.xml_variables)
    

def test_read_write_to_str(tmp_path):

    xml_file_expected = AlaskaXmlFile(str(TEST_DATA / 'Blade.xml'))
    xml_file_str =  xml_file_expected.write_to_str()
    xml_file = AlaskaXmlFile()
    xml_file.read_from_str(xml_file_str)

    assert deep_equal_tables(xml_file.xml_tables, xml_file_expected.xml_tables) and deep_equal_tables(xml_file.xml_variables, xml_file_expected.xml_variables)


def test_var_add_real(tmp_path):
    xml_file = AlaskaXmlFile(TEST_DATA / 'Blade.xml')
    xml_file.add_real_variable('TEstVar', 42.42 )
    # xml_file.write(TEST_DATA / 'Blade_var_add_real.xml')
    xml_file_expected = AlaskaXmlFile(TEST_DATA / 'Blade_var_add_real.xml')

    assert deep_equal_tables(xml_file.xml_tables, xml_file_expected.xml_tables) and deep_equal_tables(xml_file.xml_variables, xml_file_expected.xml_variables)
   
def test_var_add_real_unit(tmp_path):
    xml_file = AlaskaXmlFile(TEST_DATA / 'Blade.xml')
    xml_file.add_real_variable('TEstVar', 42.42 , 'm')
    #xml_file.write(TEST_DATA / 'Blade_var_add_real_unit.xml')
    xml_file_expected = AlaskaXmlFile(TEST_DATA / 'Blade_var_add_real_unit.xml')

    assert deep_equal_tables(xml_file.xml_tables, xml_file_expected.xml_tables) and deep_equal_tables(xml_file.xml_variables, xml_file_expected.xml_variables)


def test_var_add_string(tmp_path):
    xml_file = AlaskaXmlFile(TEST_DATA / 'Blade.xml')
    xml_file.add_string_variable('TEstS TRING2', 'ein string')
    #xml_file.write(TEST_DATA / 'Blade_var_add_string.xml')
    xml_file_expected = AlaskaXmlFile(TEST_DATA / 'Blade_var_add_string.xml')


    assert deep_equal_tables(xml_file.xml_tables, xml_file_expected.xml_tables) and deep_equal_tables(xml_file.xml_variables, xml_file_expected.xml_variables)

def test_var_set_string(tmp_path):
    xml_file = AlaskaXmlFile(TEST_DATA / 'Blade.xml')
    xml_file.set_variable_value('MRBladeForceTemplate', 'TMyBladeForce')
    #xml_file.write(TEST_DATA / 'Blade_var_set_string.xml')
    xml_file_expected = AlaskaXmlFile(TEST_DATA / 'Blade_var_set_string.xml')

    assert deep_equal_tables(xml_file.xml_tables, xml_file_expected.xml_tables) and deep_equal_tables(xml_file.xml_variables, xml_file_expected.xml_variables)

def test_var_set_real(tmp_path):
    xml_file = AlaskaXmlFile(TEST_DATA / 'Blade.xml')
    xml_file.add_real_variable('TEstVar', 42.42 , 'm')
    xml_file.set_variable_value('TEstVar', -412)
    #xml_file.write(TEST_DATA / 'Blade_var_set_real.xml')
    xml_file_expected = AlaskaXmlFile(TEST_DATA / 'Blade_var_set_real.xml')

    assert deep_equal_tables(xml_file.xml_tables, xml_file_expected.xml_tables) and deep_equal_tables(xml_file.xml_variables, xml_file_expected.xml_variables)
