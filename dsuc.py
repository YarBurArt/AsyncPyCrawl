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

async def extractor(soup, host_http):
    """ receives bs4 object and in order according 
    to the conditions gets from the page all link"""
    all_links = []
    for link in soup.find_all('a', href=True):
        is_http_www = 'http' in link['href'] or 'www' in link['href']
        is_good_attr = (len(link['href']) > 2) and ('#' not in link['href'])

        # internal links and website buttons
        if link['href'].startswith('/'):
            new_link = f"{host_http}{link['href']}" if link['href'] not in all_links else None
        # links with current host_http
        elif host_http in link['href']:
            new_link = link['href'] if link['href'] not in all_links else None
        # other links via http and https divide
        elif 'http://' in host_http:
            https_host = f"https://{host_http.split('http://')[1]}"
            is_http_in_link = https_host in link['href']
            new_link = link['href'] if is_http_in_link and link['href'] not in all_links else None
        # not a reference to selectors
        elif not is_http_www and is_good_attr:
            new_link = f"{host_http}/{link['href']}" if link['href'] not in all_links else None
        # external links
        elif len(link['href']) > 6:
            external.append(link['href']);new_link = None
        else:
            unknown.append(link['href']);new_link = None

        if new_link:
            all_links.append(new_link)

    return all_links

def fuzzable_extract(linklist):
    """ check for uri parameters """
    return [link for link in linklist if "=" in link]

async def xploit(link, host_http = None):
    """ wrapper with page loading into memory, returns all links """
    if host_http is None:
        host_http = link
    res = requests.get(link, allow_redirects=True, timeout=5)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    res = await extractor(soup, host_http)
    return res

async def level2(linklist, host_http):
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
    parser.add_argument('-o', '--output', help='save to file', dest='output')
    args = parser.parse_args()
    u = args.url

    if u is None:
        sys.exit(0)
    if 'http' not in u:
        u = 'http://' + u
    
    links_g0 = await asyncio.gather(xploit(u))
    links_g1 = list(links_g0)[0]
    
    if args.deepcrawl:
        links = await aio_l2(links_g1, u)
        print('\n\nLINKS WITH DEEPCRAWL : \n\n' if len(links) > 1 else '\n\nNo Link Found\n\n')
        [print('>\t', link) for link in links]
    elif args.deepcrawl2:
        links_l1 = await aio_l2(links_g1, u)
        print('\n\nLinks l1 found\n\n')
        links_l2 = await aio_l2(links_l1, u)
        links_l3 = await aio_l2(set(external), u)
        links = links_l1 | links_l2 | links_l3
        print('\n\nLINKS WITH L1-L3 DEEPCRAWL : \n\n' if len(links) > 1 else '\n\nNo Link Found\n\n')
        [print('>\t', link) for link in links]
    else:
        print('\n\nLINKS : \n\n' if len(links_g1) > 1 else '\n\nNo Link Found\n\n')
        [print('>\t', link) for link in links_g1]

    if args.fuzzable and len(links) > 1 and len(fuzzable_links := fuzzable_extract(links)) > 1:
        print('\n\nFUZZABLE LINKS : \n\n' if len(fuzzable_links) > 1 else '\n\nNo Fuzzable Link Found\n\n')
        [print('>\t', link) for link in fuzzable_links]

    if args.external:
        print('\n\nEXTERNAL LINKS : \n\n' if len(external) > 1 else '\n\nNo EXTERNAL Link Found\n\n')
        [print('>\t', link) for link in set(external) | links]

    if args.output:
        all_lists = [external, unknown, fuzzables]
        with open(str(args.output), 'w') as file:  # write links line by line
            file.writelines('\n'.join(str(item) for sublist in all_lists for item in sublist))
        print("Lists saved to file successfully.")

if __name__ == "__main__":
    BANNER = '''
 _____________________________________________________________________
|CODED BY > R3DXPLOIT(JIMMY)                                          | |
|GITHUB > https://github.com/r3dxpl0it                                | |
|_____________________________________________________________________|/|
'''
    print(BANNER)
    asyncio.run(main())
