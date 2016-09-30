Instructions
============

Get the code:

.. code-block:: bash

    git clone https://github.com/ezag/gamebook.git
    cd gamebook

Set up virtualenv, install dependencies and development tools:

.. code-block:: bash

    virtualenv .env
    source .env/bin/activate
    pip install -r requirements-devel.txt
    pip install -e .

Convert PDF to CSV:

.. code-block:: bash

    gb-pdf-to-csv < tests/pdf/56505.pdf > 56505.csv
    gb-pdf-to-csv < tests/pdf/56918.pdf > 56918.csv
