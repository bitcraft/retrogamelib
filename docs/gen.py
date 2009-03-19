import os
nav = open("source/nav.html").read()
for file in os.listdir("source"):
    if file == "nav.html":
        continue
    if file == ".svn":
        continue
    f = open("source/"+file, "rb")
    txt = f.read().replace("..NAV", nav)
    f.close()
    f = open(file, "wb")
    f.write(txt)
    f.close()