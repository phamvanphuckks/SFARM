import sqlite3 as sql
from datetime import datetime
# hàm insert dữ liệu vào databases


def insert_data(battery, temp, hum, soil, signal, time):
    path = "databases\\db_farm.db"
    con = sql.connect(path)
    table_name = "data_of_"+ str(datetime.now().day) + "_" + \
        str(datetime.now().month) + "_" + str(datetime.now().year)
    with con:
        cur = con.cursor()
        cmd = "CREATE TABLE IF NOT EXISTS " + table_name + '''(
			battery TEXT NOT NULL,
			temp TEXT NOT NULL,
			hum TEXT NOT NULL,
			soil TEXT NOT NULL,
			signal TEXT NOT NULL,
			time TEXT NOT NULL )
			'''
        cur.execute(cmd)
        cmd = "INSERT INTO " + table_name + " VALUES(?,?,?,?,?,?)"
        cur.execute(cmd, (str(battery), str(temp), str(
            hum), str(soil), str(signal), time))
    con.close()

# Xóa tất cả các bảng trong database;


def Delete_all_tb():
    path = "databases\\db_farm.db"
    con = sql.connect(path)
    with con:
        cur = con.cursor()
        tables = list(cur.execute(
            "select name from sqlite_master where type is 'table'"))
        cur.executescript(
            ';'.join(["drop table if exists %s" % i for i in tables]))
    con.close()


# Query với n cột trong bảng của ngày hôm đó
def Query(n):
    path = "databases\\db_farm.db"
    con = sql.connect(path)
    datas = []
    data = []
    table_name = "data_of_"+str(datetime.now().day) + "_" + \
        str(datetime.now().month) + "_" + str(datetime.now().year)
    with con:
        cur = con.cursor()
        cmd = "SELECT * FROM " + str(table_name)
        cur.execute(cmd)
        data = cur.fetchall()
    con.close()
    
    for i in range(len(data)-n,len(data)):
        datas.append(data[i])
    return datas
