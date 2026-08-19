from pathlib import Path
import numpy as np

#import alaska_io 
from alaska_io import AlaskaParameterSetFile

# routines for dict and table comparison

def deep_equal_dict(d1, d2):
    if d1.keys() != d2.keys():
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
                print('we are here ?')
                print(f"{v1}")
                print(f"{v2}")
                
                return False

    return True

def deep_equal_tables(t1, t2):
    if len(t1) != len(t2):
        return False

    return all(deep_equal_dict(a, b) for a, b in zip(t1, t2))


# ----- start of tests

TEST_DATA = Path(__file__).parent / "data"

def test_create_parameter_set_file():
    parameter_set_file = AlaskaParameterSetFile()

    assert parameter_set_file is not None

def test_read(tmp_path):
    output_file = tmp_path / "test.xml"
    parameter_set_file1 = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')

    parameter_set_file1.write(output_file)

    parameter_set_file2 = AlaskaParameterSetFile(output_file)

    # parameter_set_file3 = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    # parameter_set_file3.del
    # parameter_set_file3.write(TEST_DATA / 'LoadCases3.xml')

    assert deep_equal_tables(parameter_set_file1.tables, parameter_set_file2.tables)

def test_get_table():
    parameter_set_file1 = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    table = parameter_set_file1.get('Aerodynamics Parameter')
    
    assert deep_equal_dict(parameter_set_file1[7], table)

def test_get_index():
    parameter_set_file1 = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    simulation_control_index = parameter_set_file1.get_index('Simulation Control')

    assert simulation_control_index == 2

def test_names():
    parameter_set_file1 = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    table_names = parameter_set_file1.names()
    print(f'{table_names}')

    assert table_names == ['BatchControl', 'Loadcase Description', 'Simulation Control', 'File Inputs', 'Turbine Configuration', 'Turbine Initial Conditions', 'Aerodynamics Control', 'Aerodynamics Parameter', 'Rotor Parameter']

def test_get_add_parameter_data_set():
    parameter_set_file1 = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    pds1 , id1 = parameter_set_file1.get_parameter_data_set_by_id()
    parameter_set_file1.add_parameter_data_set(pds1, 'LC2')

    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_get_add.xml')
    
    assert deep_equal_tables(parameter_set_file1.tables, parameter_set_file_expected.tables)

def test_delete_all():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    pds1 , id1 = parameter_set_file.get_parameter_data_set_by_id()
    parameter_set_file.delete_all_parameter_data_sets()
    parameter_set_file.add_parameter_data_set(pds1, 'LC2')
    
    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_del_all_add.xml')
    
    assert deep_equal_tables(parameter_set_file.tables, parameter_set_file_expected.tables)


def test_create_table():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    parameter_set_file.append_table("NewTable")
    
    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_create_table.xml')
    
    assert deep_equal_tables(parameter_set_file.tables, parameter_set_file_expected.tables)


def test_find_variable():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    shear_exponent_table_ind, shear_exponent_column_ind      = parameter_set_file.find_variable('ShearExponent')
    wind_shear_model_table_ind , wind_shear_model_column_ind = parameter_set_file.find_variable('WindShearModel')
    
    #print(f"{shear_exponent_table_ind}, {shear_exponent_column_ind}")
    #print(f"{wind_shear_model_table_ind} {wind_shear_model_column_ind}")
    
    assert shear_exponent_table_ind == 7 and shear_exponent_column_ind == 2 and wind_shear_model_table_ind == 6 and wind_shear_model_column_ind == 3


def test_add_variable_int():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    parameter_set_file.add_variable(table_name = 'Turbine Initial Conditions', variable_name = 'newVar1', data_column = 3, variable_type = 'INT' )
    #parameter_set_file.write(TEST_DATA / 'LoadCases_var1.xml')
    
    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_var_int.xml')
    
    assert deep_equal_tables(parameter_set_file.tables, parameter_set_file_expected.tables)
    
def test_add_variable_real():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    parameter_set_file.add_variable('Turbine Initial Conditions', 'SomeAngle', 3.7, 'REAL' , 'deg')
    # parameter_set_file.write(TEST_DATA / 'LoadCases_var2.xml')
    
    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_var_real.xml')
    
    assert deep_equal_tables(parameter_set_file.tables, parameter_set_file_expected.tables)


def test_add_variable_string():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    parameter_set_file.add_variable('Turbine Initial Conditions', 'SomeSing')
    #parameter_set_file.write(TEST_DATA / 'LoadCases_var_string.xml')
    
    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_var_string.xml')
    
    assert deep_equal_tables(parameter_set_file.tables, parameter_set_file_expected.tables)


def test_add_variable_select():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    parameter_set_file.add_select_variable('Turbine Initial Conditions', 'SomeSwitch','fancy switch 2', "switch1/'fancy switch 2'")
    parameter_set_file.write(TEST_DATA / 'LoadCases_var_select2.xml')
    
    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_var_select.xml')
    
    assert deep_equal_tables(parameter_set_file.tables, parameter_set_file_expected.tables)


def test_add_variable_mix():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    pds1 , _ = parameter_set_file.get_parameter_data_set_by_id()
    parameter_set_file.add_parameter_data_set(pds1, 'LC2')    
        
    parameter_set_file.add_variable('Turbine Initial Conditions', 'SomeAngle1')
    parameter_set_file.add_variable('Turbine Initial Conditions', 'SomeAngle2', data_column = [3.7, 4.2], variable_type = 'REAL' , unit = 'deg')
    #parameter_set_file.write(TEST_DATA / 'LoadCases_var_mix.xml')
    
    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_var_mix.xml')
    
    assert deep_equal_tables(parameter_set_file.tables, parameter_set_file_expected.tables)

def test_delete_variable():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases.xml')
    parameter_set_file.delete_variable('YawIC')    
        
    #parameter_set_file.write(TEST_DATA / 'LoadCases_var_del.xml')
    
    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_var_del.xml')
    
    assert deep_equal_tables(parameter_set_file.tables, parameter_set_file_expected.tables)


def test_get_variable():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_var_get.xml')
    var1 = parameter_set_file.get_variable('MeanWindSpeed')
    var2 = parameter_set_file.get_variable('MeanWindSpeed', 'LC2')
    var3 = parameter_set_file.get_variable('WindWakeModel')

    assert np.all(var1 == ['14' , '12.3']) and var2 == '12.3' and np.all(var3 == ['Dynamic_Flex', 'Dynamic_ADI'])
   

def test_get_variable():
    parameter_set_file = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_var_get.xml')
    parameter_set_file.set_variable_value('MeanWindSpeed', [15, 16])
    parameter_set_file.set_variable_value('MeanWindSpeed', 10.3, 'LC2')
    parameter_set_file.set_variable_value('WindWakeModel', ['Equilibrium', 'Equilibrium'])

    #parameter_set_file.write(TEST_DATA / 'LoadCases_var_set.xml')
    
    parameter_set_file_expected = AlaskaParameterSetFile(TEST_DATA / 'LoadCases_var_set.xml')

    assert deep_equal_tables(parameter_set_file.tables, parameter_set_file_expected.tables)
