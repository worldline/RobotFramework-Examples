*** Settings ***
Library    Examples    autoexpand=Off
Suite Setup      Setup this suite
Test teardown    Set Global Variable    ${cnt}    ${cnt + 1}
Suite teardown   Should Be Equal        ${cnt}    ${3}

*** Test cases ***
My test with examples for ${name}
    Log    Hello ${name}, welcome to ${where welcome}    console=True
    
    Examples:    name      where welcome    --
            ...    @{{$combos($names, $places)}}

*** Keywords ***
Setup this suite
    Set Global Variable    ${cnt}    ${0}
    ${names}    Create list    Joe    Arthur    Patsy
    ${places}   Create list    the world!    Camelot (clip clop).    it's only a model!
    ${combos}    Evaluate      lambda *s: list(itertools.chain(*itertools.product(*s)))    modules=itertools
    Expand test examples    random=3
