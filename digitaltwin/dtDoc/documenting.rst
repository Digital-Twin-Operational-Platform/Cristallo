Write more documentation
+++++++++++++++++++++++++++++++

If you wanna write more documentation or simply document your new page this is the place of start.

This documentation is semi-automatically generated using `Sphinx`_. 
So developers do not need to worry about the documentation, but need only worry about documenting their code. 

.. _Sphinx: https://www.sphinx-doc.org/en/master/index.html


This page illustrates what needs to be done from the developers' side in order to document the code. 

What files can be documented?
=============================

Only Python files can be documented with the Sphinx engine. So any file having the ``.py`` extension. 

If there is a need to document another file with extension say ``.html`` or ``.js`` then this needs to be done manually as a standalone ``.rst`` file. 
Sumbit your standalone documentation file to the administrator of the project, who will take care to integrate and build it within the documentation. 



Where should the documentation text go? 
========================================

The Sphinx engine will pick up only the *docstring* that are at **the very top** of your ``file.py``. See the example below:

.. code-block:: python
    :linenos:

    ''' 
    Title (Heading)
    ================
    
    This text will appear in the documentation. 
    ''' 

    from flask import render_template, request, redirect, url_for  # file.py starts here.

Also *docstrings* at the beginning of a function will be rendered by the documentation engine:


.. code-block:: python
    :linenos:

    def myfun():
        ''' 
        My function (Heading)
        ================
        
        This text will appear in the documentation. 
        ''' 

        pass  # myfun starts here.


How is the text going to be formatted?
======================================

The text will be interpreted as *reStructuredText* (reST) which is the default plaintext markup language used by Sphinx.


Check out the this `page`_ for a a brief introduction to reST concepts and syntax.

.. _page: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html



Following is some common syntax you may want to use in your page:

* Headings and sub-headings

.. code-block:: python
    :linenos:

    ''' 
    =================
    Chapter (Heading)
    =================

    Title (Sub-heading)
    ===================
    
    This text will appear in the documentation. 
    ''' 

* Emphasis

.. code-block:: python

    ''' 
    *text* for emphasis (italics),
    **text** for strong emphasis (boldface), and
    ``text`` for code samples.
    ''' 

* Code block
  
.. code-block:: python

    ''' 
    .. code-block:: python

        import numpy

    ''' 


* Tables 
  
.. code-block:: python

    '''
    +------------------------+------------+----------+----------+
    | Header row, column 1   | Header 2   | Header 3 | Header 4 |
    | (header rows optional) |            |          |          |
    +========================+============+==========+==========+
    | body row 1, column 1   | column 2   | column 3 | column 4 |
    +------------------------+------------+----------+----------+
    | body row 2             | ...        | ...      |          |
    +------------------------+------------+----------+----------+
    '''

* External links

.. code-block:: python

    '''

    This is a paragraph that contains `a link`_.

    .. _a link: https://domain.invalid/.

    '''


* Field list

.. code-block:: python

    def my_function(my_arg, my_other_arg):
        """A function.

        :param my_arg: The first of my arguments.
        :param my_other_arg: The second of my arguments.

        :returns: A message (just for me, of course).
        """

another *field list*

::

    :Authors: 
    Tony J. (Tibs) Ibbs, 
    David Goodger

    (and sundry other good-natured folks)

    :Version: 1.0 of 2001/08/08 
    :Dedication: To my father.

* Comments

.. code-block:: python

    '''

    .. This is a comment.   

    '''


* List and Quote blocks

.. code-block:: python

    '''

    * This is a bulleted list.
    * It has two items, the second
    item uses two lines.

    1. This is a numbered list.
    2. It has two items too.

    #. This is a numbered list.
    #. It has two items too.
    
    '''



