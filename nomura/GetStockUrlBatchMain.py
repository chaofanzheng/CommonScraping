from bs4 import BeautifulSoup
from nomura.login import NomuraHometradeAccess
import requests

nomuraHometradeAccess = NomuraHometradeAccess(model = '')
nomuraHometradeAccess.login()


with open(r'.\nomura\data\株リンク.txt','a') as f:
    for i in range(1,208):
        url = r'https://hometrade.nomura.co.jp/web/rmfInvInfMulGetG520Action.do?qid=12-01-01&arg=&op_para=pageno={}'.format(i)
        page_html = nomuraHometradeAccess.request('get',url).text
        tag = BeautifulSoup(page_html,'html.parser').find("tbody",attrs = {'class':'brand_list'})
        if tag:
            a_list = list()
            for tag2 in BeautifulSoup(str(tag),'html.parser').findAll("a"):
                a_list.append(tag2['href'])
            f.writelines('\n'.join(a_list))
            f.write('\n')
        time.sleep(1)
