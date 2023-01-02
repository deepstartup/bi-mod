# -*- encoding: utf-8 -*-
"""
Created By : Arghadeep Chaudhury
Dated : 12/21/2022
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from flask import Response
from jinja2 import TemplateNotFound
#from sqlparser_c import sql_to_df_html
from moz_sql_parser import parse
import json
import pandas as pd
import openai
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
    return df
def codeexplain(codetext):
    textBulk:str=f"""{codetext}\n\"\"\"\nHere's what the above code is doing:"""
    openai.api_key = "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"
    response = openai.Completion.create(
                        model="code-davinci-002",
                        prompt=textBulk,
                        temperature=0,
                        max_tokens=64,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0,
                        stop=["\"\"\""]
                    )
    return response["choices"][0]["text"]
def apiconversion(text,fromcode,tocode):
    textBulk:str=f'##### Translate this function from {fromcode} into {tocode} \n ### {fromcode} \n {text} \n ### {tocode}'
    openai.api_key = "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"
    response = openai.Completion.create(
        model="code-davinci-002",
        prompt=textBulk,
        temperature=0,
        max_tokens=54,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"]
    )
    return response["choices"][0]["text"]
@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')
@blueprint.route('/featuresSel',methods=['POST', 'GET'])
@login_required
def featuresSel():
    global tab_html
    file_val=request.files.get('sql')
    #sql_text=request.files.get('textarea')
    sql_text=request.form['textarea']
    tab_html=sql_to_df_html(sql_text)
    json_query=json.dumps(parse(sql_text))
    segment = get_segment(request)

    #return render_template('home/ui-sql-report.html', sql_text=tab_html,segment=segment)
    return render_template('home/ui-sql-report.html', tables=[tab_html.to_html(classes='data')], titles=tab_html.columns.values,json_query=json_query,segment=segment)
@blueprint.route('/getfile_test', methods=['POST', 'GET'])
@login_required
def getfile_test():
    #testme=request.form['testme']
    #model_raw=tab_html.to_csv()
    return Response(
       tab_html.to_csv(),
       mimetype="text/csv",
       headers={"Content-disposition":
       "attachment; filename=filename.csv"})
    #return Response(model_raw,headers={'Content-Disposition':'attachment;filename=model.pkl'})
@blueprint.route('/codeConvert',methods=['POST', 'GET'])
@login_required
def codeConvert():
    file_val=request.files.get('code_part')
    #sql_text=request.files.get('textarea')
    code_text=request.form['codetextarea']
    from_code=request.form['domain']
    to_code=request.form['tgtlang']
    print(code_text)
    print(from_code)
    print(to_code)
    return_txt:str=apiconversion(code_text,from_code,to_code)
    segment = get_segment(request)
    ###get code explainer###
    code_text_exp=codeexplain(code_text)
    return_txt_exp=codeexplain(return_txt)
    code_text = code_text.replace('\n', '<br/>')
    return_txt = return_txt.replace('\n', '<br/>')
    code_text_exp = code_text_exp.replace('\n', '<br/>')
    return_txt_exp = return_txt_exp.replace('\n', '<br/>')
    #return render_template('home/ui-sql-report.html', sql_text=tab_html,segment=segment)
    return render_template('home/ui-code-report.html',from_code=from_code,to_code=to_code,code_text=code_text,return_txt=return_txt ,code_text_exp=code_text_exp,return_txt_exp=return_txt_exp,segment=segment)
#codeConvert
@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            pass

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
