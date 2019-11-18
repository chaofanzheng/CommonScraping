import re
from bs4 import BeautifulSoup
from nomura.login import NomuraHometradeAccess
import requests

nomuraHometradeAccess = NomuraHometradeAccess()
nomuraHometradeAccess.login()


column_A = 'コード,現在値,始値,高値,安値,VWAP,出来高,売買代金,前日終値,'
column_B = 'PER(連結),配当利回り,PER(単独),株式益回り,PBR(連結),ROE(連結),PBR(単独),ROE(単独),発行済株式,時価総額,一株利益(連結),一株利益(単独)'
column = column_A + column_B + '\n'

#マップを作る
with open(r'.\nomura\data\株リンク.txt','r') as f:
    urls = list()
    for line in f:
        urls.append(line.replace('\n',''))
code_url = dict(zip(list(map(lambda x:re.search(r'op_para=brand=\d+',x).group().replace('op_para=brand=',''),urls)),urls))


with open(r'.\nomura\data\Daydata.txt','w',encoding='utf-8') as f:
    f.write(column)
with open(r'.\nomura\data\Daydata.txt','a',encoding='utf-8') as f:
    for code in code_url:
        page_html = page_access.request('get',code_url[code]).text
        tags = BeautifulSoup(page_html,'html.parser').findAll("table",attrs = {'class':'qik-table qik-grid-24 qik-grid-sd-24'})
        if len(tags) >= 2:
            value_list = list()
            #8 現在値,始値,高値,安値,VWAP,出来高,売買代金,前日終値,
            for tag in BeautifulSoup(str(tags[0]),'html.parser').findAll("span",attrs = {'class':'qik-first qik-txt-num'}):
                group = re.search('[\d,\.-]+',tag.text)
                if group:
                    value_list.append(group.group().replace(',',''))
            #12 PER(連結),配当利回り,PER(単独),株式益回り,PBR(連結),ROE(連結),PBR(単独),ROE(単独),発行済株式,時価総額,一株利益(連結),一株利益(単独)
            for tag in BeautifulSoup(str(tags[1]),'html.parser').findAll("td",attrs = {'class':'qik-txt-num'}):
                group = re.search('[\d,\.-]+',tag.text)
                if group:
                    value_list.append(group.group().replace(',',''))

            if len(value_list) != 21:
                value_list.insert(9,'0')

            print(value_list)
            f.write(','.join(value_list))
            f.write('\n')
