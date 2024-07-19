'''_____________________________________________________________________
|[] R3DXPL0IT SHELL                                            |ROOT]|!"|
|"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""|"| 
|CODED BY > R3DXPLOIT(JIMMY)                                          | |
|UPGRADED BY > YARBURART                                              | |
|EMAIL > RETURN_ROOT@PROTONMAIL.COM                                   | |
|GITHUB > https://github.com/r3dxpl0it                                | |
|WEB-PAGE > https://r3dxpl0it.Github.io                               |_|
|_____________________________________________________________________|/|
'''
import argparse
import sys
import requests
import bs4
import asyncio
import aiohttp

external  = []
unknown   = []
fuzzables = []

def extractor(soup, host_http):
    """ receives bs4 object and in order according 
    to the conditions gets from the page all link"""
    all_links = []
    for link in soup.find_all('a', href=True):
        is_http_www = 'http' in link['href'] or 'www' in link['href']
        is_good_attr = (len(link['href']) > 2) and ('#' not in link['href'])
        if link['href'].startswith('/'):  # for internal links and website buttons
            if link['href'] not in all_links:
                all_links.append(host_http+link['href'])
        elif host_http in link['href']:  # for links with current host_http
            if link['href'] not in all_links:
                all_links.append(link['href'])
        elif 'http://' in host_http:  # for other links via http and https
            is_http_in_link = 'https://'+host_http.split('http://')[1] in link['href']
            is_new_link = link['href'] not in all_links
            if is_http_in_link and is_new_link:
                all_links.append(link['href'])
        elif not is_http_www and is_good_attr: # this is not a reference to selectors
            if link['href'] not in all_links:
                all_links.append(host_http+'/'+link['href'])
        elif len(link['href']) > 6: # for external links
            external.append(link['href'])
        else:
            unknown.append(link['href'])
    return all_links


def fuzzable_extract(linklist):
    """ check for uri parameters """
    fuzzables = []
    for link in linklist:
        if "=" in link:
            fuzzables.append(link)
    return fuzzables


def xploit(link, host_http = None):
    """ wrapper with page loading into memory, returns all links """
    if host_http is None:
        host_http = link
    res = requests.get(link, allow_redirects=True)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    return extractor(soup, host_http)

def level2(linklist, host_http):
    """ check the child's unique links of links """
    final_list = []
    for link in linklist:
        for in_links in xploit(link , host_http):
            if in_links not in final_list:
                final_list.append(in_links)
                print("Appended", in_links)
        if link not in final_list:
            final_list.append(link)
    return final_list


async def aio_l2(linklist, host_http):
    async with aiohttp.ClientSession() as session:
        async def aio_xploit(link):
            try:
                res = await session.get(link)
                soup = bs4.BeautifulSoup(await res.text(), 'lxml')
                return extractor(soup, host_http)
            except Exception as e:
                print(f"Bits url: {link}: {e}"); return None 
        # get unique links, including errors, works through list magic in python
        return set([item for item in await asyncio.gather(*[aio_xploit(link) for link in linklist]) if item is not None][0])

async def main():
    """ user interface through cli arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='root url', dest='url')
    parser.add_argument(
        '-d', '--deepcrawl', help='crawl deaply',
        dest='deepcrawl', action='store_true')
    parser.add_argument(
        '-d2', '--deepcrawl2', help='crawl deaply 2',
        dest='deepcrawl2', action='store_true')
    parser.add_argument(
        '-f', '--fuzzable', help='extract fuzzable',
        dest='fuzzable', action='store_true')
    parser.add_argument(
        '-e', '--external', help='extract external',
        dest='external', action='store_true')
    args = parser.parse_args()

    if args.url is None:
        sys.exit(0)
    if 'http' not in args.url:
        args.url = 'http://' + args.url

    if args.deepcrawl:
		# TODO: level3, multithreads
        links = await aio_l2(xploit(args.url) , args.url)
        if len(links) > 1:
            print('\n\nLINKS WITH DEEPCRAWL : \n\n')
            for link in links:
                print('>\t' , link)
        else:
            print('\n\nNo Link Found\n\n')
    elif args.deepcrawl2:
        links_l1 = await aio_l2(xploit(args.url) , args.url)
        print('\n\nLinks l1 found\n\n')
        links_l2 = await aio_l2(links_l1, args.url)
        links_l3 = await aio_l2(set(external), args.url)
        links = links_l1 | links_l2 | links_l3
        if len(links) > 1:
            print('\n\nLINKS WITH L3 DEEPCRAWL : \n\n')
            for link in links:
                print('>\t' , link)
        else:
            print('\n\nNo Link Found\n\n')
    else:
        links =xploit(args.url)
        if len(links) > 1:
            print('\n\nLINKS : \n\n')
            for link in links:
                print('>\t', link)
        else:
            print('\n\nNo Link Found\n\n')

    if args.fuzzable:
        if len(links) > 1:
            if len(fuzzable_extract(links)) > 1:
                print('\n\nFUZZABLE LINKS : \n\n')
                for link in fuzzable_extract(links):
                    print('>\t' , link)
            else:
                print('\n\nNo Fuzzable Link Found\n\n')

    if args.external:
        if  len(external) > 1:
            print('\n\nEXTERNAL LINKS : \n\n')
            for link in set(external) | links:
                print('>\t' , link)
        else:
            print('\n\nNo EXTERNAL Link Found\n\n')


if __name__ == "__main__":
    BANNER = '''
 _____________________________________________________________________
|CODED BY > R3DXPLOIT(JIMMY)                                          | |
|GITHUB > https://github.com/r3dxpl0it                                | |
|_____________________________________________________________________|/|
'''
    print(BANNER)
    asyncio.run(main())
