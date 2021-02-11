from CrawlerFunction import *

def API1(CaseNum,Tele,way):#參數:案件編號，輸入電話、爬蟲方式
    Tele=ClearTele(Tele)
    start=datetime.datetime.now()#程式開始時間
    Status=[]
    
    CrawResult=[]#儲存在google搜尋回來的結果
    FirstSearch=Craw(Tele,way)#呼叫Craw，回傳為FirstSearch
    
    if type(FirstSearch)==str:#爬蟲錯誤會得到錯誤訊息的字串
        Status.append({"1Search":FirstSearch})
    else:
        #輸入為行動電話，則以Input再加上兩種情況，回傳為SecondSearch和ThirdSearch
        CrawResult.append(FirstSearch)
        if Tele[:2]=="09":
            Tele=Tele[:4]+"-"+Tele[4:]
            SecondSearch=Craw(Tele,way)
            CrawResult.append(SecondSearch)
            
            Tele=Tele[:8]+"-"+Tele[8:]
            ThirdSearch=Craw(Tele,way)
            CrawResult.append(ThirdSearch)
            
        #輸入為家用電話，則Input再加上"-"搜尋，回傳為SecondSearch
        else:
            Tele=Tele[:2]+"-"+Tele[2:]
            SecondSearch=Craw(Tele,way)
            CrawResult.append(SecondSearch)
        
    FinalResult=[]#整理負面字詞後，儲存最後的結果
    NegCheck=0
    CutWay=0
    
    for index,i in enumerate(CrawResult):
        if type(i)==str:#如果搜尋出錯結果時的處理
            Status.append({"{}Search".format(index+2):i})
        else:
            Status.append({"{}Search".format(index+1):"Success"})
            for j in i:
                NegList={}
                WordsDict={}
                WordsDict=APICut(j['Title'],CutWay,WordsDict,Tele)#對標題斷詞
                WordsDict=APICut(j['Content'],CutWay,WordsDict,Tele)#對內文斷詞
                for k in WordsDict:
                    if k in negative:
                        if NegList.get(k)==None:
                            NegList.update({k:1})
                        else:
                            NegList[k]+=1
                j.update({"NegList":NegList})
                if NegList!={}:
                    NegCheck=1
                FinalResult.append(j)
                            
    cost=(str(datetime.datetime.now()-start))#總花費時間
    Output={"Status":Status,"App_Case_No":CaseNum,"Cust_Tel":Tele,"Result":FinalResult,"NEG_CHECK":NegCheck,"Cost":cost}#最後回傳結果
    
    with open("./log/"+CaseNum+" Google搜尋結果.json", 'w',encoding="utf-8") as outfile:
        json.dump(Output,outfile,ensure_ascii=False)
    return Output

def API2(CaseNum,InputName,InputTele,InputHomeAddr,way):#參數:案件編號、公司名稱、公司電話、居住地址，爬蟲方式
    InputName=FillNan(InputName)
    InputTele=ClearTele(InputTele)
    InputHomeAddr=ClearAddr(InputHomeAddr)
    start=datetime.datetime.now()
    #台灣每個地區的附近縣市
    AroundArea={"新北":["新北","台北","臺北","基隆","宜蘭","桃園"],
                    "台北":["台北","臺北","新北","基隆","宜蘭","桃園"],
                    "桃園":["桃園","新竹","宜蘭","新北","台北","臺北"],
                    "新竹":["新竹","桃園","苗栗","宜蘭"],
                    "苗栗":["苗栗","新竹","台中","臺中"],
                    "台中":["台中","臺中","苗栗","彰化","南投","宜蘭","花蓮"],
                    "彰化":["彰化","台中","臺中","南投","雲林"],
                    "雲林":["雲林","彰化","南投","嘉義"],
                    "嘉義":["嘉義","雲林","台南","臺南","南投"],
                    "台南":["台南","臺南","嘉義","高雄"],
                    "高雄":["高雄","臺南","台南","屏東","南投","台東","臺東"],
                    "屏東":["屏東","高雄","台東","臺東"],
                    "台東":["台東","臺東","屏東","花蓮"],
                    "花蓮":["花蓮","臺東","台東","南投","台中","臺中","宜蘭"],
                    "宜蘭":["宜蘭","花蓮","台中","臺中","新竹","桃園","新北","台北","臺北","基隆"],
                    "基隆":["基隆","新北","臺北","台北","宜蘭"]}
    Status=[]
    
    #公司電話不為null，以電話搜尋，為空的話以公司名稱
    Search,BackInput=ProcessInput(InputTele,InputName)
    FirstSearch=Craw(Search,way) #呼叫Craw()，回傳為FirstSearch
    if type(FirstSearch)==str:#
        Status.append({"1Search":FirstSearch})
    if len(FirstSearch)==0:#如果第一次的搜尋沒有結果，以BackInput作為第一次搜尋
        Status.append({"1Search":"Success"})
        Search=BackInput
        FirstSearch=Craw(Search,way)
    print(FirstSearch)
    CleanResult=[]#儲存整理店家名稱、電話、地址、類型後的結果
    if type(FirstSearch)!=str:#搜尋成功的處理
        Status.append({"1Search":"Success"})
        for i in FirstSearch:
            if i["Title"].find("- 店家介紹- ")!=-1:#店家名稱的條件，"...- 店家介紹 -"
                Title="沒有搜尋到店家名稱"
                Tele="沒有搜尋到店家電話"
                Addr="沒有搜尋到店家地址"
                Type="沒有搜尋到店家類型"
                
                titleindex=i["Title"].find("- 店家介紹- ")
                Title=i["Title"][:titleindex]
                
                #店家電話的條件，在黃頁網址後面得到，去除黃頁網址之後留下的字串，字串頭尾都需介於0~9
                #為了判斷字串是電話
                if i["Url"].find("https://www.iyp.com.tw/")!=-1 and\
                    i["Url"].replace("https://www.iyp.com.tw/","")[0]>="0" and\
                        i["Url"].replace("https://www.iyp.com.tw/","")[0]<="9":
                    Tele=i["Url"].replace("https://www.iyp.com.tw/","")
                    Tele=Tele.replace("/","")
                    Type=SearchYP(i["Url"])#用網址在黃頁爬取店家類型
                    
                if i["Content"].find("位於")!=-1:#店家地址的條件，"位於...的...店家"
                    addrindex=i["Content"].find("位於")
                    if i["Content"].find("的")!=-1 and i["Content"].find("的")>addrindex:
                        typeindex=i["Content"].find("的")
                        Addr=i["Content"][addrindex+2:typeindex]
    
                CleanResult.append({"Title":Title,"Tele":Tele,"Addr":Addr,"Type":Type})

    else:#搜尋出錯的處理
        Status.append({"1Search":FirstSearch})
    
    YPTeleCheck=0
    FinalResult=[]#儲存比對輸入電話跟結果電話、居住地址跟店家地址之後的結果
    for i in CleanResult:
        #輸入電話與結果電話相同，將FinalResult清空，只存這一項結果，YPCheck設為1
        if i["Tele"]==InputTele:
            FinalResult=[]
            FinalResult.append(i)
            YPTeleCheck=1
            break
            
        #沒有相符合電話，則比對住家地址跟店家地址
        else:
            if AroundArea.get(InputHomeAddr)!=None:
                around=AroundArea[InputHomeAddr]
                if i["Addr"][:2] in around:
                    FinalResult.append(i)
        
    #FinalResult不到5筆，則依照CleanResult的順序讓FinalReuslt有5筆結果
    if YPTeleCheck==0:
        for i in CleanResult:
            if len(FinalResult)>=5:
                break
            if i not in FinalResult:
                FinalResult.append(i)
        
    #搜尋關鍵詞用，如果命中則以那一筆結果的Title去搜尋
    #沒命中則以輸入公司名稱，輸入公司名稱如果為null，則以輸入電話，回傳結果為SecondSearch
    if YPTeleCheck==1:
        SecondSearch=Craw(FinalResult[0]["Title"],way)
    elif InputName!="":
        SecondSearch=Craw(InputName,way)
    elif InputTele!="":
        SecondSearch=Craw(InputTele,way)
    GKeyWord={}
    if type(SecondSearch)==str:
        Status.append({"2Search":SecondSearch})
    elif len(SecondSearch)==0:
        Status.append({"2Search":"Success"})
        
    else:#搜尋成功
        Status.append({"2Search":"Success"})
        JiebaWordsDict={}#儲存以jieba斷詞
        MonpaWordsDict={}#儲存以monpa斷詞
        Monpa,Jieba=0,1
        for i in SecondSearch:
            MonpaWordsDict=APICut(i['Title'],Monpa,MonpaWordsDict,InputName)#對標題斷詞
            MonpaWordsDict=APICut(i['Content'],Monpa,MonpaWordsDict,InputName)#對內文斷詞
            
            JiebaWordsDict=APICut(i['Title'],Jieba,JiebaWordsDict,InputName)
            JiebaWordsDict=APICut(i['Content'],Jieba,JiebaWordsDict,InputName)
            
        MaxJiebaWords=Dict2MaxList(JiebaWordsDict)#Dictionary轉成List，方便排序
        MaxMonpaWords=Dict2MaxList(MonpaWordsDict)#Dictionary轉成List，方便排序
        GKeyWord={"MonpaMaxWord":MaxMonpaWords,"JiebaMaxWord":MaxJiebaWords}

    cost=datetime.datetime.now()-start #花費時間
    #最後回傳結果
    Output={"Status":Status,"App_Case_No":CaseNum,"Comp_Tel":InputTele,"Comp_Name":InputName,"Home_Addr":InputHomeAddr,
            "Result":FinalResult,"YP_Tel_Check":YPTeleCheck,"G_KeyWord":GKeyWord,"Cost":str(cost)}
    #存成json
    with open("./log/"+CaseNum+" 黃頁搜尋結果.json", 'w',encoding="utf-8") as outfile:
            json.dump(Output, outfile,ensure_ascii=False)
    return Output