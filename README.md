#  Welcome to Cristallo! 

*Cristallo* is an open-source web-based _digital twin operational platform_ (DTOP). User interaction is currently provided via webforms. This version works best on a standalone machine, and is primarily aimed at demonstrating how this type of digital twin can be applied to a specific engineering application. In this code, the application structure is a 3-storey structure. 

>Disclaimer: The repository does not include code for recording data, because of the hardware-specific nature of such code. In the spirit of demonstrating the concept, data is either simulated or in some cases pre-recorded experimental data is used.   
   
# Installation 
The DTOP runs on any machine with a modern browser. There are no proprietary barriers preventing users to access the software. 
This section will guide you through a few main steps to install Cristallo on your machine. Cristallo is powered by Python 3, so before you begin, make sure you have Python 3 installed on your machine. 

> Best performance with python 3.8+

## Download
Download or clone this repository on your local machine. For a visual walkthrough on how to download and run, visit https://www.youtube.com/watch?v=-l04b4dEypo

> Skip the following instructions if you are familiar with GitHub.

If you don't have git and a Github account, just click on the code green button at the top of this page and hit Download. This will zip and download the code in your designated downloads folder. Then, open a code editor in the unzipped downloaded folder.

If you have git but not a Github account, or if you don't have Github SSH keys, then clone the repo with: 

```bash
git clone https://github.com/Digital-Twin-Operational-Platform/Cristallo.git
```

If you have GitHub SSH keys you know what you are doing and you can move ahead. 

## Virtual environment
Before we install the required dependencies, we need a new virtual environment, i.e. a safe copy of your installed Python distribution. 

> But why? Python 3 is often used by your machine to perform essential tasks. Creating a virtual environment will prevent installing dependencies that your OS does not need, which can conflict with your computer system (a.k.a. dependency hell). In other words, the Python used by your OS will be fully orthogonal to the Python used in your project. 

To create the virtual environment (1) locate the executable of your Python3 system distrubution, and (2) invoke the following CLI command:

```bash
python3 -m venv venv 
```

If your Python3 distribution is not in your PATH, you may need to replace `python3` with the full path. For example on Windows:

```bash
C:/Users/mda/AppData/Local/Programs/Python/Python39/python.exe -m venv venv 
```
or on MacOS:


```bash
/usr/local/bin/python3 -m venv venv 
```

This will create the folder `venv` in your current directory. This folder need not be located inside the downloaded repository. 

>If you go ahead and create the `venv` folder in the downloaded repository then make sure it is detached from version control. 

### Activate your virtual environment

From the same directory, invoking the following command will activate the virtual environment:

MacOS/Linux:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

Successful execution of the above CLI command will result in the prompt displaying the name of the environment `venv` before the prompt line, as such

MacOS/Linux:
```bash
# MacOS/Linux
(venv) cristallo % 
# Windows:
(venv) C:\cristallo> 
```

## Dependencies
There are four main dependencies that need to be installed separately:
1. Flask
2. Scipy 
3. Plotly
4. Wtforms

We can install these dependencies by `pip install`. `pip` will take care to install all the related dependencies that these packages need in order to function. 

```bash
(venv) C:\cristallo> pip install flask scipy plotly wtforms
```

`pip install flask` will automatically install the following:
``zipp, MarkupSafe, colorama, Werkzeug, Jinja2, itsdangerous, importlib-metadata, click, flask``

`pip install scipy` will automatically install the following: ``numpy, scipy``

`pip install plotly` will automatically install the following: ``six, tenacity, plotly``

You can also install all the dependencies in one go with the following CLI command:

```bash
(venv) C:\cristallo> pip install -r requirements.txt
```

In `requirements.txt` all the individual dependencies are spelled out in a list. This file is a snapshot of the list of dependencies at a particular point in time, i.e. the moment the `requirements.txt` was created. 

At this particular moment (April 2022) the `requirements.txt` looks as follows: 

```txt
click==8.1.2
colorama==0.4.4
Flask==2.1.1
importlib-metadata==4.11.3
itsdangerous==2.1.2
Jinja2==3.1.1
MarkupSafe==2.1.1
numpy==1.22.3
plotly==5.7.0
scipy==1.8.0
six==1.16.0
tenacity==8.0.1
Werkzeug==2.1.1
WTForms==3.0.1
zipp==3.8.0
```
This is how `requirements.txt` is supposed to look like for the current version of the project. 

> Using the `pip install -r requirements.txt` CLI command is only reccommended to install the dependencies if your `venv` is set up correctly. 


## Running the Flask server
Finally, we can give Cristallo a go by starting the Flask server.

``` bash
# MacOS/Linux:
(venv) cristallo% export FLASK_APP=run.py
(venv) cristallo% export FLASK_DEBUG=1
(venv) cristallo% flask run

# PowerShell (Windows)
(venv) C:\cristallo> $env:FLASK_APP=".\run.py"
(venv) C:\cristallo> $env:FLASK_DEBUG=1
(venv) C:\cristallo> flask run

# Windows:
(venv) C:\cristallo> set FLASK_APP=run.py
(venv) C:\cristallo> set FLASK_DEBUG=1
(venv) C:\cristallo> flask run
```

The successful excecution of this CLI sequence will start the flask server, which will output the following console message:

```bash
 * Serving Flask app 'run.py' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 169-144-882
```

Now you can navigate to the URL `http://localhost:5000/` via your browser to access the DTOP.

# Cite 
>Bonney, M., De Angelis, M., Dal Borgo, M., Andrade, L., Beregi, S., Jamia, N., & Wagg, D. (2022). Development of a digital twin operational platform using Python Flask. Data-Centric Engineering, 3, E1. doi:10.1017/dce.2022.1

```BibteX
@article{bonney_de angelis_dal borgo_andrade_beregi_jamia_wagg_2022, 
title = {Development of a digital twin operational platform using Python Flask},
volume = {3}, 
DOI = {10.1017/dce.2022.1}, 
journal = {Data-Centric Engineering}, 
publisher = {Cambridge University Press}, 
author = {Bonney, Matthew S. and de Angelis, Marco and Dal Borgo, Mattia and Andrade, Luis and Beregi, Sandor and Jamia, Nidhal and Wagg, David J.}, 
year = {2022}, 
pages = {e1}}
```

# More
Instructions on how to contribute to the project as adeveloper can be consulted via our documentation.

## Links

documentation: https://digital-twin-operational-platform.github.io/
github: https://github.com/Digital-Twin-Operational-Platform/Cristallo/
