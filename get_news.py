# NEWS-GPT
# News-gpt is a bot that gets the most recent articles on Data Science from the internet then uses OpenAI GPT-3.5 to summarize the articles and publish them in an easy to read GitHub repo
# This script uses multiple local tmp files to logically seperate tasks
# I've cleaned up some of the date variables but a significant amount of consolidation could happen

# Requirements
# dotenv, openai, base64

# Imports
import os
from dotenv import load_dotenv
import requests
import json
import openai
from base64 import b64encode
from datetime import date, timedelta

# Load environment variables
load_dotenv()
API = os.getenv('API')
GPT = os.getenv('NEWS_GPT')
GIT = os.getenv('GIT')

# Use NewsAPI to get articles
#set variables
q = 'data analytics'
domains = 'forbes.com, venturebeat.com, searchbusinessanalytics.techtarget.com, www.informationweek.com/big-data-analytics.asp, www.zdnet.com/topic/big-data-analytics, www.datasciencecentral.com, www.kdnuggets.com, www.analyticsinsight.net, www.datanami.com, Bloomberg' # comma seperated
day = date.today()
date_from = day - timedelta(days=1)
date_to = day
language = 'en'
sortBy = 'relevancy' # relevancy, popularity, publishedAT
pageSize = 5 # set max number of articles you'd like to summarize
page = 1

#make request
# api_url = f"https://newsapi.org/v2/everything?q={q}&apiKey={API}&from={date_from}&to={date_to}&language={language}&sortBy={sortBy}&pageSize={pageSize}&page={page}"
api_url = f"https://newsapi.org/v2/everything?q={q}&apiKey={API}&domains={domains}&from={date_from}&to={date_to}&language={language}&sortBy={sortBy}&pageSize={pageSize}&page={page}"
response = requests.get(api_url)
data = response.json()
print(data)

#write news to tmp file
with open('tmp_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# read and parse json from tmp
with open('tmp_data.json') as data_tmp_file:
    data_string = data_tmp_file.read()
data = json.loads(data_string)
    
openai.api_key = GPT

for i in data['articles']:
    article = i['url']
    content = f"Provide a summary of this article in 3 bullet points (format 1, 2, 3). Condense the response and remove fillers like 'the article' and 'the author':{article}"
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])

    # append summary(completion) to data
    summary = completion.choices[0].message.content
    i['summary'] = summary 

    # print(completion.choices[0].message.content)

# write summarized output to file
with open('tmp_summarized_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# Write a markdown file to be used as the daily post

with open('tmp_summarized_data.json') as data_tmp_file:
    data_string = data_tmp_file.read()
data = json.loads(data_string)

# Write top of post file
topic = 'Data Analytics'

top = f"---\ntitle: Rollup for {day}\ndate: {day}\ndescription: GPT generated news rollup for {day}\ntag: {topic}\nauthor: System\n---\n# {topic} news for {day}\n"

# Parse data from summarized posts and put into markdown format
post = ''

for i in data['articles']:
    #get variables from json
    title = i['title']
    source = i['source']['name']
    url = i['url']
    summary = i['summary']

    #write variables to file
    md_title = '### '+title
    md_credit = '_['+source+']('+url+')_'
    md_summary = summary
    
    post += f'{md_title}\n{md_credit}\n{md_summary}\n'
    
# print(post)

# write the markdown file
f = open('tmp_newpost.mdx','w')
f.write(
    top +
    post
)
f.close()

# Post request returns 201


repo = 'mattray-xyz'
path = 'pages/posts'
owner = 'mdray'

# Base64 endoce new post
with open('tmp_newpost.mdx', 'r') as file:
    data = file.read()

data_bytes = data.encode('utf8')
# print(data_bytes)
data_b64 = b64encode(data_bytes)
# print(data_b64)
b64 = data_b64.decode('utf8')
# print(b64)

# Write GitHub API variables
header = {'Authorization':'Bearer ' +GIT, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}/{day}.mdx'
message = {'message':'my commit message', 'content':f'{b64}'}

response = requests.put(url=url, headers=header, json=message)
print(response)
# print(response.request.url)
# print(response.request.body)
# print(response.request.headers) # Contains passwords