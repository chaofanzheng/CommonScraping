import re
from bs4 import BeautifulSoup
from nomura.login import NomuraHometradeAccess
import traceback

column_A = 'コード,現在値,始値,高値,安値,VWAP,出来高,売買代金,前日終値,'
column_B = 'PER(連結),配当利回り,PER(単独),株式益回り,PBR(連結),ROE(連結),PBR(単独),ROE(単独),発行済株式,時価総額,一株利益(連結),一株利益(単独)'
column = column_A + column_B + '\n'
column_C = 'コード,決算期,連/単,売上高,営業利益,経常利益,当期利益,EPS（円）,一株配当金（円）' + '\n'

#ファイルから株ごとのリンクを取得して、リストに格納する
with open(r'.\nomura\data\株リンク.txt','r') as f:
    urls = list()
    for line in f:
        urls.append(line.replace('\n',''))
#コード、株リンクをセットにして、マップに入れる
code_url = dict(zip(list(map(lambda x:re.search(r'op_para=brand=\d+',x).group().replace('op_para=brand=',''),urls)),urls))


#タブ株価の情報を取得、requestsの場合はソースを編集する必要がある
def getStockValues(page_html):
    tags = BeautifulSoup(page_html,'html.parser').findAll("table",attrs = {'class':'qik-table qik-grid-24 qik-grid-sd-24'})
    if len(tags) >= 2:
        value_list = list()
        #8 現在値,始値,高値,安値,VWAP,出来高,売買代金,前日終値,
        for tag in BeautifulSoup(str(tags[0]),'html.parser').findAll("span",attrs = {'class':'qik-first qik-txt-num'}):
            group = re.search('[\d,\.-]+',tag.text)
            #TODO　0.00の書き方は良くない、誤って別のカラムが引っかかる可能性がある
            if group and group.group()!='0.00':
                value_list.append(group.group().replace(',',''))
        #12 PER(連結),配当利回り,PER(単独),株式益回り,PBR(連結),ROE(連結),PBR(単独),ROE(単独),発行済株式,時価総額,一株利益(連結),一株利益(単独)
        for tag in BeautifulSoup(str(tags[1]),'html.parser').findAll("td",attrs = {'class':'qik-txt-num'}):
            group = re.search('[\d,\.-]+',tag.text)
            if group:
                value_list.append(group.group().replace(',',''))

        return value_list

#タブ業績の情報を取得
def getPerformance(code,page_html):
    ret = list()
    tag = BeautifulSoup(page_html,'html.parser').find("table",attrs = {'class':'qik-table qik-table-stripe qik-grid-24 qik-grid-sd-24 qik-table-transform'})
    if tag:
        tags = BeautifulSoup(str(tag),'html.parser').findAll('td')
        line = code + ','
        for tag in tags:
            line +=  tag.text.replace(',','') + ','
            if tag.attrs['data-title'] == '一株配当金（円）':
                ret.append(line)
                line = code + ','
    tag = BeautifulSoup(page_html,'html.parser').find("table",attrs = {'class':'qik-table qik-grid-24 qik-grid-sd-24 qik-table-transform'})
    if tag:
        tags = BeautifulSoup(str(tag),'html.parser').findAll('td')
        line = code + ','
        for tag in tags:
            line +=  tag.text.replace(',','') + ','
            if tag.attrs['data-title'] == '一株配当金（円）':
                ret.append(line)
                line = code + ','
    return ret


page_access = NomuraHometradeAccess()
page_access.login_by_selenium()

print(page_access.get_text())

with open(r'.\nomura\data\stockValuesData.txt','w',encoding='utf-8') as f:
    f.write(column)
    with open(r'.\nomura\data\performancedata.txt','w',encoding='utf-8') as f2:
        f2.write(column_C)


with open(r'.\nomura\data\stockValuesData.txt','a',encoding='utf-8') as f:
    with open(r'.\nomura\data\performancedata.txt','a',encoding='utf-8') as f2:
        try:
            for code in code_url:

                if int(code) <= 4521:
                    continue

                page_access.request('',code_url[code])
                value_list = getStockValues(page_access.get_text())
                value_list.insert(0,code)
                f.write(','.join(value_list))
                f.write('\n')

                urls = 'https://hometrade.nomura.co.jp/web/rmfInvInfMulGetG522Action.do?qid=12-05-01&op_para=market=TKY&arg={quote:'+ code +'}&qpc='
                page_access.request('',urls)
                value_list = getPerformance(code,page_access.get_text())
                f2.write('\n'.join(value_list))
                f2.write('\n')
        except Exception as e:
            traceback.print_exc()
            print(code)
