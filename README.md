## Damn Small URL Crawler ==> AsyncPyCrawl
Minimal But Powerful Crawler for Extracting all The Internal/External/Fuzz-able Links from a website it can also crawl until 2 depth for each link given. For myself, I added deeper scanning and acceleration through asynchronous threads, maybe it will be useful to someone. This is the essence of the art of github, if you don’t like something then just fix it. This Script is Used for Penetration-Testing and During Ethical Hacking Engagements. This is needed to collect web links that the site uses, and quickly find those that can be sorted out for vulnerabilities..
### Usage 
##### Instalation
`git clone https://github.com/YarBurArt/AsyncPyCrawl.git && cd AsyncPyCrawl && pip install -r	requirements.txt`

Sometimes you may need to create a Python venv environment so as not to break system packages on the latest versions of Python and pip

##### Examples 
 - Normal Crawl
`python3 dsuc.py -u http://testsite.com`
 - Show Fuzzable Links 
`python3 dsuc.py -u http://testsite.com -f` 
 - Show External Links 
`python3 dsuc.py -u http://testsite.com -e` 
 - DeepCrawl_l1 and Show Fuzzable Links 
`python3 dsuc.py -u -d http://testsite.com -f`
 - DeepCrawl_l2 via aiohttp and Show Fuzzable Links 
`python3 dsuc.py -u -d2 http://testsite.com -f`
