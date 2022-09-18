#!/usr/bin/env python
# coding: utf-8

# # FPL Reports for MiniLeagues

# In[15]:


import requests
import json
import pandas as pd

from html2image import Html2Image
hti = Html2Image()

# import dataframe_image as dfi


# In[2]:


# Get the league team IDs

league = 851139

leagueData = requests.get('https://fantasy.premierleague.com/api/leagues-classic/{}/standings/'.format(league))
#leagueData.status_code
leagueData = leagueData.json()

teamsDF = pd.DataFrame(leagueData['standings']['results'])
teamsDF.head(20)


# In[3]:


# Create a dictionary of Team IDs and Names

entries = teamsDF['entry']

teamDict = dict(zip(teamsDF.entry, teamsDF.entry_name))
teamDict


# ## Top Scoring Game Weeks

# In[4]:


# Iterate over team GWs to collect scores

allWeekTotals = pd.DataFrame()

for team in entries:
    currentTeam = requests.get('https://fantasy.premierleague.com/api/entry/{}/history/'.format(team))
    currentTeam = currentTeam.json()
    
    currentTeamDF = pd.DataFrame(currentTeam['current'])
    currentTeamDF['entry'] = team
    
    allWeekTotals = pd.concat([allWeekTotals, currentTeamDF], ignore_index=True)

allWeekTotals['TeamName'] = allWeekTotals['entry'].map(teamDict)
allWeekTotals = allWeekTotals.rename(columns={"event":"GW", "points":"Points"})

allWeekTotals


# In[5]:


# Cleanup total scores DF to get top weeks

topWeeks = allWeekTotals.sort_values(by='Points', ascending=False)
topWeeks = topWeeks.reset_index()

topWeeks = topWeeks[['TeamName', 'GW', 'Points']]
topWeeks.head()


# ## Bench Points

# In[6]:


benchDF = allWeekTotals.groupby('TeamName').sum()

benchDF = benchDF[['points_on_bench']]
benchDF = benchDF.sort_values(by='points_on_bench', ascending=False)
benchDF = benchDF.rename(columns={"points_on_bench":"Bench Points"})

benchDF


# In[ ]:





# ## Team Values

# In[7]:


topValues = allWeekTotals.sort_values(by='value', ascending=False)
topValues = topValues.reset_index()

topValues['value'] = topValues['value']/10
topValues['Bank'] = topValues['bank']/10
topValues['Value with Bank'] = topValues['Bank'] + topValues['value']

topValues = topValues[['TeamName', 'GW', 'value', 'Bank']]
#topValues = topValues[topValues.GW==5]
topValues = topValues[topValues.GW==allWeekTotals.GW.max()]

topValues = topValues.rename(columns={"value":"Team Value"})

topValues


# ## Captaincy

# In[8]:


# Iterate over teams to collect players in current game week

#teamEntry = 2539468
gw = allWeekTotals.GW.max()

leaguePlayers = pd.DataFrame()

for team in entries:

    teamPlayers = requests.get('https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/'.format(team, gw))
    teamPlayers = teamPlayers.json()
    teamPlayersDF = pd.DataFrame(teamPlayers['picks'])
    
    teamPlayersDF['entry'] = team
    teamPlayersDF['TeamName'] = teamPlayersDF['entry'].map(teamDict)
    teamPlayersDF['GW'] = gw
    
    leaguePlayers = pd.concat([leaguePlayers, teamPlayersDF], ignore_index=True)


# In[9]:


leaguePlayers


# In[10]:


# Get the Player IDs and stats to merge

static = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
static = static.json()
#static['elements']

players = pd.DataFrame(static['elements'])
players = players[['id', 'first_name', 'second_name']]
players = players.rename(columns={"id":"element"})

players.head()


# In[11]:


playersReport = leaguePlayers.merge(players, on='element', how='left')
playersReport


# In[12]:


captainsReport = leaguePlayers.merge(players, on='element', how='left')
captainsReport = playersReport[playersReport.is_captain==True]
captainsReport = captainsReport.reset_index()

captainsReport = captainsReport[['TeamName', 'GW', 'second_name', 'first_name']]
captainsReport


# ## Differentiators

# In[ ]:





# ## Export Reports

# In[13]:


# Export reports 
#dfi.export(topWeeks.head(), 'Top5GW.png')
#dfi.export(benchDF, 'BenchPoints.png'.format(gw))

#dfi.export(topValues, 'TopValues.png'.format(gw))

#dfi.export(captainsReport, 'captains_GW{}.png'.format(gw))


# In[32]:


# Export reports 

css = '''
.dataframe {
  font-family: Arial, Helvetica, sans-serif;
  border-collapse: collapse;
  background-color: white;
}

.dataframe th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #04AA6D;
  color: white;
}
  
.dataframe th, td {
  padding-left: 10px;
  padding-right: 10px;
}
'''

topWeekshtml = topWeeks.head().to_html(index=False)
benchhtml = benchDF.to_html()
valueshtml = topValues.to_html(index=False)
captainshtml = captainsReport.to_html(index=False)

hti.screenshot(html_str=[topWeekshtml, benchhtml, valueshtml, captainshtml], css_str = css, save_as=['topWeeks.png', 'benchGW{}.png'.format(gw), 'valuesGW{}.png'.format(gw), 'captainsGW{}.png'.format(gw)])


# In[ ]:




