import numpy as np

from pathlib import Path

from alaska_io import AlaskaH5ResultFile


# ----- start of tests

TEST_DATA = Path(__file__).parent / "data"

def test_create_result_file():
    result_file = AlaskaH5ResultFile()

    assert result_file is not None

def test_get_sensor_names():
    result_file = AlaskaH5ResultFile(TEST_DATA / 'RWT_LC2.hdf5')
    sensors = result_file.get_sensor_names()
    sensors_expected = ['TIME', 'L1RFrc[1]', 'L1RFrc[2]', 'L1RFrc[3]', 'L1RTrq[1]', 'L1RTrq[2]', 'L1RTrq[3]', 'L40RFrc[1]', 'L40RFrc[2]', 'L40RFrc[3]', 'L40RTrq[1]', 'L40RTrq[2]', 'L40RTrq[3]', 'L80RFrc[1]', 'L80RFrc[2]', 'L80RFrc[3]', 'L80RTrq[1]', 'L80RTrq[2]', 'L80RTrq[3]', 'AF1FL', 'AF1FD', 'AF1T', 'AF40FL', 'AF40FD', 'AF40T', 'AF80FL', 'AF80FD', 'AF80T', 'AF1AoA', 'AF1a', 'AF40AoA', 'AF40a', 'AF80AoA', 'AF80a', 'N40Pos[1]', 'N40Pos[2]', 'N40Pos[3]', 'N84Pos[1]', 'N84Pos[2]', 'N84Pos[3]', 'Azimuth', 'TIME', 'L1RFrc[1]', 'L1RFrc[2]', 'L1RFrc[3]', 'L1RTrq[1]', 'L1RTrq[2]', 'L1RTrq[3]', 'L40RFrc[1]', 'L40RFrc[2]', 'L40RFrc[3]', 'L40RTrq[1]', 'L40RTrq[2]', 'L40RTrq[3]', 'L80RFrc[1]', 'L80RFrc[2]', 'L80RFrc[3]', 'L80RTrq[1]', 'L80RTrq[2]', 'L80RTrq[3]', 'AF1FL', 'AF1FD', 'AF1T', 'AF40FL', 'AF40FD', 'AF40T', 'AF80FL', 'AF80FD', 'AF80T', 'AF1AoA', 'AF1a', 'AF40AoA', 'AF40a', 'AF80AoA', 'AF80a', 'N40Pos[1]', 'N40Pos[2]', 'N40Pos[3]', 'N84Pos[1]', 'N84Pos[2]', 'N84Pos[3]', 'Azimuth', 'TIME', 'L1RFrc[1]', 'L1RFrc[2]', 'L1RFrc[3]', 'L1RTrq[1]', 'L1RTrq[2]', 'L1RTrq[3]', 'L40RFrc[1]', 'L40RFrc[2]', 'L40RFrc[3]', 'L40RTrq[1]', 'L40RTrq[2]', 'L40RTrq[3]', 'L80RFrc[1]', 'L80RFrc[2]', 'L80RFrc[3]', 'L80RTrq[1]', 'L80RTrq[2]', 'L80RTrq[3]', 'AF1FL', 'AF1FD', 'AF1T', 'AF40FL', 'AF40FD', 'AF40T', 'AF80FL', 'AF80FD', 'AF80T', 'AF1AoA', 'AF1a', 'AF40AoA', 'AF40a', 'AF80AoA', 'AF80a', 'N40Pos[1]', 'N40Pos[2]', 'N40Pos[3]', 'N84Pos[1]', 'N84Pos[2]', 'N84Pos[3]', 'Azimuth', 'TIME', 'GenTrq', 'Power', 'TIME', 'RotorOmega', 'RotorTrq', 'TipTowerWallDistance', 'TIME', 'WindSpeed', 'WindSlope', 'WindYaw', 'MeanInflow', 'TIME', 'P1PitchRev', 'P1PitchRevVel', 'P1PitchRevAcc', 'P1PitchDrvTrq', 'P2PitchRev', 'P2PitchRevVel', 'P2PitchRevAcc', 'P2PitchDrvTrq', 'P3PitchRev', 'P3PitchRevVel', 'P3PitchRevAcc', 'P3PitchDrvTrq', 'TIME', 'L1RFrc[1]', 'L1RFrc[2]', 'L1RFrc[3]', 'L1RTrq[1]', 'L1RTrq[2]', 'L1RTrq[3]', 'L2RFrc[1]', 'L2RFrc[2]', 'L2RFrc[3]', 'L2RTrq[1]', 'L2RTrq[2]', 'L2RTrq[3]', 'L3RFrc[1]', 'L3RFrc[2]', 'L3RFrc[3]', 'L3RTrq[1]', 'L3RTrq[2]', 'L3RTrq[3]', 'L4RFrc[1]', 'L4RFrc[2]', 'L4RFrc[3]', 'L4RTrq[1]', 'L4RTrq[2]', 'L4RTrq[3]', 'L5RFrc[1]', 'L5RFrc[2]', 'L5RFrc[3]', 'L5RTrq[1]', 'L5RTrq[2]', 'L5RTrq[3]', 'L6RFrc[1]', 'L6RFrc[2]', 'L6RFrc[3]', 'L6RTrq[1]', 'L6RTrq[2]', 'L6RTrq[3]', 'L7RFrc[1]', 'L7RFrc[2]', 'L7RFrc[3]', 'L7RTrq[1]', 'L7RTrq[2]', 'L7RTrq[3]', 'L8RFrc[1]', 'L8RFrc[2]', 'L8RFrc[3]', 'L8RTrq[1]', 'L8RTrq[2]', 'L8RTrq[3]', 'L9RFrc[1]', 'L9RFrc[2]', 'L9RFrc[3]', 'L9RTrq[1]', 'L9RTrq[2]', 'L9RTrq[3]', 'L10RFrc[1]', 'L10RFrc[2]', 'L10RFrc[3]', 'L10RTrq[1]', 'L10RTrq[2]', 'L10RTrq[3]', 'TIME', 'YawRev', 'YawRevVel', 'YawRevAcc', 'YawDrvTrq', 'NoddRev', 'NoddAcc']
    
    assert np.all(sensors == sensors_expected )

def test_get_sensor():
    result_file = AlaskaH5ResultFile(TEST_DATA / 'RWT_LC2.hdf5')
    sensor1 = result_file.get_sensor('L40RFrc[1]')
    sensor2 = result_file.get_sensor('NoddRev')

    #print(f"{sensor1}")
    #print(f"{sensor2}")
    
    sensor1_expected = np.array([ -43440.96788454089,  -53464.66468858088,  -79714.09755055935, -114811.72764138291, -148988.812437636])
    sensor2_expexted = np.array([0., 0., 0., 0., 0.])
    assert np.all( sensor1 == sensor1_expected ) and np.all(sensor2 == sensor2_expexted)

def test_load_results():
    
    result_file = AlaskaH5ResultFile(TEST_DATA / 'RWT_LC2.hdf5')
    data, header, unit = result_file.load_simulation_results('Blade1')
    
    print(f"{header}")
    print(f"{unit}")

    header_expected = ['TIME', 'L1RFrc[1]', 'L1RFrc[2]', 'L1RFrc[3]', 'L1RTrq[1]', 'L1RTrq[2]', 'L1RTrq[3]', 'L40RFrc[1]', 'L40RFrc[2]', 'L40RFrc[3]', 'L40RTrq[1]', 'L40RTrq[2]', 'L40RTrq[3]', 'L80RFrc[1]', 'L80RFrc[2]', 'L80RFrc[3]', 'L80RTrq[1]', 'L80RTrq[2]', 'L80RTrq[3]', 'AF1FL', 'AF1FD', 'AF1T', 'AF40FL', 'AF40FD', 'AF40T', 'AF80FL', 'AF80FD', 'AF80T', 'AF1AoA', 'AF1a', 'AF40AoA', 'AF40a', 'AF80AoA', 'AF80a', 'N40Pos[1]', 'N40Pos[2]', 'N40Pos[3]', 'N84Pos[1]', 'N84Pos[2]', 'N84Pos[3]', 'Azimuth']
    unit_expected = ['s', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    assert np.all(header == header_expected) and np.all(unit == unit_expected)
