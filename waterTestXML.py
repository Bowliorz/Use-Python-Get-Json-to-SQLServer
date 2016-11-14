# coding=utf-8
import xml.etree.ElementTree as et
import requests
import pypyodbc

tableName = input("請輸入欲新增資料表名稱:")

webData = requests.get('http://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-001619/?format=xml&token=WYaSsoCzlE6SWh0J3M5lmw')
root = et.fromstring(webData.text)  #XML解析webData.text

columnCreate = 'CREATE TABLE %s ('%tableName  #新增表格語法
columnName = ""  #欄位名稱，給後續insert into語法用
for i in root[0]:  #將資料欄名稱取出來
    columnCreate += "%s NVARCHAR(50),"%i.tag
    columnName += i.tag + ","
creatTableSQL = columnCreate[0:-1] + ')'  #整理新增語法，最後的逗點不需要，加上右括號
columnName = columnName[0:-1]  #最右邊逗點不需要

cnxn = pypyodbc.connect('DRIVER={SQL Server}; SERVER=120.113.70.211; DATABASE=水資源; UID=sa; PWD=nfu123@@@')
cursor = cnxn.cursor()

cursor.execute(creatTableSQL)
cnxn.commit()

rowValue = ''
for i in range(len(root)):  #總共有1000筆
    for j in root[i]:  #將data階層的資料讀出來
        try:  #做例外處理因為怕有空值出現
            rowValue += "'%s',"%j.text  #開始存insert into要的值
        except:
            pass
    cursor.execute('insert into %s(%s) values(%s)'%(tableName,columnName,rowValue[0:-1]))
    cnxn.commit()
    rowValue = ''