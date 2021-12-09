*** Settings ***
Library    Examples    autoexpand=Off
Library    Collections
Suite Setup      Setup this suite

*** Test cases ***
My test with examples for ${name} in ${where welcome}
    Log    Hello ${name}, welcome to ${where welcome}    console=True
    
    Examples:       name      where welcome    --
    ...    @{combos(${names}, ${places})}

Variable dictionary ${Column2Value}

    ${dict}    Create Dictionary    @{{$pick(($column1, $column1value), ($column2, $column2value), ($column3, $column3value))}}
    Log Dictionary    ${dict}

    Examples:
    ...  Column1        Column1Value                   Column2       Column2Value               Column3       Column3Value
    ...    --
    ...    place   Camelot                             name          Arthur                      ${NONE}       ${NONE}
    ...    item    Rosery                              obstacle      Black knight                objective     Holy grail

*** Keywords ***
Setup this suite
    Set Global Variable    ${cnt}    ${0}
    ${names}    Create list    Joe    Arthur    Patsy
    ${places}   Create list    the world!    Camelot (clip clop).    it's only a model!
    ${combos}    Evaluate      lambda *s: list(itertools.chain(*itertools.product(*s)))    modules=itertools
    ${pick}      Evaluate      lambda *pairs:list(map(lambda pair:'{}={}'.format(*pair), filter(lambda pair:pair[0], pairs)))
    Expand test examples   random=2
