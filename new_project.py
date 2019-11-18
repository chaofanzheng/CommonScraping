from bs4 import BeautifulSoup
# from nomura.login import NomuraHometradeAccess
import requests
from getpass import getpass
import time

class  PageAccess:

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36)"}

    def  __init__(self):
        #初期化
        self.loginType = ''
        self.btnCd = input('取引店コード（半角）:')
        self.kuzNo = input('口座番号（半角）:')
        self.gnziLoginPswd = getpass ('ログインパスワード（半角）')
        self.loginTuskLoginId = self.btnCd + self.kuzNo
        self.data = {'loginType':self.loginType,'btnCd':self.btnCd,'kuzNo':self.kuzNo,'gnziLoginPswd':self.gnziLoginPswd,'loginTuskLoginId':self.loginTuskLoginId}
        self.ses = requests.Session()

    def login(self,url = 'https://hometrade.nomura.co.jp/web/rmfCmnCauSysLgiAction.do'):

        #cookiesを取得する（野村證券の仕様）
        # self.cookies = requests.request('get','https://hometrade.nomura.co.jp/web/rmfIndexWebAction.do',headers  = self.headers).cookies
        self.ses.request('get','https://hometrade.nomura.co.jp/web/rmfIndexWebAction.do',headers  = self.headers)
        #method,url,post_data,headers,cookies
        self.req = self.ses.request('post',url,data = self.data,headers = self.headers)
        #返却値確認
        self.req.raise_for_status()
        # check_response(self.req.text)

        #エンコードを変更
        self.req.encoding = self.req.apparent_encoding
        #cookiesを保存
        self.cookies = self.req.cookies

    def request(self,method,url):
        #自由アクセス
        return self.ses.request(method,url,headers = self.headers)

    def get_text(self):
        return self.req.text


import re

column_A = 'コード,現在値,始値,高値,安値,VWAP,出来高,売買代金,前日終値,'
column_B = 'PER(連結),配当利回り,PER(単独),株式益回り,PBR(連結),ROE(連結),PBR(単独),ROE(単独),発行済株式,時価総額,一株利益(連結),一株利益(単独)'
column = column_A + column_B + '\n'
column_C = 'コード,決算期,連/単,売上高,営業利益,経常利益,当期利益,EPS（円）,一株配当金（円）'

with open(r'.\nomura\data\株リンク.txt','r') as f:
    urls = list()
    for line in f:
        urls.append(line.replace('\n',''))

code_url = dict(zip(list(map(lambda x:re.search(r'op_para=brand=\d+',x).group().replace('op_para=brand=',''),urls)),urls))

def getStockValues(page_html):
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

        return value_list

# def getPerformanceUrl(page_html):
#     tag = BeautifulSoup(page_html,'html.parser').find("a",attrs = {'id':'qik-aLink4'})
#     if tag:
#         return tag.attrs['href']


def getPerformance(code,page_html):
    ret = list()
    tag = BeautifulSoup(page_html,'html.parser').find("table",attrs = {'class':'qik-table qik-table-stripe qik-grid-24 qik-grid-sd-24 qik-table-transform'})
    if tag:
        tags = BeautifulSoup(str(tag),'html.parser').findAll('td')
        line = code + ','
        for tag in tags:
            line +=  tag.text + ','
            if tag.attrs['data-title'] == '一株配当金（円）':
                ret.append(line)
                line = code + ','
    tag = BeautifulSoup(page_html,'html.parser').find("table",attrs = {'class':'qik-table qik-grid-24 qik-grid-sd-24 qik-table-transform'})
    if tag:
        tags = BeautifulSoup(str(tag),'html.parser').findAll('td')
        line = code + ','
        for tag in tags:
            line +=  tag.text + ','
            if tag.attrs['data-title'] == '一株配当金（円）':
                ret.append(line)
                line = code + ','
    return ret


page_access = PageAccess()
page_access.login()
with open(r'.\nomura\data\stockValuesData.txt','w',encoding='utf-8') as f:
    f.write(column)
    with open(r'.\nomura\data\performancedata.txt','w',encoding='utf-8') as f2:
        f2.write(column_C)
        for code in code_url:
            page_html = page_access.request('get',code_url[code]).text
            value_list = getStockValues(page_html)
            value_list.insert(0,code)
            f.write(','.join(value_list))
            f.write('\n')

            urls = 'https://hometrade.nomura.co.jp/web/rmfInvInfMulGetG522Action.do?qid=12-05-01&op_para=market=TKY&arg={quote:'+ code +'}&qpc='
            page_html = page_access.request('get',urls).text
            value_list = getPerformance(code,page_html)
            f2.write(','.join(value_list))
            f2.write('\n')




ret = list()
urls = 'https://hometrade.nomura.co.jp/web/rmfInvInfMulGetG522Action.do?qid=12-05-01&op_para=market=TKY&arg={quote:'+ '1301' +'}&qpc='
urls
page = page_access.request('get',urls)
print(page.content)


print(page_html)
code = '1301'
tag = BeautifulSoup(page_html,'html.parser').find("table",attrs = {'class':'qik-table qik-table-stripe qik-grid-24 qik-grid-sd-24 qik-table-transform'})
print(tag)
if tag:
    tags = BeautifulSoup(str(tag),'html.parser').findAll('td')
    tags[0]
    line = code + ','
    for tag in tags:
        line +=  (tag.text + ',')
        if tag.attrs['data-title'] == '一株配当金（円）':
            ret.append(line)
            line = code + ','
tag = BeautifulSoup(page_html,'html.parser').find("table",attrs = {'class':'qik-table qik-grid-24 qik-grid-sd-24 qik-table-transform'})
if tag:
    tags = BeautifulSoup(str(tag),'html.parser').findAll('td')
    line = code + ','
    for tag in tags:
        line +=  tag.text + ','
        if tag.attrs['data-title'] == '一株配当金（円）':
            ret.append(line)
            line = code + ','
ret
