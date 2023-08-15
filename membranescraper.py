import requests
import bs4
from dateutil import parser
import datetime
import csv

# Is the line a membrane header?
def isMembraneLine(line, membranes):
    return line in membranes

# Is the line a date?
def isDateLine(line, dates):
    if line.strip().upper() == "NO DATE":
        return True
    if line in dates:
        try:
            if parser.parse(line).year<2001 and parser.parse(line).year>500:
                return True
        except ValueError:
            return False
    return False

# Parse the line and return it as a python datetime.date
def parseDate(line):
    if line.strip().upper() == "NO DATE":
        return "No date"
    # if parser.parse(line).year < 1200 or parser.parse(line).year > 1500:
    #     print(parser.parse(line).strftime("%Y/%m/%d"))
    return parser.parse(line).strftime("%Y/%m/%d")

# Open the list of URLs
with open("urls.txt") as urls:
    entries = []
    for url in urls:
        html  = requests.get(url.strip()).text
        soup = bs4.BeautifulSoup(html, 'html.parser')
        t = soup.find_all("div",class_="inner")[0].text
        with open ("text.txt", "w") as out:
            out.write(t)
        h3s = soup.find_all("div",class_="inner")[0].find_all("h3")
        membranes = []
        # Grab all the header3s inside, which are membrane labels
        for h3 in h3s:
            membranes.append(h3.text)
        ems = soup.find_all("div",class_="inner")[0].find_all("em")
        dates = []
        # Grab all the em tags, which are dates
        for em in ems:
            dates.append(em.text)
        roll = soup.find_all("h1",class_="page-header")[0].text.strip()
        membrane = None
        date = None
        text = ""
        #First line is empty, so start from line 1
        for line in t.splitlines()[1:]:
            # Is the line not a date or a membrane (i.e. is text)
            if not isDateLine(line, dates) and not isMembraneLine(line,membranes):
                text = text+" "+line.strip()
                continue
            else:
                # append entry only if it's complete (has date, membrane, text)
                if date != None and membrane != None and len(text.strip())>0:
                    entries.append({"roll":roll, "membrane":membrane, "date":date, "text":text.strip()})
                text = ""
                if isDateLine(line, dates):
                    date = parseDate(line)
                elif isMembraneLine(line, membranes):
                    membrane = line.strip()
        entries.append({"roll":roll, "membrane":membrane, "date":date, "text":text.strip()})

    with open('rolls.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=entries[0].keys())
        writer.writeheader()
        writer.writerows(entries)