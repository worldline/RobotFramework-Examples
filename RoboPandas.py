import pandas as pd
from pandas import *
from sqlalchemy import create_engine
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from fnmatch import fnmatch
import numpy
from itertools import islice

def dataframe(dataframe_dict, index=None, dtype=object, **kwargs):
    """
    Creates a dataframe based on the inserted dictionary
    Dict should follow format key: [list of values], even if only 1 value
    Note that all values should have the same length
    e.g. a dict of {'a':[1,2], 'b':[3,4]} will work
    but {'a':[1,2,7], 'b':[3,4]} will not
    Optional argument is index, which can be one column name
    or multiple column names in a list
    """
    df = pd.DataFrame(dataframe_dict, dtype=dtype, **kwargs)
    if index:
        set_index(df, index)
    return df

def create_dataframe(*args, to_dict=None, set_index=None):
    """Create a dataframe from the arguments.
    
    The keyword needs to know how many columns there are and be able to distinguish column headers from column values.
    To be able to count the column headers, a separator argument "--" is used after all the header arguments and before the data.
    The remaining data arguments must be a multiple of the number of headers.

    An index can be set by using the keyword argument set_index.
    
    Robot framework dictionary notation ${mydict}[value] requires dictionaries. To use this notation, the to_dict option
    can be used to convert the dataframe to a dictionary structure. The column name for the index can be specified
    to this argument and the default orientation 'index' will be used. When another orientation is needed
    (documented here: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html), the index column
    should be specified in the separate set_index argument and the orientation given in to_dict.
    """

    source = iter(args)
    col_names = list()
    while not (col_name := next(source)) == '--':
        col_names.append(col_name)
    rows = tuple(row for row in iter(lambda: tuple(islice(source, len(col_names))), ()))
    df = pd.DataFrame(numpy.array(rows), columns=col_names)
    if to_dict and not to_dict in ('dict', 'list', 'series', 'split', 'records', 'index') and not set_index:
        set_index = to_dict
        to_dict = 'index'
    if set_index:
        df['_idx_'] = df[set_index]
        set_index = '_idx_'
        df.drop_duplicates(subset=[set_index], inplace=True)
        df = df.set_index(set_index)
    if to_dict:
        df = df.to_dict(to_dict)
    return df

def create_dataframe_from_table(table, db_url, schema=None,
                                index=None, return_columns=None):
    """
    Creates a dataframe from the database table
    Arguments are the table name and the database url

    Optionally the database schema can be given, the return_columns
    which are to be returned and an index (single column) or a
    multi-index (list of columns) can be set

    More information about the database url can be found at
    https://docs.sqlalchemy.org/en/latest/core/engines.html
    """
    #maybe good to use a global connection with a
    #connect_to_database and disconnect_from_database keyword
    table = table.lower()
    if schema:
        schema = schema.lower()
    if return_columns:
        if isinstance(return_columns, list):
            return_columns = [i.lower() for i in return_columns]
        else:
            return_columns = [return_columns.lower()]
    if index:
        if isinstance(index, list):
            index = [i.lower() for i in index]
        else:
            index = index.lower()
    conn = create_engine(db_url).connect(close_with_result=True)
    df = pd.read_sql_table(table, conn, schema=schema,
                            columns=return_columns, index_col=index)
    return df

def create_dataframe_from_query(query, db_url, index=None):
    """
    Creates a dataframe from the query results
    Arguments are the query and the database url

    Optionally an index (single column) or a
    multi-index (list of columns) can be set

    More information about the database url can be found at
    https://docs.sqlalchemy.org/en/latest/core/engines.html
    """
    #maybe good to use a global connection with a
    #connect_to_database and disconnect_from_database keyword
    if index:
        if isinstance(index, list):
            index = [i.lower() for i in index]
        else:
            index = index.lower()
    conn = create_engine(db_url).connect(close_with_result=True)
    df = pd.read_sql_query(query, conn, index_col=index)
    return df

def read_excel(excel, sheet_name, set_index=None, to_dict=None, query=None, noreplace=None, **kwargs):
    """
    Converts an excel sheet to a dataframe
    Arguments are the excel and the sheet that is to be converted

    Optional arguments are:
    - return_columns, can be one column or a list of columns
    Note that column values can only be used in combination with set headers
    Otherwise numeric values have to be used
    - set_index, (default None) can be a column for a single index
    or a list of columns for a multi-index
    - skiprows, starting from the first row, which rows to ignore
    - header: starting from 0, which row to use as header
    This is done after ignore_rows
    - nrows, how many rows to get max
    This is not including the header row if there is one
    - to_dict: can be 'records' to return list of records. Other values are in the
    documentation for DataFrame.to_dict

    Additional options as documented in the pandas library are available here:
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html

    Robot Framework variables in the spreadsheet are resolved as
    the sheet is read in. This behaviour can be disabled with the option:
    - noreplace=*
    noreplace can also match column names using patterns (with * and ? wildcards)
    separated with a ;
    """
    for arg in kwargs:
        if arg in ('header', 'nrows'):
            kwargs[arg] = int(kwargs[arg])

    if noreplace == '*':
        converters=None
    else:
        columns = pd.read_excel(excel, sheet_name=sheet_name, nrows=0).columns
        replacer = lambda value:BuiltIn().replace_variables(value) if isinstance(value, str) and '${' in value else value
        if noreplace:
            converters = {col: replacer for col in columns
                      if not any(filter(lambda pat:fnmatch(col, pat), noreplace.split(';')))}
        else:
            converters = {col: replacer for col in columns}

    df = pd.read_excel(excel, sheet_name=sheet_name, converters=converters, **kwargs)

    if query:
        df = df.query(query)

    if set_index:
        df['_idx_'] = df[set_index]
        set_index = '_idx_'
        df.drop_duplicates(subset=[set_index], inplace=True)
        df = df.set_index(set_index)

    if to_dict:
        return df.to_dict(to_dict)

    return df

def set_index(df, index, append=False, inplace=True):
    """
    Turns one, or multiple dataframe columns into an index
    Arguments are the dataframe to be modified, as well as a column name
    or multiple column names in a list

    Optional arguments are;
    - append (default False, can be True or False) which determines whether
    to append the index to the existing index
    - inplace (default True, can be True or False) which determines whether
    to change the existing dataframe, or return a new dataframe

    Note that if append is not true, the original index will be dropped
    """
    df = df.set_index(index, append=append, inplace=inplace)
    return df

def reset_index(df, drop_index_columns=True, inplace=True):
    """
    Resets the index of the given dataframe
    Optional arguments are
    - drop_index_columns (default True, can be True or False) which can be used
    to drop or keep the column(s) that are used as the index
    - inplace (default True, can be True or False) which determines whether
    to change the existing dataframe, or return a new dataframe
    """
    df = df.reset_index(drop=drop_index_columns,inplace=inplace)
    return df

def add_dataframe_column(df, column, values):
    """
    Will add a new column to the given dataframe
    Arguments are the dataframe, column name
    and a list of values
    The value count must match the row count
    """
    df[column] = values
    return df

def drop_dataframe_columns(df, columns, inplace=True):
    """
    Drops the columns in the dataframe
    Arguments are the dataframe and the columns (in list format)
    Optionally, inplace can be set (default True, can be True or False) which
    determines whether to change the existing dataframe, or return a new dataframe
    """
    df.drop(columns=columns, inplace=inplace)
    return df

def merge_dataframes_with_same_key_names(dataframe1, dataframe2, key_names, merge_type='inner',
                                            suffixes=['_df1', '_df2'], sort=False):
    """
    Will join the first dataframe and right dataframe, based on the key(s)
    These keys should have the same names in both dataframes
    If that is not the case, use Merge Dataframes With Different Key Names instead
    Default arguments are the dataframes and the key, or list of keys, to merge them on
    Optional  arguments are:
    - merge_type (inner, left, right or outer, inner by default)
    - suffixes (list like, default '_df1', '_df2')
    - sort (True or False, default False)
    """
    df = dataframe1.merge(dataframe2, on=key_names, how=merge_type, suffixes=suffixes, sort=sort)
    return df

def merge_dataframes_with_different_key_names(dataframe1, dataframe2, key_names_left, key_names_right,
                                            merge_type='inner', suffixes=['_df1', '_df2'], sort=False):
    """
    Will join the first dataframe and right dataframe, based on the left and right key(s)
    These keys should have different names in both dataframes
    If that is not the case, use Merge Dataframes With Same Key Names instead
    Default arguments are the dataframes, the left key and the right key
    Multiple keys can be given by putting them in a list, but make sure the order is correct
    Optional  arguments are:
    - merge_type (inner, left, right or outer, inner by default)
    - suffixes (list like, default '_df1', '_df2')
    - sort (True or False, default False)
    """
    df = dataframe1.merge(dataframe2, left_on=key_names_left, right_on=key_names_right,
                            how=merge_type, suffixes=suffixes, sort=sort)
    return df

def use_loc(df, statement):
    """
    Due to some weird interaction between pandas and Robot Framework,
    loc doesn't always work the way it's intended
    So this keyword exists to work around that
    Arguments are the dataframe and the loc statement that you want to do
    """
    return df.loc[statement]

def use_map(df, column, map_df):
    """
    Due to some weird interaction between pandas and Robot Framework,
    map doesn't always work the way it's intended
    So this keyword exists to work around that
    Arguments are the dataframe, column and dataframe you want to map
    """
    return df[df[column].map(map_df, na_action='ignore')]

def query_dataframe(dataframe, query, return_columns=None, offset=0):
    """
    Find a row, or multiple rows through the query
    Arguments are the dataframe to be searched and the query to be done
    The query should follow the Pandas query format

    Optionally, an offset can be used to ignore the first x results
    and the columns to be returned can be set
    If multiple columns are to be returned, put them in a list

    Examples:
    Equal to:           A=="value1" and B=="value2"
    Bigger/Smaller:     A < 7 or B > 5
    In a list of vars:  C in ("15", "22", "18")
    Not null check:     D == D

    Make sure to use quotes around the values inside the query

    Learn more at http://jose-coto.com/query-method-pandas
    """
    df = dataframe.query(query)
    if return_columns:
        df = df[return_columns]
    return df[offset:]

def get_dataframe_head(dataframe, number=5):
    """
    Gets the first number of results (5 by default) from the dataframe
    Arguments are the dataframe and the first number of rows to return
    Number can also be a negative amount, in which case it will
    return everything but the last number of rows
    """
    df = dataframe.head(number)
    return df

def get_dataframe_tail(dataframe, number=5):
    """
    Gets the last number of results (5 by default) from the dataframe
    Arguments are the dataframe and the last number of rows to return
    Number can also be a negative amount, in which case it will
    return everything but the first number of rows
    """
    df = dataframe.tail(number)
    return df

def sort_dataframe(dataframe, sort_column, order='ascending', nulls_position='last', inplace=True):
    """
    Sort the dataframe by the sort column
    Arguments are the dataframe and column that you want to sort by
    Optional arguments are:
    - order (default ascending, can be ascending or descending) which determines
    whether to sort by the column ascending or descending
    - nulls_position (default last, can be first or last) which determines
    whether null values (NaN) are sorted first or last
    - inplace (default True, can be True or False) which determines whether
    to change the existing dataframe, or return a new dataframe
    """
    if order == 'ascending':
        ascending = True
    else:
        ascending = False
    df = dataframe.sort_values(sort_column, ascending=ascending, na_position=nulls_position, inplace=inplace)
    if not inplace:
        return df
