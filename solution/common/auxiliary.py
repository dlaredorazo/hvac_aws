import sqlalchemy

from sqlalchemy.orm import sessionmaker


def connect_to_db(host, dbname, username=None, pasw=None):
    """Exceptions are handled at the use business layer"""

    sqlsession, sqlengine = None, None

    #driver = "?driver=ODBC+Driver+17+for+SQL+Server"

    if username == None:
        databaseString = "mysql+pymysql://" + host + "/" + dbname
    else:
        databaseString = "mysql+pymysql://" + username + ":" + pasw + "@" + host + "/" + dbname

    sqlengine = sqlalchemy.create_engine(databaseString)
    SQLSession = sessionmaker(bind=sqlengine)
    sqlsession = SQLSession()

    # See if the connection is good
    connection = sqlsession.connection()
    connection = None

    return sqlsession, sqlengine