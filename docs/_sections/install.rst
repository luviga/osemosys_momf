Installation
===============


Clone Repository
----------------

All source code for MOMF is available in a `GitHub repository 
<insert repository link here>`__.

To clone the repository using **HTTPS**, use the command below:

.. code:: bash

   $ git clone [insert HTTPS link here]

For cloning using **SSH**, execute the following command. 
Please ensure that you have already configured an **SSH key** 
by following the `instructions provided by GitHub 
<https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account>`__.

.. code:: bash

   git clone [insert ssh key here]

Dependencies
------------
MOMF utilizes a variety of tools. We encourage you 
to explore the following key programs and packages 
that are integral to our processes:

`Python <https://www.python.org/downloads/>`__
   Utilized for all data processing tasks within 
   the Python programming language.

`otoole <https://github.com/OSeMOSYS/otoole>`__
   A Python-based command line tool for managing 
   OSeMOSYS data models.

`GLPK <https://www.gnu.org/software/glpk/>`__
   An open-source toolkit for linear programming.

`CBC <https://github.com/coin-or/Cbc>`__
   An open-source solver for linear programming problems.

`Microsoft Visual C++ Build Tools <https://visualstudio.microsoft.com/downloads/>`__
   During installation, select "Desktop development with 
   C++" to include all necessary tools. 
   Ensure "MSVC v142 - VS 2019 C++ x64/x86 build tools" 
   and "Windows 10 SDK" are checked.
   Is optional but usually is needed to use CBC in Windows.

Note
^^^^
Also, the model has dependencies of some Python
package. You need to check `requirements.txt`
could find in the a `GitHub repository 
<insert repository link here>`__


Test Installation of Solvers
----------------------------

MOMF is compatible with multiple solvers; among them are
`GLPK <https://www.gnu.org/software/glpk/>`__,
`CBC <https://github.com/coin-or/Cbc>`__, and 
`CPLEX <https://www.ibm.com/analytics/cplex-optimizer>`__.
OSeMOSYS particularly employs `GLPK` for generating 
solver-independent linear programming files. 

GLPK Test
^^^^^^^^^

`GNU GLPK <https://www.gnu.org/software/glpk/>`__ is a freely available package for linear programming that **comes pre-installed with the environment**. OSeMOSYS utilizes it for generating linear programming files. Verify its installation by executing `glpsol` in your terminal, which should display the following message confirming that GLPK is properly installed:

.. code:: bash

   ~/ $ glpsol

   GLPSOL: GLPK LP/MIP Solver, v4.65
   No input problem file specified; try glpsol --help

CBC Test
^^^^^^^^

`CBC <https://github.com/coin-or/Cbc>`__ is an open-source linear program solver that **is also installed with the environment**. To check its installation, run `cbc` in the terminal. You should see the following output confirming CBC's installation:

.. code:: bash

   ~/ $ cbc

   Welcome to the CBC MILP Solver
   Version: devel
   Build Date: Apr 27 2021

   CoinSolver takes input from arguments ( - switches to stdin)
   Enter ? for list of commands or help
   Coin:

To install a different version of CBC, refer to the `installation instructions <https://github.com/coin-or/Cbc#download>`__ on CBC's GitHub page.

CPLEX Test
^^^^^^^^^^^^^^^^^^

Academic researchers or students may be eligible for IBM's CPLEX optimizer through an `academic license <https://www.ibm.com/academic/topic/data-science>`__. Otherwise, a `commercial license <https://www.ibm.com/support/pages/downloading-ibm-ilog-cplex-optimization-studio-v1290>`__ will be necessary. After installation, verify by running `cplex` in the command line. The following output should appear, indicating a successful installation:

.. code:: bash

   ~/ $ cplex

   Welcome to IBM(R) ILOG(R) CPLEX(R) Interactive Optimizer 22.1.1.0
     with Simplex, Mixed Integer & Barrier Optimizers
   5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55 5655-Y21
   Copyright IBM Corp. 1988, 2022.  All Rights Reserved.

   Type 'help' for a list of available commands.
   Type 'help' followed by a command name for more
   information on commands.


