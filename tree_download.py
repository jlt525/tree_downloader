from urllib.request import urlopen
from bs4 import BeautifulSoup

ROOT = "https://www.shoarmateam.nl/upload/Lexus/IS200+IS300/"
DEBUG = False

def main(root):
    with urlopen(root) as html_src:
        soup = BeautifulSoup(html_src, 'html.parser')
        if DEBUG == True:
            print("got root:", root)

    stack = []
    stack.append(root)

    limit = len(stack)
    for y in stack:
        index = stack.index(y)
        url = stack[index]
        if DEBUG == True:
            print("using url:", stack[index])
        
        if not any(x in url for x in ['.pdf', '.txt']):
            with urlopen(url) as html_src:
                soup = BeautifulSoup(html_src, 'html.parser')
                if DEBUG == True:
                    print("got url:", url)
            for a in soup.find_all('a'):
                if a.get('href') not in url:
                    path = url + a.get('href')
                    if DEBUG == True:
                        print("path:", path)
                    if path not in url:
                        if not any(s for s in stack if path in s):
                            stack.append(url + a.get('href'))
                            if DEBUG == True:
                                print("pushed", url + a.get('href'), "to stack")
        elif DEBUG == True:
            print("hit leaf:", url)

    for node in stack:
        print(node)
    print(len(stack))


if __name__ == "__main__":
    main(ROOT)
