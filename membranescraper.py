import requests
import bs4
import parsedatetime
import datetime
import csv

cal = parsedatetime.Calendar()

# Is the line a membrane header?
def isMembraneLine(line, membranes):
    return line in membranes

# Is the line a date?
def isDateLine(line):
    if line.strip().upper() == "NO DATE":
        return True
    date = datetime.date(*cal.parse(line)[0][:-6])
    # parsedatetime hungrily parses nondate strings as the current datetime
    # return False (not a date) if the year is in this millenium
    return date.year<2001

# Parse the line and return it as a python datetime.date
def parseDate(line):
    if line.strip().upper() == "NO DATE":
        return "No date"
    date = datetime.date(*cal.parse(line)[0][:-6])
    return date

# Open the list of URLs
with open("urls.txt") as urls:
    entries = []
    for url in urls:
        html  = requests.get(url.strip()).text
        soup = bs4.BeautifulSoup(html, 'html.parser')
        t = soup.find_all("div",class_="inner")[0].text
        h3s = soup.find_all("div",class_="inner")[0].find_all("h3")
        membranes = []
        # Grab all the headers inside, which are membrane labels
        for h3 in h3s:
            membranes.append(h3.text)
        roll = soup.find_all("h1",class_="page-header")[0].text
        membrane = None
        date = None
        text = ""

        for line in t.splitlines()[1:]:
            # Is the line not a date or a membrane (i.e. is text)
            if not isDateLine(line) and not isMembraneLine(line,membranes):
                text = text+" "+line
                continue
            else:
                # append entry only if it's complete (has date, membrane, text)
                if date != None and membrane != None and len(text)>0:
                    entries.append({"roll":roll, "membrane":membrane, "date":date, "text":text})
                text = ""
                if isDateLine(line):
                    date = parseDate(line)
                elif isMembraneLine(line, membranes):
                    membrane = line.strip()
        entries.append({"roll":roll, "membrane":membrane, "date":date, "text":text})

    with open('rolls.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=entries[0].keys())
        writer.writeheader()
        writer.writerows(entries)