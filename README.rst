Instructions
============

Get the code:

.. code-block:: bash

    git clone https://github.com/ezag/gamebook.git
    cd gamebook

Set up virtualenv and install dependencies:

.. code-block:: bash

    cd gamebook
    virtualenv .env
    source .env/bin/activate
    pip install -r requirements.txt

Run on example input (downloaded from
http://www.nflgsis.com/2015/reg/01/56505/Gamebook.pdf):

.. code-block:: bash
    
    python gamebook.py < examples/Gamebook.pdf

You should get following output at stderr:

.. code-block:: none

    Looking for page with Playtime Percentage...
      page 1... not found
      page 2... not found
      page 3... not found
      page 4... not found
      page 5... not found
      page 6... not found
      page 7... not found
      page 8... not found
      page 9... not found
      page 10... not found
      page 11... not found
      page 12... not found
      page 13... not found
      page 14... not found
      page 15... not found
      page 16... not found
      page 17... found

At stdout:

.. code-block:: none

    player               position   off_snaps    off_pct     

    J Sitton             G          59           100%        
    T Lang               G          59           100%        
    B Bulaga             T          59           100%        
    A Rodgers            QB         59           100%        
    D Bakhtiari          T          59           100%        
    C Linsley            C          59           100%        
    D Adams              WR         57           97%         
    J Jones              WR         54           92%         
    R Cobb               WR         53           90%         
    E Lacy               RB         45           76%         
    R Rodgers            TE         37           63%         
    A Quarless           TE         23           39%         
    J Starks             RB         13           22%         
    J Kuhn               FB         7            12%         
    J Walker             G          3            5%          
    J Tretter            C          1            2%          
    J Janis              WR         1            2%          
    T Montgomery         WR         1            2%          
    H Clinton-Dix        FS                             
