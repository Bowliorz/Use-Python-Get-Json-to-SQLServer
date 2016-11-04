# coding=utf-8
import requests, json
import pypyodbc

#年轉換，將民國年轉成西元年資料庫才會接收
def convertDate(zzz):
    year = str(int(zzz[0:3]) + 1911)
    return year+zzz[3:]

#設定要抓取農作物
crop = '蕉'
#資料庫連接字串
cnxn = pypyodbc.connect('DRIVER={SQL Server}; SERVER=IP; DATABASE=DatabaseName; UID=UserName; PWD=Password')
cursor = cnxn.cursor()

cursor.execute("SELECT count(*) FROM sys.tables WHERE name = '%s'"%(crop))
row = cursor.fetchall()
if row[0][0] == 1: #檢查資料表是否存在
    print('該作物資料已存在')
else:
    cursor.execute("CREATE TABLE %s (作物代號 nvarchar(5) not null, 作物名稱 nvarchar(20) null, 市場代號 int not null, 市場名稱 nvarchar(5) null, 交易日期 date not null, 平均價 float null)"%(crop))
    cnxn.commit()  #新增資料表
    for y in range(101,106):
        for a in range(2):
            if a == 1:
                webData = requests.get( #設定json抓取網頁
                    'http://m.coa.gov.tw/OpenData/FarmTransData.aspx?$top=10000&$skip=0&Crop=' + crop + '&StartDate=' + str(y) + '.01.01&EndDate=' + str(y) + '.06.30')
            else:
                webData = requests.get(
                    'http://m.coa.gov.tw/OpenData/FarmTransData.aspx?$top=10000&$skip=0&Crop=' + crop + '&StartDate=' + str(y) + '.07.01&EndDate=' + str(y) + '.12.31')
            dataStr = webData.text  # 擷取網頁內容，此時型態為str
            str2list = json.loads(dataStr)  # str轉list
            for i in range(len(str2list)): #從list一一取出，取出後會自動變成dict好做處理
                Date = convertDate(str2list[i].get('交易日期'))
                cursor.execute("insert into %s(作物代號,作物名稱,市場代號,市場名稱,交易日期,平均價) values('%s','%s','%s','%s','%s','%s')" % (crop,
                    str2list[i].get('作物代號'), str2list[i].get('作物名稱'), str2list[i].get('市場代號'), str2list[i].get('市場名稱'), convertDate(str2list[i].get('交易日期')), str2list[i].get('平均價')))
                cnxn.commit()
        print('%s年完成'%(y))

