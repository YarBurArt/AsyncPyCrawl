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
import argparse, sys, requests, bs4, asyncio, aiohttp

external, unknown, fuzzables = [], [], []

def extractor(soup, host_http):
    """ receives bs4 object and in order according 
    to the conditions gets from the page all link"""
    all_links = []
    for link in soup.find_all('a', href=True):
        is_http_www = 'http' in link['href'] or 'www' in link['href']
        is_good_attr = (len(link['href']) > 2) and ('#' not in link['href'])
        
        if link['href'].startswith('/'): # for internal links and website buttons
            new_link = host_http + link['href'] if link['href'] not in all_links else None
        elif host_http in link['href']: # for links with current host_http
            new_link = link['href'] if link['href'] not in all_links else None
        elif 'http://' in host_http:  # for other links via http and https
            is_http_in_link = 'https://' + host_http.split('http://')[1] in link['href']
            new_link = link['href'] if is_http_in_link and link['href'] not in all_links else None
        elif not is_http_www and is_good_attr: # this is not a reference to selectors
            new_link = host_http + '/' + link['href'] if link['href'] not in all_links else None
        elif len(link['href']) > 6:  # for external links
            external.append(link['href']);new_link = None
        else:
            unknown.append(link['href']);new_link = None

        if new_link:
            all_links.append(new_link)
    return all_links

def fuzzable_extract(linklist):
    """ check for uri parameters """
    return [link for link in linklist if "=" in link]

def xploit(link, host_http = None):
    """ wrapper with page loading into memory, returns all links """
    if host_http is None:
        host_http = link
    res = requests.get(link, allow_redirects=True, timeout=5)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    return extractor(soup, host_http)

def level2(linklist, host_http):
    """ check the child's unique links of links """
    final_list = set()
    [final_list.add(in_links) or print("Appended", in_links) for link in linklist for in_links in xploit(link, host_http) if in_links not in final_list]
    final_list.update(linklist)
    return list(final_list)

async def aio_l2(linklist, host_http):
    """ creates async tasks and collects them in a deeper scanning set """
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
    parser.add_argument('-d', '--deepcrawl', help='crawl deaply',
        dest='deepcrawl', action='store_true')
    parser.add_argument('-d2', '--deepcrawl2', help='crawl deaply 2',
        dest='deepcrawl2', action='store_true')
    parser.add_argument('-f', '--fuzzable', help='extract fuzzable',
        dest='fuzzable', action='store_true')
    parser.add_argument('-e', '--external', help='extract external',
        dest='external', action='store_true')
    args = parser.parse_args()
    u = args.url

    if u is None:
        sys.exit(0)
    if 'http' not in u:
        u = 'http://' + u

    if args.deepcrawl:
        links = await aio_l2(xploit(u), u)
        message = '\n\nLINKS WITH DEEPCRAWL : \n\n' if len(links) > 1 else '\n\nNo Link Found\n\n'
        [print('>\t', link) for link in links] if len(links) > 1 else print(message)
    elif args.deepcrawl2:
        links_l1 = await aio_l2(xploit(u), u)
        print('\n\nLinks l1 found\n\n')
        links_l2 = await aio_l2(links_l1, u)
        links_l3 = await aio_l2(set(external), u)
        links = links_l1 | links_l2 | links_l3
        message = '\n\nLINKS WITH L3 DEEPCRAWL : \n\n' if len(links) > 1 else '\n\nNo Link Found\n\n'
        [print('>\t', link) for link in links] if len(links) > 1 else print(message)
    else:
        links = xploit(u)
        message = '\n\nLINKS : \n\n' if len(links) > 1 else '\n\nNo Link Found\n\n'
        [print('>\t', link) for link in links] if len(links) > 1 else print(message)

    if args.fuzzable and len(links) > 1 and len(fuzzable_links := fuzzable_extract(links)) > 1:
        print('\n\nFUZZABLE LINKS : \n\n')
        [print('>\t', link) for link in fuzzable_links]
    elif args.fuzzable:
        print('\n\nNo Fuzzable Link Found\n\n')

    if args.external and len(external) > 1:
        print('\n\nEXTERNAL LINKS : \n\n')
        [print('>\t', link) for link in set(external) | links]
    elif args.external:
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
