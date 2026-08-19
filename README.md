# alaska_io

This module contains input and output utilities for alaska. All functionality is put into fully documented classes. Classes are added in __input__.py:

1. `AlaskaXmlFile` , which can read and manipulate simple alaska xml files (containing only tables <TABLE> and variables <STRING>, <REAL> no hierarchy using <Container ) 
2. `AlaskaParameterSetFile`, which can read and manipulate parameter set files
3. `AlaskaH5ResultFile`, simple load functionalities to extract data, header, units 

import statement for the classes: 

```
from alaska_io import AlaskaXmlFile
from alaska_io import AlaskaParameterSetFile
from alaska_io import AlaskaH5ResultFile
```

requirements:

`AlaskaXmlFile` and `AlaskaParameterSetFile`
import shlex
import re
from io import StringIO
import numpy as np
from datetime import datetime

`AlaskaH5ResultFile`
import h5py    