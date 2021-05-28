#  Digital Twin Operational Platform: DTOP-Cristallo

This operational platform is web-based and the user interface is provided using webpages.This version is designed to be used on a standalone machine, and is primarily aimed at demonstrating how this type of digital twin might be applied to a specific engineering application. In this code, the application structure is a 3-storey building. Code for recording data has not been included here, as this needs to be specific to the data acquisition hardware connected to the physical twin. Instead, in the spirit of demonstrating the concept, data is either simulated or in some cases pre-recorded experimental data is used.

## Getting started

### Prerequisites

This code requires python 3.8 or later, and a code editing system such as VS code or similar.

### Installing

To install the code, first clone the repository using: 
``` bash
$ git clone git@github.com:Digital-Twin-Operational-Platform/cristallo.git
```

On MacOS/Linux:

``` bash
$ python3 -m venv venv 

$ source venv/bin/activate

(venv) $ pip install -r requirements.txt

(venv) $ export FLASK_APP=run.py

(venv) $ export FLASK_ENV=development

(venv) $ export FLASK_DEBUG=1

(venv) $ flask run
```


On Windows10:

``` bash
$ python -m venv venv

$ venv\Scripts\activate

(venv) $ pip install -r requirements.txt

(venv) $ set FLASK_APP=run.py

(venv) $ set FLASK_ENV=development

(venv) $ set FLASK_DEBUG=1

(venv) $ flask run
```

On Windows10 using VSCode with PowerShell:

``` bash
$ python -m venv v-env
```
You have to enable running scripts. Run PowerShell as Administrator and type "Set-ExecutionPolicy -ExecutionPolicy AllSigned". Then ypu can run the 'activate' script.

``` bash
$ v-env\Scripts\activate

(v-env) $ pip install -r requirements.txt

(v-env) $env:FLASK_APP="run.py"

(v-env) $env:FLASK_ENV="development"

(v-env) $env:FLASK_DEBUG=1

(v-env) $ flask run
```

Then in a web browser navigate to <http://localhost:5000/> where the DTOP webpages should be available.

Please refer to the documentation for more detailed information.
