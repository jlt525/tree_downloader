from urllib.request import urlopen
from bs4 import BeautifulSoup
from os import getcwd as cwd
from os import makedirs as mkdirs
from os import path as ospath
import wget

ROOT = "https://www.shoarmateam.nl/upload/Lexus/IS200+IS300/"
NO_MAKE_STACK = True
DEBUG = True
WORKDIR = '/workdir/'
LEAF_INDICATORS = [ ".pdf", ".txt", "wget", "a123", "ad54332", "a2345" ]

def main(root):
    absoluteWorkdir = cwd() + WORKDIR
    if DEBUG == True:
        print("Absolute path to workdir", absoluteWorkdir)

    if ospath.exists(absoluteWorkdir) == False:
        mkdirs(absoluteWorkdir)
        if DEBUG == True:
            print("Making workdir:", absoluteWorkdir)
    else:
        if DEBUG == True:
            print("Workdir exists:", absoluteWorkdir)

    noMakeStack = NO_MAKE_STACK
    stack = mkUrlStack(root, noMakeStack)

    mkTreeSkeleton(stack, absoluteWorkdir)

    populateTree(stack, absoluteWorkdir)

def mkUrlStack(root, noMakeStack = False, downloadLog=cwd()+"/.downloaded_files", stackFile=cwd()+"/.stack"):
    stackFilePath = str(stackFile)
    with urlopen(root) as html_src:
        soup = BeautifulSoup(html_src, 'html.parser')
        if DEBUG == True:
            print("got root:", root)

    stack = []

    if ospath.exists(stackFile) == True:
        if DEBUG == True:
            print("Found stackfile:", stackFile)
        with open(stackFilePath, 'r') as stackFile:
            for line in stackFile:
                stack.append(line.strip("\n"))
        if noMakeStack == True:
            return stack
    else:
        if DEBUG == True:
            print("Making stackfile:", stackFile)
        with open(stackFilePath, 'w') as stackFile:
            stackFile.write(root + "\n")

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
                            with open(stackFilePath, 'a+') as stackFile:
                                stackFile.write(url + a.get('href') + "\n")

                            if DEBUG == True:
                                print("pushed", url + a.get('href'), "to stack")
                                print()
                        else:
                            if DEBUG == True:
                                print()

        elif DEBUG == True:
            print("hit leaf:", url)

    if DEBUG == True:
        print("Items on stack", len(stack))

    return stack

def mkTreeSkeleton(stack, absoluteWorkdir):
    for node in stack:
        if DEBUG == True:
            print()
            print("Stack position", stack.index(node), "-", node)

        relativePath = node.replace(ROOT, "").replace("%20", " ")
        if DEBUG == True:
            print("relative path:", relativePath)

        absolutePath = absoluteWorkdir + relativePath

        if bool([element for element in LEAF_INDICATORS if(element in str(relativePath))]) == False:
            if ospath.exists(absolutePath) == False:
                if DEBUG == True:
                    print("Making directory:", absolutePath)

                mkdirs(absolutePath)
            else:
                if DEBUG == True:
                    print("Directory exists:", absolutePath)

def populateTree(stack, absoluteWorkdir, stackFile = cwd() + "/.stack"):
    stackFilePath = str(stackFile)
    downloadLog = cwd() + "/.downloaded_files"

    while len(stack) != 0:
        node = stack.pop()

        if DEBUG == True:
            print("Stack position", len(stack), "-", node)

        relativePath = node.replace(ROOT, "").replace("%20", " ")
        if DEBUG == True:
            print("relative path:", relativePath)

        absolutePath = absoluteWorkdir + relativePath

        if DEBUG == True:
            print("Downloading:", node)
            print("\tTo:", absolutePath)

        if ospath.exists(absolutePath) == False:
            wget.download(node.replace("%20", " "), absolutePath)
        else:
            if DEBUG == True:
                print("File already exists:", absolutePath)

        with open(downloadLog, 'a') as log:
            log.write(node + "\n")

        with open(stackFilePath, 'r') as stackFile:
            lines = stackFile.readlines()
            with open(stackFilePath, 'w') as stackFile:
                for line in lines:
                    if line.strip('\n') != node:
                        stackFile.write(line)


if __name__ == "__main__":
    main(ROOT)
