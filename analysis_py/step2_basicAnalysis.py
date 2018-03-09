# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 11:29:56 2017

@author: yc180
"""
#%%
import pandas as pd
import numpy as np
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
import os
from copy import copy

#workingDir = os.path.dirname(os.path.realpath(__file__))
workingDir = os.getcwd()
os.chdir(workingDir)

gpData = pd.read_pickle('gpData.pkl')

gpResult  = pd.DataFrame(np.empty((0,0),dtype=int))
gpResult2 = pd.DataFrame(np.empty((0,0),dtype=int))
gpResult3 = pd.DataFrame(np.empty((0,0),dtype=int))
gpResult4 = pd.DataFrame(np.empty((0,0),dtype=int))

gpData_valid = pd.DataFrame(np.empty((0,0),dtype=int))

#gpRT=pd.DataFrame(np.empty((0,1),dtype=int))

overallACC = pd.DataFrame(np.unique(gpData.sbjId),dtype=int,columns=['sbjId'])
overallACC['meanACC']=np.nan
excludeSbj=[]
goodSbj=[]

#%% do a fist pass to exclude subjects with low cued task accuracy
gpData['sbjRT2'] = copy(gpData.sbjRT)
gpData.loc[gpData.sbjRT2<350, 'sbjRT']  = np.nan
gpData.loc[gpData.sbjRT2<350, 'sbjACC'] = 0

totalSCNT = len(np.unique(gpData.sbjId))

for S in np.unique(gpData.sbjId):
    D = gpData.loc[gpData.sbjId==S]    
    if D[D.bkType=='cued'].sbjACC.mean()*100 > 85:
        goodSbj.append(S)
    else:
        excludeSbj.append(S)


#%%
ISSP = pd.DataFrame(np.unique(gpData.sbjId),dtype=int,columns=['sbjId'])

for S in goodSbj:
    D = gpData.loc[gpData.sbjId==S]
    choiceHalfRun = int(len(D[D['runId']==8])/2)
    D.loc[D['runId']==8,'runId_half'] = np.concatenate((np.ones(choiceHalfRun),np.ones(choiceHalfRun)*2),axis=0)
    D.loc[D['runId']==9,'runId_half'] = np.concatenate((np.ones(choiceHalfRun)*3,np.ones(choiceHalfRun)*4),axis=0)
    #
    gpData_valid = pd.concat([gpData_valid, D], axis=0)
    #
    sbjMeans = pd.DataFrame(D.groupby(['bkType','swProb','trialType']).sbjACC.mean()*100)
    sbjMeans['sbjRT']=pd.DataFrame(D.loc[D.sbjACC==1,:].groupby(['bkType','swProb','trialType']).sbjRT.mean())
    sbjMeans['sbjId']=S
    gpResult = pd.concat([gpResult,sbjMeans],axis=0)        
    
#    if sbjMeans.sbjACC.std()>30:   ## if set at 10, there'll be about 10 subjects being excluded due to this criteria
#        excludeSbj.append(S)
    #
    sbjMeans.reset_index(inplace=True)
    RT = sbjMeans.sbjRT
    ISSP.loc[ISSP[ISSP.sbjId==S].index, 'issp'] = RT[1]-RT[0]-(RT[3]-RT[2])    
    ISSP.loc[ISSP[ISSP.sbjId==S].index, 'issp_choice'] = RT[5]-RT[4]-(RT[7]-RT[6])
    #
    sbjMeans2 = pd.DataFrame(D[D['bkType']=='choice'].groupby('swProb').trialType2.mean()*100)
    sbjMeans2['taskRatio']= pd.DataFrame(D[D['bkType']=='choice'].groupby('swProb').taskNum.mean()*100)
    sbjMeans2['sbjId']=S
    
    gpResult2 = pd.concat([gpResult2,sbjMeans2],axis=0)        
    
    sbjMeans3 = pd.DataFrame(D[D['bkType']=='choice'].groupby(['swProb','runId']).trialType2.mean()*100)
    sbjMeans3['taskRatio']= pd.DataFrame(D[D['bkType']=='choice'].groupby(['swProb','runId']).taskNum.mean()*100)
    sbjMeans3['sbjId']=S
    gpResult3 = pd.concat([gpResult3,sbjMeans3],axis=0)
    
    
    sbjMeans4 = pd.DataFrame(D[D['bkType']=='choice'].groupby(['swProb','runId_half']).trialType2.mean()*100)
    sbjMeans4['taskRatio']= pd.DataFrame(D[D['bkType']=='choice'].groupby(['swProb','runId_half']).taskNum.mean()*100)
    sbjMeans4['sbjId']=S
    gpResult4 = pd.concat([gpResult4,sbjMeans4],axis=0)
    
    
    if (sum(sbjMeans3.trialType2<=15) + sum(sbjMeans3.trialType2>=85))>=1:  # one of the block swRate was zero...
        excludeSbj.append(S)
    # 
    ISSP.loc[ISSP[ISSP.sbjId==S].index, 'sw25%_swRate'] = sbjMeans2.trialType2[0]
    ISSP.loc[ISSP[ISSP.sbjId==S].index, 'sw75%_swRate'] = sbjMeans2.trialType2[1]

#%%
# MUST INCLUDE RESET_INDEX, OTHERWISE THE BELOW exclude subject chuck will be order

gpResult.reset_index(inplace=True)
gpResult2.reset_index(inplace=True)
gpResult3.reset_index(inplace=True)
gpResult4.reset_index(inplace=True)
gpData_valid.reset_index(inplace=True)

drop_1 =  pd.DataFrame(np.empty((0,0),dtype=int))
drop_2 =  pd.DataFrame(np.empty((0,0),dtype=int))
drop_3 =  pd.DataFrame(np.empty((0,0),dtype=int))
drop_4 =  pd.DataFrame(np.empty((0,0),dtype=int))
drop_ISSP = pd.DataFrame(np.empty((0,0),dtype=int))

for S in excludeSbj:
    drop_1 = pd.concat([drop_1, gpResult[gpResult.sbjId==S]], axis=0)
    drop_2 = pd.concat([drop_2, gpResult2[gpResult2.sbjId==S]], axis=0)
    drop_3 = pd.concat([drop_3, gpResult3[gpResult3.sbjId==S]], axis=0)
    drop_4 = pd.concat([drop_4, gpResult4[gpResult4.sbjId==S]], axis=0)
    drop_ISSP = pd.concat([drop_ISSP, ISSP[ISSP.sbjId==S]], axis=0)
    
    gpResult.drop(gpResult[gpResult.sbjId==S].index, axis=0, inplace=True)
    gpResult2.drop(gpResult2[gpResult2.sbjId==S].index, axis=0, inplace=True)
    gpResult3.drop(gpResult3[gpResult3.sbjId==S].index, axis=0, inplace=True)
    gpResult4.drop(gpResult3[gpResult4.sbjId==S].index, axis=0, inplace=True)        
    ISSP.drop(ISSP[ISSP.sbjId==S].index,axis=0, inplace=True)    
    
    gpData_valid.drop(gpData_valid[gpData_valid.sbjId==S].index, axis=0, inplace=True)
    
#%%
gpResult.reset_index(inplace=True)
gpResult2.reset_index(inplace=True)
gpResult3.reset_index(inplace=True)
gpResult4.reset_index(inplace=True)
ISSP.reset_index(inplace=True)
#%%

fig = plt.figure(figsize=(16,5))
sns.factorplot(x='swProb',y='sbjACC',data=gpResult,hue='trialType',col='bkType')
sns.factorplot(x='swProb',y='sbjRT', data=gpResult,hue='trialType',col='bkType')

# sns.factorplot("Sex", "Survived", hue="Pclass", data=dfTrain)

gpResult2.rename(columns={'trialType2':'VolSwRate'},inplace=True)
fig = plt.figure(figsize=(5,5))
sns.boxplot(x='swProb',y='VolSwRate',data=gpResult2)

# quick paired t-test
a = np.array(gpResult2[gpResult2.swProb=='sw25%'].VolSwRate)
b = np.array(gpResult2[gpResult2.swProb=='sw75%'].VolSwRate)
tt = stats.ttest_rel(a,b)
tvalue = tt.statistic
print(tt.pvalue)

validSCNT=np.unique(gpResult.sbjId).shape[0]
print(validSCNT)

# quick 1 sample ttest on ISSP (essentially the interaction) against 0
ISSP_inX=stats.ttest_1samp(ISSP.issp,0)
print(ISSP_inX.pvalue)

ISSP_c_inX=stats.ttest_1samp(ISSP.issp_choice,0)
print(ISSP_c_inX.pvalue)

#%%
gpResult3.rename(columns={'trialType2':'VolSwRate'},inplace=True)
fig = plt.figure(figsize=(5,5))
sns.factorplot(x='runId',y='VolSwRate', hue='swProb',data=gpResult3)
# 
a = np.array(gpResult3[(gpResult3.swProb=='sw25%') & (gpResult3.runId==9)].VolSwRate)
b = np.array(gpResult3[(gpResult3.swProb=='sw75%') & (gpResult3.runId==9)].VolSwRate)
tt2 = stats.ttest_rel(a,b)

gpResult4.rename(columns={'trialType2':'VolSwRate'},inplace=True)
fig = plt.figure(figsize=(5,5))
sns.factorplot(x='runId_half',y='VolSwRate', hue='swProb',data=gpResult4)



print(totalSCNT)
gpData_valid.to_csv('validgpData.csv',encoding='utf-8', index=False)



#%% dropped data....
dropSCNT=np.unique(drop_1.sbjId).shape[0]
print(validSCNT)
fig = plt.figure(figsize=(16,5))
sns.factorplot(x='swProb',y='sbjACC',data=drop_1,hue='trialType',col='bkType')
sns.factorplot(x='swProb',y='sbjRT', data=drop_1,hue='trialType',col='bkType')

drop_ISSP_inx = stats.ttest_1samp(drop_ISSP.issp[~np.isnan(drop_ISSP.issp)],0)

# sns.factorplot("Sex", "Survived", hue="Pclass", data=dfTrain)

drop_2.rename(columns={'trialType2':'VolSwRate'},inplace=True)
fig = plt.figure(figsize=(5,5))
sns.boxplot(x='swProb',y='VolSwRate',data=drop_2)

drop_3.rename(columns={'trialType2':'VolSwRate'},inplace=True)
fig = plt.figure(figsize=(5,5))
sns.factorplot(x='runId',y='VolSwRate', hue='swProb',data=drop_3)




