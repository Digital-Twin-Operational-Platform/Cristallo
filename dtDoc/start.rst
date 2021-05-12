Get started
+++++++++++++++++++++++++++

Updated version of the DTOP code with some plotting and front end code examples

Clone our repository using:

.. code-block:: shell-session

    $ git clone git@github.com:Digital-Twin-Operational-Platform/dtop3.git

On MacOS/Linux:

.. code-block:: shell-session

    $ python3 -m venv venv

    $ source venv/bin/activate

    (venv) % pip install -r requirements.txt

    (venv) % export FLASK_APP=run.py

    (venv) % export FLASK_DEBUG=1

    (venv) % flask run


On Windows10:

.. code-block:: shell-session

    % python -m venv venv

    % venv\Scripts\activate

    (venv) % pip install -r requirements.txt

    (venv) % set FLASK_APP=run.py

    (venv) % set FLASK_ENV=development

    (venv) % flask run


Then in a web browser navigate to http://localhost:5000/

To know more about how to get started in Flask, see the official `documentation`_ page.

.. _documentation: https://flask.palletsprojects.com/en/1.1.x/quickstart/