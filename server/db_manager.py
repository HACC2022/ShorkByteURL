# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
from io import TextIOWrapper
import json
import time
import datetime
from typing import Union, Any, Tuple, List, Dict
import mysql.connector
from settings import DB_NAME, USER_TBL, URL_TBL
from mysql.connector import errorcode
from mysql.connector.connection import MySQLConnection
from mysql.connector.connection_cext import CMySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor

class DBManager:
    cnx: Union[CMySQLConnection, MySQLConnection, None] = None
    cursor: Union[CMySQLCursor, Any] = None
    files:Dict[str, str] = {}

    def __init__(self, **files:str) -> None:
        self.create_db_connection()

        for file_name, file_path in files.items():
            with open(file_path, "r") as f:
                self.files[file_name] = f.read()
    
    def create_db_connection(self) -> None:
        db_json_file: TextIOWrapper = open('secret/db_login.json')

        secret_data: dict[str, str] = json.load(db_json_file)

        username_str: str = secret_data['username']
        password_str: str = secret_data['password']

        try:
            self.cnx = mysql.connector.connect(
                host = 'localhost',
                user = username_str,
                password = password_str,
                database = DB_NAME
            )
            if self.cnx is not None:
                self.cursor: Union[CMySQLCursor, Any]  = self.cnx.cursor()
            print('Created Connection')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print('Something is wrong with your user name or password')
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print('Database does not exist')
            else:
                print(err)

    def insert(self, tbl: str, vals: List[Union[str, int]]) -> None:
        tbl_cols: List[str] = self.get_cols(tbl)[1:]
        entry: List[str] = ['\'{}\''.format(x) if type(x) is str else str(x) for x in vals]
        insert_str: str = (
            'INSERT INTO {}({})\n'
            '   VALUES({})'.format(tbl, ', '.join(tbl_cols), ', '.join(entry))
        )
        self.exec(insert_str)
        if self.cnx is not None:
            self.cnx.commit()
        

    def get_cols(self, tbl: str) -> List[str]:
        query_str: str = (
            'SELECT COLUMN_NAME '
            'FROM INFORMATION_SCHEMA.COLUMNS '
            'WHERE TABLE_SCHEMA = \'{}\' AND TABLE_NAME = \'{}\''.format(DB_NAME, tbl)
        )
        return [col[0] for col in self.exec(query_str)]
    
    def get_query_cols(self) -> List[str]:
        if self.cursor is None or self.cursor.description is None: return []
        return [field_md[0] for field_md in self.cursor.description] # type: ignore

    def get_count(self, tbl: str) -> int:
        return self.exec('SELECT COUNT(*) FROM {tbl}'.format(**locals()))[0][0]
    
    def format_select(self, tbl:str, select_args: List[str]) -> str:
        return ', '.join([('{}.{}'.format(tbl, select_arg) if select_arg != '*' else select_arg) for select_arg in select_args])

    def select(self, from_arg: str, select_args: List[str] = ['*'], where_args: Dict[str, Union[int, str]]={}, join_tbl:str="", join_select_args:List[str]= [], join_id:str="") -> List[Tuple[Any, ...]]:
        query_str: List[str] = []
        query_str.append('SELECT {}'.format(', '.join([self.format_select(tbl, args) for tbl, args in [(from_arg, select_args), (join_tbl, join_select_args)] if tbl and args ])))
        query_str.append('FROM {}'.format(from_arg))
        if where_args:
            query_str.append('WHERE {}'.format(self.format_dict_args(where_args)))
        if join_tbl and join_select_args and join_id:
            query_str.append('INNER JOIN {join_tbl} ON {from_arg}.{join_id}={join_tbl}.{join_id}'.format(**locals()))
        return self.exec(' '.join(query_str))

    def delete(self, from_arg: str, where_args: Dict[str, Union[str, int]]) -> None:
        self.exec('DELETE FROM {} WHERE {}'.format(from_arg, self.format_dict_args(where_args)))
        if self.cnx is not None:
            self.cnx.commit()
    
    def update(self, from_arg:str, set_args:Dict[str, Union[str, int]], where_args: Dict[str, Union[str, int]] ={}) -> None:
        query_str: List[str] = []
        query_str.append('UPDATE {}'.format(from_arg))
        if set_args:
            query_str.append('SET {}'.format(self.format_dict_args(set_args, delim=', ')))
        if where_args:
            query_str.append('WHERE {}'.format(self.format_dict_args(where_args)))
        self.exec(' '.join(query_str))
        if self.cnx is not None:
            self.cnx.commit()

    def format_dict_args(self, where_args: Dict[str, Union[str, int]], delim:str=' AND ') -> str:
        return delim.join(['{} = {}'.format(key, self.val_to_str(val)) for key, val in where_args.items()])

    def val_to_str(self, val: Union[int, str]) -> str:
        return '\'{}\''.format(val) if type(val) is str else str(val)

    def truncate(self, tbl: str) -> None:
        self.exec('TRUNCATE TABLE {tbl}'.format(**locals()))

    def get_timestamp(self) -> str:
        time_obj =  datetime.datetime.fromtimestamp(int(time.time()))
        try:
            try:
                timestamp: str = time_obj.strftime('%Y-%m-%d %H:%:%S')
            except:
                timestamp: str = time_obj.strftime('%Y-%m-%d %H:%M:%S')
            return timestamp
        except Exception as e:
            print(e)
            return ""

    def exec(self, exec_str: str) -> List[Tuple[Any, ...]]:
        if exec_str in self.files: exec_str = self.files[exec_str]
        # print('exec_str:', exec_str)
        self.cursor.execute(exec_str)
        return list(self.cursor)

    def exec_w_headers(self, exec_str: str) -> List[Dict[str, Any]]:
        rows: List[Tuple[Any, ...]] = self.exec(exec_str)
        cols: List[str] = self.get_query_cols()
        return [{col: value for col, value in zip(cols, row)} for row in rows]

    def close_db_connection(self) -> None:
        print('Closing Connection')
        if self.cnx is not None:
            self.cursor.close()
            self.cnx.close()

    def __del__(self) -> None:
        self.close_db_connection()

def main() -> None:
    db: DBManager = DBManager(requests_query='server/db/query_requests.sql')
    print('All Users:', db.select(USER_TBL))
    print('All URLs:', db.select(URL_TBL))

    queries: List[str] = ['/ZS8', '/ZS']
    for query in queries:
        print('Query:', [url for url in db.select(
            from_arg=URL_TBL,
            select_args=['short_url', 'orig_url'],
            where_args={'short_url': query}
        )])
    print('User Columns:', ', '.join(db.get_cols(URL_TBL)))
    print('Deleting:', '"/https-health-hawaii-gov"')
    db.delete(URL_TBL, {'short_url': '/https-health-hawaii-gov', 'orig_url':'https://health.hawaii.gov/'})

    query_res: List[Tuple[Any, ...]] = db.exec('requests_query')
    print("\nJoin:", query_res)
    print("Join Cols:", db.get_query_cols())

    query_id: int = int(query_res[0][0])
    query_name: str = query_res[0][7]
    new_query_name: str = '/ZS82222' if query_name == '/ZS8' else '/ZS8'
    db.update(URL_TBL, set_args={
        'short_url': new_query_name
    }, where_args={
        'url_id': query_id
    })
    print("Join Again:", db.exec_w_headers('requests_query'))

if __name__ == '__main__':
    main()
