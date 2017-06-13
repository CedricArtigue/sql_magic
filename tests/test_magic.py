import ntpath
import time

import pytest

import sql_magic
from sql_magic.exceptions import EmptyResult

from IPython import get_ipython
from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite

ip = get_ipython()
ip.register_magics(sql_magic.SQL)
sql_magic.load_ipython_extension(ip)

# TODO: NAME to use, db.conn.__name__


connections = []

sqlite_conn = create_engine('sqlite+pysqlite:///test.db', module=sqlite)
ip.all_ns_refs[0]['sqlite_conn'] = sqlite_conn
connections.append('sqlite_conn')

try:
    import pyspark
except:
    pass


@pytest.fixture(scope="module",params=connections)
def conn(request):
    return request.param

def test_query_1(conn):
    ip.run_line_magic('config', "SQL.conn_name = '{conn}'".format(conn=conn))
    ip.run_cell_magic('read_sql', 'df', 'SELECT 1')
    df = ip.all_ns_refs[0]['df']
    assert df.iloc[0, 0] == 1

# def test_python_variable():
#     val = 'this is a python variable'
#     ip.user_global_ns['val'] = val
#     ip.run_line_magic('config', "SQL.conn_name = 'conn'")
#     ip.run_cell_magic('read_sql', 'df', "SELECT '{val}'")
#     df = ip.all_ns_refs[0]['df']
#     assert df.iloc[0, 0] == val
#
# def test_query_1_async():
#     ip.run_line_magic('config', "SQL.conn_name = 'conn'")
#     ip.run_cell_magic('read_sql', 'df -a', 'SELECT "async_query"')
#     df = ip.all_ns_refs[0]['df']
#     assert isinstance(df, str) and (df == 'QUERY RUNNING')
#     time.sleep(0.1)  # need to wait for query to finish
#     df = ip.all_ns_refs[0]['df']
#     assert df.iloc[0, 0] == 'async_query'
#
# def test_query_1_notify():
#     ip.run_line_magic('config', "SQL.conn_name = 'conn'")
#     ip.run_cell_magic('read_sql', 'df -n', 'SELECT 1')
#     df = ip.all_ns_refs[0]['df']
#     assert df.iloc[0, 0] == 1
#
# # def test_invalud_conn_object(sqlite_conn):
# #     with pytest.raises(message="Expecting ZeroDivisionError"):
# #         ip.run_line_magic('config', "SQL.conn_name = 'invalid_conn'")
#
# # def test_commented_query(sqlite_conn):
# #     sql_statement = '''
# #     /* DROP TABLE IF EXISTS TEST; */
# #     /* CREATE TABLE TEST AS SELECT 1; */
# #     /* WITH test AS (SELECT 1) */
# #     /* SELECT 2 */
# #     '''
# #     assert 1 == 2
#
# def test_second_conn_object():
#     # test original
#     ip.run_line_magic('config', "SQL.conn_name = 'conn'")
#     ip.run_cell_magic('read_sql', 'df', 'PRAGMA database_list;')
#     df = ip.all_ns_refs[0]['df']
#     assert ntpath.basename(df.file.iloc[0]) == 'test.db'
#
#     # test new connection
#     conn2 = create_engine('sqlite+pysqlite:///test2.db', module=sqlite)
#     ip.all_ns_refs[0]['conn2'] = conn2
#     # ip.run_line_magic('config', "SQL.conn_name = 'conn2'")
#     ip.run_cell_magic('read_sql', 'df -c conn2', 'PRAGMA database_list;')
#     df = ip.all_ns_refs[0]['df']
#     assert ntpath.basename(df.file.iloc[0]) == 'test2.db'
#
#     # make sure with no argument stays connected to original database
#     ip.run_cell_magic('read_sql', 'df', 'PRAGMA database_list;')
#     df = ip.all_ns_refs[0]['df']
#     connected_to_orig_db = ntpath.basename(df.file.iloc[0]) == 'test.db'
#     assert connected_to_orig_db
#
#
# def test_no_result():
#     ip.run_line_magic('config', "SQL.conn_name = 'conn'")
#     ip.run_cell_magic('read_sql', '_df', 'DROP TABLE IF EXISTS test;')
#     _df = ip.all_ns_refs[0]['_df']
#     assert isinstance(_df, EmptyResult)
#
# def test_query_with():
#     ip.run_line_magic('config', "SQL.conn_name = 'conn'")
#     ip.run_cell_magic('read_sql', 'df', 'WITH test AS (SELECT 1) SELECT 2')
#     df = ip.all_ns_refs[0]['df']
#     assert df.iloc[0, 0] == 2
#
# def test_multiple_sql_statements_var():
#     sql_statement = '''
#     DROP TABLE IF EXISTS TEST;
#     SELECT 1;
#     SELECT 2;
# '''
#     ip.run_cell_magic('read_sql', 'df3', sql_statement)
#     df3 = ip.all_ns_refs[0]['df3']
#     assert df3.iloc[0, 0] == 2
#
# def test_multiple_sql_statements_no_result():
#     ip.run_cell_magic('read_sql', '', 'DROP TABLE IF EXISTS test;')
#     ip.run_cell_magic('read_sql', '', 'CREATE TABLE test AS SELECT 2;')
#     ip.run_cell_magic('read_sql', '', 'SELECT * FROM test')
#     ip.run_cell_magic('read_sql', '_df', 'DROP TABLE IF EXISTS test;')
#     _df = ip.all_ns_refs[0]['_df']
#     assert isinstance(_df, EmptyResult)
#     # assert df2.iloc[0, 0] == 2
