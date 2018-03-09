# -*- coding: utf-8 -*-
"""
Created on 2/13/2018

@author: yc180

This script go through all the log/txt in the folder and extract data to build a "group" DataFrame for later analysis
The output are two files: gpData.pkl & gpSbjInfo.pkl

%% Phase: cued=1, choice_practice=2, choice =3 (real VTS trials)
%% stimCat
Odd-High [11]
Odd-Low [12]
Even-High [21]
Even-Low [22]
%% trialType: 1 = switch, 0 = repetition, 2 = voluntary TS
%% swProb: 25,75
%% task: 1= odd/even, 2 = high/low


"""

import os
import glob
import pandas as pd
import numpy as np
from copy import copy
from extractData import extractDataFromCSV

workingDir = os.path.dirname(os.path.realpath(__file__))
#%%
os.chdir("..")
# go up one level to the experiment directory

dataDir = os.getcwd() + os.sep + 'data' + os.sep + 'v2_batches' + os.sep  # where the log/txt files are located
csvDir  = os.getcwd() + os.sep + 'data' + os.sep + 'v2_csv' + os.sep

# run the following function to extract missing data from CSV files
extractDataFromCSV(dataDir, csvDir)

fileList     = glob.glob(dataDir +  "*.log")
infofileList = glob.glob(dataDir +  "*.txt")


gpSbjInfo=pd.DataFrame()


colNames=['runId','phase','stim','stimCat','trialType','swProb','task','response','sbjResp','sbjACC','sbjRT']
gpData = pd.DataFrame(np.empty((0,len(colNames)),dtype=int), columns=colNames)
SCNT=0

for f in range(0,len(fileList),1):
    SCNT=SCNT+1
    D = np.genfromtxt(fileList[f],delimiter=',',dtype=int)
    D = pd.DataFrame(np.transpose(np.reshape(D,(len(colNames),int(D.shape[0]/len(colNames))))),columns=colNames)
    D['sbjId']=SCNT
    
    txtFileName = fileList[f][:-3]+ "txt"
    # read in the corresponding text file and extract SRmapping, etc
    sbjInfo=np.genfromtxt(txtFileName, delimiter=":", dtype=str)
    sbjInfo=pd.DataFrame(np.transpose(sbjInfo))
    sbjInfo.columns = sbjInfo.iloc[0]
    sbjInfo.drop([0],axis=0,inplace=True)
    SRmapping = sbjInfo.loc[1,'SRmapping'].split(',') 
    # 0 was the index that become header, hasn't reset index, so taking 1
    sbjInfo['sbjId']=SCNT
    sbjInfo.index = sbjInfo.sbjId
    sbjInfo.drop('sbjId',axis=1,inplace=True)
    # figure which task subject performed based on left/right hand 
    D.loc[D['trialType']==2, 'task']=np.nan
    D.loc[(D['trialType']==2) & (D['sbjResp']==int(SRmapping[0])),'task']=1
    D.loc[(D['trialType']==2) & (D['sbjResp']==int(SRmapping[1])),'task']=1
    D.loc[(D['trialType']==2) & (D['sbjResp']==int(SRmapping[2])),'task']=2
    D.loc[(D['trialType']==2) & (D['sbjResp']==int(SRmapping[3])),'task']=2
    # this means that if sbjResp ==99, then the task = nan
    
    # figure out 'correct response' based on the task inferred
    # stimCat     
    #Odd-High [11]
    #Odd-Low [12]
    #Even-High [21]
    #Even-Low [22]
    
    for trial in range(0,len(D),1):
        if D.loc[trial,'phase']>=2:
            if D.loc[trial,'task']==1:  # odd/even
                if (D.loc[trial,'stimCat']=='11')|(D.loc[trial,'stimCat']=='12'):
                    D.loc[trial,'response']=int(SRmapping[0])
                else:
                    D.loc[trial,'response']=int(SRmapping[1])
            else: # high/low
                if (D.loc[trial,'stimCat']=='11')|(D.loc[trial,'stimCat']=='21'):
                    D.loc[trial,'response']=int(SRmapping[2])
                else:
                    D.loc[trial,'response']=int(SRmapping[3])                
    
    # figure out switch/repeat for the voluntary 
    
    firstTrial=np.where(D.loc[:,'phase']==2)[0][0]  # first voluntary trial (practice)
    currentTask = D.loc[firstTrial,'task']    
    D.loc[firstTrial,'trialType'] = np.nan  # consider the first voluntary trial as NULL for both choice_practice and choice block
    
    for trial in range(firstTrial+1,len(D),1):
        if np.isnan(D.loc[trial,'task']):    # a missing trial
            D.loc[trial,'trialType']= np.nan
        else:
            if D.loc[trial,'task']==currentTask:
                D.loc[trial,'trialType']=0
            else:
                D.loc[trial,'trialType']=1
                currentTask=D.loc[trial,'task']
                
    
    D.loc[(D.loc[:,'sbjResp']==D.loc[:,'response']),'sbjACC']=1
    D.loc[(D.loc[:,'sbjResp']!=D.loc[:,'response']),'sbjACC']=0
    
    # make sure trials subj didn't respond, RT is marked as nan....
    D.loc[D['sbjResp']==99,'sbjRT']=np.nan    
    
    
    ## to be fair, mark all the 1st trial in each run as NULL -> not switch not repeat
    for runId in D.runId.unique():
         firstTrial=np.where(D.runId==runId)[0][0] 
         D.loc[firstTrial,'trialType']=np.nan
         D.loc[firstTrial,'sbjRT']=np.nan
         D.loc[firstTrial,'sbjACC']=np.nan
    
    
    gpSbjInfo = pd.concat([gpSbjInfo,sbjInfo],axis=0)
    gpData=pd.concat([gpData,D],axis=0)


#%%
# convert codings to categorical variables with meaningful names
gpData['trialType_int'] = copy(gpData['trialType'])  # preserve 0,1 to calcuate switch rate for VTS task
gpData['task_int']      = copy(gpData['task'])       # preserve 1,2 to calculate task ratio for VTS task
gpData.task_int = gpData.task_int - 1 # become 0 and 1 

gpData.phase     = gpData.phase.map({1:'cued', 2:'choice_practice',3:'choice'})
gpData.trialType = gpData.trialType.map({0:'repeat',1:'switch'})
gpData.swProb    = gpData.swProb.map({25:'sw25%',75:'sw75%'})
gpData.task      = gpData.task.map({1:'parity', 2:'magnitude'})


gpData['phase']    = pd.Categorical(gpData.phase, categories=['cued','choice','choice_practice'],ordered=True)
gpData['swProb']   = pd.Categorical(gpData.swProb, categories=['sw25%','sw75%'],ordered=True)
gpData['trialType']= pd.Categorical(gpData.trialType, categories=['repeat','switch'],ordered=True)
gpData['task']     = pd.Categorical(gpData.task, categories=['parity','magnitude'],ordered=True)

# output DataFrame
os.chdir(workingDir)  # scripts directory


gpData.to_pickle('gpData.pkl')
gpSbjInfo.to_pickle('gpSbjInfo.pkl')


gpData.to_csv('gpData.csv',encoding='utf-8', index=False)
gpSbjInfo.to_csv('gpSbjInfo.csv',encoding='utf-8', index=False)


print(SCNT)