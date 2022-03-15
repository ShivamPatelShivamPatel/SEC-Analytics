import requests
import json
import threading
import hashlib
import concurrent.futures 
from bs4 import BeautifulSoup
from datetime import date
from time import sleep
from time import perf_counter

def today():
    today = str(date.today())
    return today

Today = today()

def createUserAgent(ip):
    h = hashlib.blake2b(digest_size=5)
    h.update(str(ip).encode())
    return h.hexdigest()

def createInputs(num):
    with open("proxylist.txt",'r') as f:
        proxyList = f.read().split("\n")
        #print(proxyList)
 
    inputs = []
    for i in range(num):#range(len(proxyList)):
        if(len(proxyList[i]) <= 0):
            continue

        split = proxyList[i].split(':')
        proxyList[i] = {'ip':split[0], 'port':split[1], 'user':split[2], 'pass':split[3]}
        proxyHash = str(createUserAgent(proxyList[i]['ip']))
        
        proxies = {
            "http" : "http://"  + proxyList[i]['user'] + ':' + proxyList[i]['pass'] + '@' + proxyList[i]['ip'] + ":" + proxyList[i]['port'],
            "https": "https://" + proxyList[i]['user'] + ':' + proxyList[i]['pass'] + '@' + proxyList[i]['ip'] + ":" + proxyList[i]['port']
        }


        headers = {
            'User-Agent':proxyHash[0:5] + "@" + proxyHash[5:] + ".edu",
            'Accept-Encoding':'gzip, deflate',
            'Host':'www.sec.gov'
        }

        inputs.append({'headers':headers, 'proxies':proxies})

    return inputs

def generateForm4URLs(cik_str, inputs):
    entries = []
    EdgarEndpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"

    params = {
        'action':'getcompany',
        'CIK':cik_str,
        'type':'4',
        'dateb':Today,
        'owner':'include',
        'output':'atom',
        'count':'100'
    }

    url = EdgarEndpoint
    t = perf_counter()
    running_count = 0
    retry = 0
    while True:
        if(running_count == 10):
            sleep(1)
            running_count = 0
        try:
            response = requests.get(url, 
                    headers = inputs['headers'], 
                    params = params, 
                    proxies = inputs['proxies']
                    )
            running_count += 1
            soup = BeautifulSoup(response.content, 'lxml')
            
            localEntries = soup.find_all('entry')
            if(len(localEntries) <= 0): # this is the case it throws a 200 and returns 0 so genuinely 0 records for a company
                with open(cik_str + "error.txt","w") as f:
                    f.write(response.text)
                    f.write(response.status_code)

            else:
                entries += localEntries
            
            print("in CIK: " + cik_str + " just fetched " + str(len(localEntries)) + " records" + " status code: " + str(response.status_code))

        except:
            print("error inside CIK: " + cik_str)
            print("status code: " + str(response.status_code)) #this is the case it throws a 503 which is an error
            with open(cik_str + "error.txt","w") as f:
                f.write(response.text)
                f.write(response.status_code)
            break
       
        #if(len(soup.find_all('entry')) == 0):
            #print(entries[-1])
        if ((int(entries[-1].find('filing-date').text.split("-")[0]) < 2011) or
           (soup.find_all('link', {'rel':'next'}) == [])):
            break
        
        else:
            url = soup.find_all('link', {'rel':'next'})[0]['href']

    return (cik_str, perf_counter()-t, len(entries), entries)

def main():

    MasterJsonEndpoint = r"https://www.sec.gov/files/company_tickers.json"
    MasterCompanyList = json.loads(requests.get(MasterJsonEndpoint).text)
    numThread = 15
    headersAndProxies = createInputs(numThread)
    inputs = [(MasterCompanyList[str(i)]['cik_str'],headersAndProxies[i%len(headersAndProxies)]) for i in range(len(MasterCompanyList))]
    entries = []
   
    for i in range(numThread,len(inputs),numThread):
        with concurrent.futures.ThreadPoolExecutor(max_workers = numThread) as executor:
            futures = [executor.submit(generateForm4URLs, str(content[0]), content[1]) for content in inputs[i-numThread:i]]

            for task in concurrent.futures.as_completed(futures):
                cik_str, t, count, localEntries = task.result()
                entries += localEntries
                print("CIK: " + cik_str + " time: " + str(t) + " count: " + str(count))
    #filtered = list(filter(lambda entry: int(entry.find('filing-date').text.split("-")[0]) >= 2011, entries))
    #mapped = list(map(lambda entry: entry.find('filing-href').text, filtered))
   
    #fileName = params['CIK'] + "form4URLs.txt"
    #with open(filename, "w") as f:
        #f.writelines(mapped)

    #print("found %d",len(soup.find_all('link', {'rel':'alternate'})))
    return

if __name__ == '__main__':
    main()
