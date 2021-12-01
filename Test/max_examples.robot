*** Settings ***
Library    Examples    max_examples=2
Suite Setup      Set Global Variable    ${cnt}    ${0}
Test teardown    Set Global Variable    ${cnt}    ${cnt + 1}
Suite teardown   Should Be Equal        ${cnt}    ${2}

*** Test cases ***
My test with examples for ${name}
    Log    Hello ${name}, welcome to ${where welcome}    console=True
    
    Examples:    name      where welcome    --
            ...    Joe       the world!
            ...    Arthur    Camelot (clip clop).
            ...    Patsy     it's only a model!"""
