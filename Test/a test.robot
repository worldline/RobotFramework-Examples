*** Settings ***
Library    Examples

*** Test cases ***
My test with examples for ${name}
    Log    Hello ${name}, welcome to ${where welcome}    console=True
    
    Examples:    name      where welcome    --
            ...    Joe       the world!
            ...    Arthur    Camelot (clip clop).
            ...    Patsy     it's only a model!"""
