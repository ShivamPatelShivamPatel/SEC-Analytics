# SEC-Analytics
## A (in progress) System to download all 2-3 TB of historical SEC filings, run statistics on them, and then download the new daily filings to search for *

### You will need a list of proxys formatted to host:user:password:ip:port to be able to run TestGenerateEntries(basic template of how to webscrape new filings of type form 4, can easily reconfigure to download any type of forms) but feel free to run downloadOldLoads.py, as well feel free to steal from me and redistribute oldLoads.csv so that maybe someone building a similar system doesnt have to manually construct the URL list.

### downloadOldLoadsSEC.py is a file that will generate a CSV corresponding to 6000+ days of daily filings of american corporations with the SEC.  If you attempt to download the contents of all the urls contained in oldLoads.csv, it will be about 2-3 tb at the current time of writing.  Daily increase is about 1.5 gb per day.
