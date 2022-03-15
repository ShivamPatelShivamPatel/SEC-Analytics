import requests
from bs4 import BeautifulSoup
import json
import hashlib
import concurrent.futures 
from bs4 import BeautifulSoup
from datetime import date
from time import sleep
from time import perf_counter
import pandas as pd
import numpy as np

def today():
    today = str(date.today())
    return today

Today = today()

def main():
    #inputs = createInputs()
    headers = {
            'User-Agent':'joe@joe.ede',
            'Accept-Encoding':'gzip, deflate',
            'Host':'www.sec.gov'
        }

    _url = "https://www.sec.gov/Archives/edgar/Oldloads/"#r"https://www.sec.gov/Archives/edgar/Oldloads/"
    _years = [str(year) for year in range(1996,2023)]
    _quarters = ["/QTR1/", "/QTR2/", "/QTR3/", "/QTR4/"]
    urls = []
    
    for year in _years:
        for quarter in _quarters:
            if(year == "2022" and quarter != "/QTR1/"):
                break
            urls.append(_url+year+quarter)
    #print(urls)
    i = 17
    t = 1
    results = []
    sizes = []
    quarters = []
    years = []
    dates = []
    for url in urls:
        #print(url)
        #response = requests.get(url, headers=inputs[i]['headers'],proxies=inputs[i]['proxies'])
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
        print("status: " + str(response.status_code) + " " + url[len(_url):])
        #print(soup)
        anchors = soup.findAll('a')
        td = soup.findAll('td')
        td = list(filter(lambda x: "KB" in x.text, td))
        sizes += list(map(lambda x: [int(x.text[:len(x.text)-3]),
                                     int(x.text[:len(x.text)-3])*0.001024,
                                     int(x.text[:len(x.text)-3])*9.5367431640625E-7], td))
        results += [url + x.text for x in anchors if url[len(_url):len(_url)+4] in x.text]
        if(t == 10):
            #i = (i+1) % len(inputs)
            print ("slept 1 second")
            sleep(1)
            t = 0
        print(t)
        t += 1

    results = np.array(["urls"] + results)
    #print(sizes)
    sizes = np.vstack([["KB","MB","GB"]] + [size for size in sizes])

    results.shape =  (max([dim for dim in results.shape]), 1)
    sizes.shape = (max([dim for dim in sizes.shape]), 3)
    pd.DataFrame(np.hstack([sizes, results])).to_csv("oldLoads.csv", index=False)
    print("Success: Check oldLoads.csv")
    #with open("oldLoadsSizes.txt","w") as f:
    #    f.writelines(sizes)
    #    print(len(sizes))
    #with open("oldLoadsURLs.txt","w") as f:
    #    f.writelines(results)
    #    print(len(results))
if __name__ == '__main__':
    main()

