Project folders
=======================

.. code-block:: python

    '''.
    ├── README.md
    ├── config.py             # DTOP app configuration
    ├── dtApp                 # Flask code folder for the dtop app
    │   ├── __init__.py
    │   ├── dtCode
    │   │   ├── __init__.py
    │   │   ├── control.py
    │   │   ├── dplot.py
    │   │   ├── dplot2.py
    │   │   ├── dplot3.py
    │   │   ├── dtopstruc.py
    │   │   └── prop.py
    │   ├── dtData
    │   │   ├── data_th_harmonic.csv
    │   │   ├── data_th_impulse.csv
    │   │   ├── data_th_noise.csv
    │   │   └── soton_twin.py
    │   ├── routes.py
    │   ├── static            # Static web content
    │   │   ├── css           # Style sheets for web content
    │   │   ├── img           # Static images in this folder
    │   │   └── txt           # Text only (like this file)
    │   └── templates         # html pages
    │       ├── base.html
    │       ├── control.html
    │       ├── dashboard.html
    │       ├── docs.html
    │       ├── dplot.html
    │       ├── dplot2.html
    │       ├── dtop3.html
    │       ├── dtopstruc.html
    │       ├── dtwin.html
    │       ├── home.html
    │       └── propagation.html
    ├── dtDoc                 # Documentation folder
    ├── dtLib                 # Scientific code library
    │   ├── __init__.py
    │   ├── general
    │   │   ├── __init__.py
    │   │   └── module1.py
    │   ├── uncertainty
    │   │   ├── __init__.py
    │   │   ├── msd.py
    │   │   └── number.py
    │   └── control
    │       ├── __init__.py
    │       ├── activeStructureVFCideal.py
    │       └── passiveStructure.py
    ├── requirements.txt    # A list of all the required Python packages
    └── run.py              # DTOP app launcher '''
