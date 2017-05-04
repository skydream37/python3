import xml.etree.ElementTree as ET

import requests
import rethinkdb as r
import pandas as pd
pd.options.display.max_columns = 999

def parse_row(res, stn_no):
    etree = ET.fromstring(res.text)
    for row in etree.iterfind('.//Deptid'):
        rec_yy = row.find('.//rec_yy').text
        d_tuple = (row.find('.//wellno').text,
                   row.find('.//well').text,)
        stn_no.append(d_tuple)

# get station no
stn_no = []
for x in range(1,11):
    url = "http://gic.wra.gov.tw/gic/Water/WrHydroFx/qry_Gw_Stno.aspx?AreaType=3&AreaItem={}".format(x)
    res = requests.get(url)
    parse_row(res, stn_no)

for qyy in range(2010,2015):
    for loc in stn_no:
        data = []
        params = {'MM': '1',
         'Mode': '0',
         'MultiYY': '',
         'QYY': '{}'.format(qyy),
         'RaStno': '',
         'WatchRa': 'true',
         'eYY': '2099',
         'sYY': '1000',
         'stno': loc[0]}
        res = requests.get("http://gweb.wra.gov.tw/hyis/AdvQuery/flex/getGwGraph.aspx", params=params)
        if res.status_code > 200:
            continue
        try:
            etree = ET.fromstring(res.text)
            for row in etree.iterfind('.//ROW'):
                data_dict = {}
                data_dict['wellid'] = loc[0]
                data_dict['wellname'] = loc[1]
                data_dict['level'] = row.find('.//L').text
                data_dict['date'] = row.find('.//DATE').text
                data.append(data_dict)
        except:
            continue
        r.db('nasa').table('water').insert(data).run(r.connect())
