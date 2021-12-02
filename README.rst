# RobotFramework-Examples

Support for Examples: in Robot Framework like in other BDD style test frameworks

An example of a test case looks like this:

.. code:: robotframework

    *** Settings ***
    Library    Examples

    *** Test cases ***
    My test with examples for ${name}
        Log    Hello ${name}, welcome to ${where welcome}    console=True
    
        Examples:    name      where welcome    --
                ...    Joe       the world!
                ...    Arthur    Camelot (clip clop).
                ...    Patsy     it's only a model!


Keyword information can be found here: `Keywords`_


.. _Keywords: https://worldline.github.io/RobotFramework-Examples
