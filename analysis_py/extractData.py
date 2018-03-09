# -*- coding: utf-8 -*-
"""
Created on 2/13/2018

@author: yc180

Ideally, participants will submit data to our server right after run_task_v1.html.
However, sometimes that did not happen and data are transferred back to the Main.html and then submitted to AMT server.
In that case, data shows up in the csv file for each batch.
Thus, this function/script is to salvage those data.
The script cross reference existing log/txt and data in the csv.
If data in the csv is not in the log/txt folder, then output log/txt files.

%% Phase: cued=1, uncued=2
%% stimCat
Odd-High [11]
Odd-Low [12]
Even-High [21]
Even-Low [22]
%% trialType: 1 = switch, 0 = repetition, 2 = voluntary TS
%% swProb: 25,75
%% task: 1= odd/even, 2 = high/low



"""

def extractDataFromCSV(dataDir, csvDir):
    
    from glob import glob
    import pandas as pd
    import numpy as np
    
   
    # NEED TO OUTPUT SRmapping to the csv file in the next version. Here, we can only make some guesses from earlier responses
    def inferSRmapping(RT): 
        colNames=['runId','phase','stim','stimCat','trialType','swProb','task','response','sbjResp','sbjACC','sbjRT']
        RT = np.array(RT.split(','))
        RT = pd.DataFrame(np.transpose(RT.reshape(11,808)),columns=colNames)
        SRmapping=[0,0,0,0]
        SRmapping[0]=RT.loc[(RT['runId']<'6') & (RT['task']=='1') & (RT['stimCat']=='11') & (RT['sbjACC']=='1'),'response'].astype(int).mean()  # use stimCat =='12' should yield the same result
        SRmapping[1]=RT.loc[(RT['runId']<'6') & (RT['task']=='1') & (RT['stimCat']=='21') & (RT['sbjACC']=='1'),'response'].astype(int).mean()
        SRmapping[2]=RT.loc[(RT['runId']<'6') & (RT['task']=='2') & (RT['stimCat']=='11') & (RT['sbjACC']=='1'),'response'].astype(int).mean()
        SRmapping[3]=RT.loc[(RT['runId']<'6') & (RT['task']=='2') & (RT['stimCat']=='12') & (RT['sbjACC']=='1'),'response'].astype(int).mean()
        SRmapping=[int(i) for i in SRmapping]    
        SRmapping = ",".join(map(str,SRmapping))
        return SRmapping

    
    csvList = glob(csvDir  + '*.csv')
    txtList = glob(dataDir + '*.txt')
    existingId=['']  # using pd.Series.str.match require at least one element, so create an empty subjId
    
    for f in range(0,len(txtList),1):
        sbjInfo=np.genfromtxt(txtList[f], delimiter=":", dtype=str)
        sbjInfo=pd.DataFrame(np.transpose(sbjInfo))
        sbjInfo.columns = sbjInfo.iloc[0]
        sbjInfo.drop([0],axis=0,inplace=True)
        sbjInfo.reset_index(drop=True,inplace=True)
        existingId.append(sbjInfo.loc[0,'workerId'])

    
    existingId = pd.Series(existingId) # in order to use str match method
    SCNT=0
    for f in range(0,len(csvList),1):
        df = pd.read_csv(csvList[f])
        for S in range(0,len(df),1):        
            SCNT=SCNT+1            
            RT = str(df.loc[S,'Answer.RTs'])
            if RT!='nan':
                #  print('contain data, check if already-exist or not...')
                wkid = str(df.loc[S,'WorkerId'])
                if sum(existingId.str.match(wkid))==0: # no existing txt/log
                    SRmapping = inferSRmapping(RT)
                    fileName = dataDir + df.loc[S,'AssignmentId'] + '.log'
                    with open(fileName, "w") as log_file:
                        log_file.write("%s" % RT)       
                    # need to print a txt file as well
                    sbjInfo['confirmation number']=''  #
                    sbjInfo['workerId']= wkid
                    sbjInfo['assignmentId']= df.loc[S,'AssignmentId']
                    sbjInfo['SRmapping']= SRmapping
                    sbjInfo['age']=''
                    sbjInfo['gender']=''
                    sbjInfo['ethnicity']=''
                    sbjInfo['race']=''                
                    fileName = dataDir + df.loc[S,'AssignmentId'] + '.txt'
                    with open(fileName, "w") as text_file:
                        for r in sbjInfo.columns:   
                            string1 = r + ":"
                            text_file.write("%s" % string1)
                            if r=='Finish':
                                text_file.write("%s" % sbjInfo.loc[0,r])
                            else:
                                text_file.write("%s\n" % sbjInfo.loc[0,r])
                else:
                    print('log/txt already exist. No output file.')
    
    



