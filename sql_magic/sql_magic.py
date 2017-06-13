import threading

import sqlparse
from IPython.core.magic import Magics, magics_class, cell_magic, needs_local_scope

from .connection import Connection
from . import utils

try:
    from traitlets.config.configurable import Configurable
    from traitlets import observe, validate, Bool, Unicode, TraitError
except ImportError:
    from IPython.config.configurable import Configurable
    from IPython.utils.traitlets import observe, validate, Bool, Unicode, TraitError


available_connection_types = []
no_return_result_exceptions = []  # catch exception if user used read_sql where query returns no result
try:
    import pyspark
    available_connection_types.append(pyspark.sql.context.SQLContext)
    available_connection_types.append(pyspark.sql.context.HiveContext)
    available_connection_types.append(pyspark.sql.session.SparkSession)  # import last;  will fail for older spark versions
except ImportError:
    pass
try:
    import psycopg2
    available_connection_types.append(psycopg2.extensions.connection)
    no_return_result_exceptions.append(TypeError)
except ImportError:
    pass
try:
    import sqlite3
    available_connection_types.append(sqlite3.Connection)
except ImportError:
    pass
try:
    import sqlalchemy
    available_connection_types.append(sqlalchemy.engine.base.Engine)
    no_return_result_exceptions.append(sqlalchemy.exc.ResourceClosedError)
except ImportError:
    pass


DEFAULT_OUTPUT_RESULT = True
DEFAULT_NOTIFY_RESULT = True
@magics_class
class SQL(Magics, Configurable):

    # traits, configurable using %config
    conn_name = Unicode("", help="Object name for accessing computing resource environment").tag(config=True)
    output_result = Bool(DEFAULT_OUTPUT_RESULT, help="Output query result to stdout").tag(config=True)
    notify_result = Bool(DEFAULT_NOTIFY_RESULT, help="Notify query result to stdout").tag(config=True)

    def __init__(self, shell):
        self.shell = shell
        self.caller = None
        self.shell.configurables.append(self)
        Configurable.__init__(self, config=shell.config)
        Magics.__init__(self, shell=shell)
        self.conn = Connection(shell, available_connection_types, no_return_result_exceptions)

    @validate('output_result')
    def _validate_output_result(self, proposal):
        try:
            return bool(proposal['value'])
        except:
            raise TraitError('output_result: "{}" is not accepted. Value must be boolean'.format(proposal['value']))

    @validate('conn_name')
    def _validate_conn_object(self, proposal):
        return self.conn.validate_conn_object(proposal['value'], self.shell)

    @observe('conn_name')
    def _assign_connection(self, change):
        new_conn_name = change['new']
        conn_object = self.shell.user_global_ns[new_conn_name]
        self.conn.caller = self.conn.read_connection(conn_object)

    @needs_local_scope
    @cell_magic
    # @line_magic
    def read_sql(self, line, cell=''):
        options = utils.parse_read_sql_args(line)
        sql = cell.format(**self.shell.user_global_ns)  # python variables {} in sql query
        options['notify'] = self.notify_result ^ options['notify']  # toggle notify
        statements = [s for s in sqlparse.split(sql) if s]  # exclude blank statements
        if options['async']:
            options['display'] = False ^ options['display']  # default to False, unless user provides flag
            t = threading.Thread(target=self.conn.execute_sqls, args=[statements, options])
            t.start()
        else:
            options['display'] = self.output_result ^ options['display']
            self.conn.execute_sqls(statements, options)


def load_ipython_extension(ip):
    """Load the extension in IPython."""
    utils.add_syntax_coloring()
    ip.register_magics(SQL)


def unload_ipython_extension(ip):
    """Reload the extension in IPython."""
    if 'SQL' in ip.magics_manager.registry:
        del ip.magics_manager.registry['SQL']
    if 'SQL' in ip.config:
        del ip.config['SQL']