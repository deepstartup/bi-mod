# -*- encoding: utf-8 -*-
"""
Created By : Arghadeep Chaudhury
Dated : 12/21/2022
"""

from moz_sql_parser import parse
import pandas as pd
"""
####Example Queries#####
query = 
select
    sales.order_id as id,
    p.product_name,
    sum(p.price) as sales_volume
from sales
right join products as p
    on sales.product_id=p.product_id
where sales.product_id>10
group by id, p.product_name;
query1='select a.a,b.b,a.a1,a.a2,c.d from a,b,c where a.x=b.x and a.y=c.y'
"""
def sql_to_df_html(query):
    da=parse(query)
    pure_tab=[]
    alis_tab=[]
    for tab in da.get('from'):
        if type(tab)==dict:
            for _tab in tab:
                if _tab=='value':
                    pure_tab.append(tab[_tab])
                elif _tab=='name':
                    alis_tab.append({tab.get('value'):tab[_tab]})
                elif _tab=='right join':
                    pure_tab.append(tab[_tab].get('value'))
                    alis_tab.append({tab[_tab].get('name'):tab[_tab].get('value')})
                elif _tab=='left join':
                    pure_tab.append(tab[_tab].get('value'))
                    alis_tab.append({tab[_tab].get('name'):tab[_tab].get('value')})
        else:
            pure_tab.append(tab)
    dict_1:dict={}
    for _v in alis_tab:
        dict_1=dict(dict_1,**_v)
    fnal_arr=[]
    for col in da.get('select'):
        if type(col.get('value'))==str:
            get_tab_col_name=col.get('value').split('.')
            print('keyfields',get_tab_col_name[1])
            if get_tab_col_name[0] in pure_tab:
                dd={'report_name':'RPT1','database':'N/A','schema':'N/A','keyfields':get_tab_col_name[1],'table_name':get_tab_col_name[0],'tab_alias_name':'N/A','col_alias_name':col.get('name')}
                fnal_arr.append(dd)
            else:
                #doing lookups
                tab_name=dict_1.get(get_tab_col_name[0])
                dd={'report_name':'RPT1','database':'N/A','schema':'N/A','keyfields':get_tab_col_name[1],'table_name':tab_name,'tab_alias_name':get_tab_col_name[0],'col_alias_name':col.get('name')}
                fnal_arr.append(dd)
        else:
            for _spclfun in col.get('value'):
                col_name_fun=col.get('value').get(_spclfun)
                get_tab_col_name=col_name_fun.split('.')
                if get_tab_col_name[0] in pure_tab:
                    dd={'report_name':'RPT1','database':'N/A','schema':'N/A','keyfields':get_tab_col_name[1],'table_name':get_tab_col_name[0],'tab_alias_name':'N/A','col_alias_name':col.get('name'),'col_function':_spclfun}
                    fnal_arr.append(dd)
                else:
                    #doing lookups
                    tab_name=dict_1.get(get_tab_col_name[0])
                    #print('else:',tab_name)
                    dd={'report_name':'RPT1','database':'N/A','schema':'N/A','keyfields':get_tab_col_name[1],'table_name':tab_name,'tab_alias_name':get_tab_col_name[0],'col_alias_name':col.get('name'),'col_function':_spclfun}
                    fnal_arr.append(dd)
    df=pd.DataFrame(fnal_arr)
    return df.to_html()