# -*- coding: utf-8 -*-
from flask import Flask,send_from_directory,render_template,request
from WebCrawler import API1,API2
import os
ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd()

file_site ='./log/'
@app.route('/<filename>')
def download(filename):
    fname = filename
    print(fname)
    return send_from_directory(file_site, fname, mimetype='application/octet-stream') #執行下載

@app.route('/',methods=['POST','GET'])
def index():

    return render_template('index.html')

@app.route('/Company',methods=['POST','GET'])
def Company():
    if request.method =='POST':
        Output=API2(str(request.values['CaseCompanyNum']),
                             str(request.values['companyname']),
                             str(request.values['tele']),
                             str(request.values['homeaddr']),1)
        if len(Output["Result"])>0:
            return render_template('Company.html',companyname=str(request.values['companyname']),
                                                   tele=str(request.values['tele']),
                                                   homeaddr=str(request.values['homeaddr']),
                                                   casecompanynum=str(request.values['CaseCompanyNum']),
                                                   Output=Output
                                               )
        else:
            return render_template('Company.html',companyname=str(request.values['companyname']),
                                                   tele=str(request.values['tele']),
                                                   homeaddr=str(request.values['homeaddr']),
                                                   casecompanynum=str(request.values['CaseCompanyNum']),
                                                   Output="沒有搜尋結果")

    

    return render_template('Company.html',name="start")

@app.route('/Tele',methods=['POST','GET'])
def Tele():

    if request.method =='POST':
        Output=API1(str(request.values['CaseTeleNum']),str(request.values['user']),1)
        
        return render_template('Tele.html',CaseNum=str(request.values['CaseTeleNum']),
                                           Input=str(request.values['user']),
                                           Output=Output,
                                           )
        #return render_template('Tele.html',MaxWord="")
    return render_template('Tele.html',MaxWord="start")

if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True,debug=False)