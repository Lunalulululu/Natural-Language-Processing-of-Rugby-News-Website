#!/usr/bin/env python
# coding: utf-8



# In[18]:

# COMP20008 Assignemnt 1 Task 1 - 5
import nltk
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from urllib.parse import urljoin
import pandas as pd
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import json
import seaborn as sns
page_limit = 999

# task 1

# the crawling method is modified from workshop 5 code
#Specify the initial page to crawl
nltk.download('punkt')
seed_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'


page = requests.get(seed_url)
soup = BeautifulSoup(page.text, 'html.parser')

visited = {}; 
visited[seed_url] = True
urls = []
pages_visited = 1


# Initialise links to visit
links = soup.findAll('a')
to_visit_relative = links
headlines = []
to_visit = []

for link in to_visit_relative:
    to_visit.append(urljoin(seed_url, link['href']))

#Find all outbound links on succsesor pages and explore each one 
while (to_visit):
    


    # Impose a limit to avoid breaking the site 
    if pages_visited == page_limit :
        break
        
    # consume the list of urls
    link = to_visit.pop(0)
    urls.append(link)
    # need to concat with base_url, an example item <a href="catalogue/sharp-objects_997/index.html">
    page = requests.get(link)
    
    # scarping code goes here
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # mark the item as visited, i.e., add to visited list, remove from to_visit
    visited[link] = True
    new_links = soup.findAll('a')
    
    sections = soup.find_all(attrs={"class": "headline"})

    for section in sections:
        headlines.append(section.text)
    

    
    
    for new_link in new_links:
        new_item = new_link['href']
        new_url = urljoin(link, new_item)
        if new_url not in visited and new_url not in to_visit:
            to_visit.append(new_url)
    
    pages_visited = pages_visited + 1
    
        

df = pd.DataFrame({'url': urls,
                   'headline': headlines})

df.to_csv('task1.csv', index = False)







# Task 2

with open('rugby.json') as f:
    Data = json.load(f)


teamnames = {dict['name'].split()[-1]: dict['name'] for dict in Data['teams']}

#Specify the initial page to crawl
seed_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'


page = requests.get(seed_url)
soup = BeautifulSoup(page.text, 'html.parser')

visited = {}; 
visited[seed_url] = True
urls = []
pages_visited = 1

# Initialise links to visit
links = soup.findAll('a')
to_visit_relative = links


headlines = []
team = []
team_score = []
to_visit = []

for link in to_visit_relative:
    to_visit.append(urljoin(seed_url, link['href']))

#Find all outbound links on succsesor pages and explore each one 
while (to_visit):
    
    # Impose a limit to avoid breaking the site 
    if pages_visited == page_limit :
        break
        
    # consume the list of urls
    link = to_visit.pop(0)
    urls.append(link)
    # need to concat with base_url, an example item <a href="catalogue/sharp-objects_997/index.html">
    page = requests.get(link)
    
    # scarping code goes here
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # mark the item as visited, i.e., add to visited list, remove from to_visit
    visited[link] = True
    new_links = soup.findAll('a')
    
    sections = soup.findAll(attrs={"class": "headline"})
    for section in sections:
        headlines.append(section.text)
    


    # find the first team occurs in the article
    body_text = []
    found = False
    tokenizer = RegexpTokenizer(r'\w+')

  
    
    body = soup.findAll('div', id = 'main_article')
    body_text=[re.sub(r'<.+?>',r'',str(a)) for a in body]



          
    for row in body_text:
        for word in tokenizer.tokenize(row):
            if word in teamnames:
                team.append(teamnames[word])
                found = True
                break
        if found:
            break

    if not found:
        team.append(None)

    
    scores = []

    # finding all scores 
  
    pattern = r'[\s\.\,\?\;\:\'\"\(\[\{\*\!]\d{1,3}\-\d{1,3}[\s\.\,\?\;\:\'\"\)\]\}\*\!]'

    for row in body_text:
        scores.extend(re.findall(pattern, row))


    # determine maximum score for the team
    pun = '.,?;:\'\"()[]{}*! \n\t\r\f'
    max_index = 0
    i = 0
    max_sum = 0
    if scores: 
        for score in scores:
            no = score.split('-')
            for number in no:
                sum = int(no[0].strip(pun)) + int(no[1].strip(pun))
                if sum > max_sum:
                    max_sum = sum
                    max_index = i
            i += 1
        team_score.append(scores[max_index].strip(pun))
    else:
        team_score.append(None) 

    # visit next pages
    for new_link in new_links:
        new_item = new_link['href']
        new_url = urljoin(link, new_item)
        if new_url not in visited and new_url not in to_visit:
            to_visit.append(new_url)
    
    pages_visited = pages_visited + 1
    
    
    
df2 = pd.DataFrame({'url': urls,
                   'headline': headlines,
                   'team': team,
                   'score': team_score})
df2.dropna(inplace = True)
df2.to_csv('task2.csv', index = False)


# Task 3
# a function to caculate game difference
def game_diff(scores):
    score = scores.split('-')
    diff = abs(int(score[0]) - int(score[1]))
    return diff

df3 = pd.DataFrame({'team': team,
                   'score': team_score})
df3.dropna(inplace=True)


df3['game_diff'] = df2['score'].apply(lambda x: game_diff(x))

df3['avg_game_difference'] = df3['game_diff'].groupby(df3['team']).transform('mean')

df3 = pd.DataFrame({'team': df3['team'],
                   'avg_game_difference': df3['avg_game_difference'] })

df3.reset_index(drop = True, inplace = True)
df3.drop_duplicates(inplace = True)
df3.to_csv('task3.csv', index = False)

# Task 4

df4 = df2['team'].value_counts().sort_index(ascending=False).sort_values(ascending=False).head(5).rename_axis('team').reset_index(name = 'counts')
df4.reset_index(drop = True, inplace = True)

plt.bar(df4['team'], df4['counts'])
plt.ylabel('frequency')
plt.title("Top 5 Most Frequent Wrote About Team")
plt.savefig('task4.png')
plt.clf()


# Task 5
# find a team average_game_differnece and frequency of occurences
df41 = df2['team'].value_counts().rename_axis('team').reset_index(name = 'counts')
df3 = df3.sort_values('avg_game_difference', ascending = False)
df5 = pd.merge(df3, df41, on='team', how='inner')

sns.set()
df5 = df5.set_index('team')

fig,ax = plt.subplots()
plt.title("Comparing Average Game Difference and Frequency of Occurence")
ax2 = ax.twinx()
width = .3

df5.avg_game_difference.plot(kind = 'bar',color = 'green',ax = ax,width = width, position=1)
df5.counts.plot(kind = 'bar',color = 'blue', ax = ax2, width = width, position=0)

ax.grid(None)
ax2.grid(None)
ax.set_ylabel('avg_game_difference')
ax2.set_ylabel('frequency_of_occurence')
plt.gcf().subplots_adjust(bottom=0.3)

# adding legends
legend1 = mpatches.Patch(color='green', label='avg_game_difference')
legend2 = mpatches.Patch(color='blue', label='frequency_of_occurence')
plt.legend(handles=[legend1, legend2])
fig.savefig('task5.png')
plt.clf()





    
# In[ ]:






# %%
