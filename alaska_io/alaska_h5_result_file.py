import h5py    

class AlaskaH5ResultFile:
    """
    hdf5 alaska result file wrapper.
    Holds content and provides access utilities.
    
    Attributes
    ----------
    filename : str or Path
        filename of hdf5 result file
    """
    
    filename : str | None
    groups : list[str]
    groupheader : list[list[str]]

    def __init__(self, filename : str = None) -> None:
        self.filename = ""
        self.groups = []
        self.groupheader = []
        
        if filename is not None: 
            self.filename = filename
            self._build_sensor_index()
        
        
    def _build_sensor_index(self) -> None:
        self.groups = []
        self.groupheader = []
        with h5py.File(self.filename, 'r') as f:
            for name, obj in f.items():

                if isinstance(obj, h5py.Group):
                    self.groups.append(name)
                    groupheader = f[name]["head"][:]                    
                    groupheader_str = [x.decode('utf-8') for x in groupheader]
                    self.groupheader.append(groupheader_str)

    def get_sensor_names(self) -> list[str]:
        """
        retrieve all sensor names contained in hdf5 data set ( = header of all hdf5-groups)
                
        Returns
        -------
         : list[str]
            list of all sensor names
        """
        return [
                header
                for group in self.groupheader
                for header in group
                ]

    def load_simulation_results(self, group_name : str = None):
        """
        loads alaska simulation data of group with group_name
        - if group_name is None: content of first group of hdf5 file will be returned
        
        Parameters
        ----------
        group_name : str or None
            name of group of simulation results
            
        Returns
        -------
        data : numpy.ndarray
            full data set of simulation results (all contained sensors as time series) in specified group
        
        header : list[str]
            header = name of sensors in data group
        
        units : list[str]
            units of all sensors if specified
        """
        data = []
        if self.filename is None:
            print("Variable for result file name is 'None'")
            return
        if group_name is None:
            group_name = self.groups[0]
        if group_name not in self.groups:
            print(f"Can not load data from group '{group_name}' of result file '{self.filename}'. Group not found!")
            return
        print(f"Loading data set '{group_name}' of result file '{self.filename}'.")
        with h5py.File(self.filename, 'r') as f:
            data = f[group_name]["value"][:]
            header = f[group_name]["head"][:]
            units = f[group_name]["units"][:]
        
        return data, [x.decode('utf-8') for x in header] , [x.decode('utf-8') for x in units]

                    
    def get_sensor(self, sensor_name) :
        """
        loads alaska simulation data of given sensor name
        - returns corresponding time series of sensor , if sensor_name is found in any header of all hdf5-groups
        
        Parameters
        ----------
        sensor_name : str 
            name of sensor
            
        Returns
        -------
        data : numpy.ndarray
            time series of sensor as vector in numpy.ndarray format
        """
    
        if sensor_name not in self.get_sensor_names():
            print(f"Sensor {sensor_name} not found in result file '{self.filename}'!")
            return
        for ind , obj in enumerate(self.groups):
            if sensor_name in self.groupheader[ind]:
                sensor_col = self.groupheader[ind].index(sensor_name)
                with h5py.File( self.filename, 'r') as f:
                    return f[self.groups[ind]]["value"][:,sensor_col]
