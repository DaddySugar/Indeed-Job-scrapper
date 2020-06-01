from bs4 import BeautifulSoup
import urllib.request as ur
import re
import json 
import pprint

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Jobs you DO NOT like
red_flags = ["business", "dernière année", "marketing", "commercial", "vente"]
# Jobs you Do like
required = ["software", "java", "c++", "c/c++", "python"]

    # Check the title for jobs you like
def check_tittle(title):
    title = title.lower()
    for word in required:
        if word in title: return True
    for word in red_flags:
        if word in title: return False
    return True

#test:
assert(check_tittle("Senior Software Engineer"))
assert(check_tittle("Stage anglais - Business Developper H/F") == False)
assert(check_tittle("Chargé de projet Web Marketing") == False)


p1 = re.compile('([bB]ac[a-zA-Z]*[ ]?\+[0-4]+)|([cC].sure)')

    # Niveau d'etude
t1 = p1.search("Bac+4")
t2 = p1.search("Césure")


#print (t1, "\n",t2)


    # Save progress
def saveData(l, file, jj=True):
    with open(file, 'w') as outfile:
        json.dump(l, outfile, sort_keys=True, indent=4) #, default_flow_style=False)
    if jj:
        print(bcolors.WARNING, len(l), " jobs found" + bcolors.ENDC)


        # Get HTML page
def get_pages(soup):
    
    total_txt = soup.find(id="searchCountPages").get_text().strip()
    
    count_temp = re.findall(r'\d.?\d*', total_txt)
    total_count = count_temp[-1].replace(u'\xa0', u'')
    print("Total jobs: ", total_count)
    
    
    last_page = int(int(total_count) / 10) * 10
    print("Last page: " + str(last_page))
    if last_page == 0 or total_count == 0:
        print("=== Error; Jobs not found! ===")
        return None, None
    return total_count, last_page


    # Add the job
def addToDic(perfect, B, comp, title, d, toVisit):
    #print((bcolors.OKGREEN if B else ""), d , "Days ago", " -- ", title, ", ", comp, ": " + (bcolors.ENDC if B else ""), toVisit,"\n")
    if B:
        perfect[comp].append({'title' : title, 'date' : d, 'perfect' : "YES", 'link' :toVisit})
    else:
        perfect[comp].append({'title' : title, 'date' : d, 'perfect' : "IDK", 'link' :toVisit})

   # Check if the job already added  
def alreadyAdded(D, B, comp, title, d, toVisit):
    if comp in D:
        for dd in D[comp]:
            if dd['title'] == title:
                    if int(d) < int(dd['date']):
                        dd['date'] = d 
    else:
        D[comp] = []
        addToDic(D, B, comp, title, d, toVisit)


def iterate_job(soup, last_page, url):
    jobs_per_page = 10
    title = ""
    comp = ""
    d = ""
    for pgno in range(0, last_page, jobs_per_page):
        if pgno > 0:
            try:
                response = ur.urlopen(url + str(pgno))
                html_doc = response.read()
            except:
                break;
            soup = BeautifulSoup(html_doc, 'html.parser')
        
        for job in soup.find_all(class_='result'):
            
            link = job.find(class_="turnstileLink")
            title = link.get('title')
            comp = job.find(class_='company').get_text().strip()
            date = re.findall(r'\d+', job.find(class_='date').get_text())
            d = date[-1] if len(date) != 0 else "0"
            
            if(check_tittle(title.lower())):
                toVisit = "http://www.indeed.com"+link.get('href')
                try:
                    html_doc = ur.urlopen(toVisit).read().decode('utf-8')
                except:
                    continue;
                m = p1.search(html_doc)
                alreadyAdded(perfect_offers, m, comp, title, d, toVisit)
        return perfect_offers



# Start the search
def searchIndeed(url_base):
    pgno = 0
    try:
        response = ur.urlopen(url_base+ str(pgno))
        html_doc = response.read()
    except:
        print("URL not accesible")
        exit();
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    pages = get_pages(soup)
    
    l =  iterate_job(soup, pages[1], url_base)
    saveData(l, 'jobs.json')
    return l


    # Load progress 
def loadJson():
    try:
        with open('jobs.json', 'r') as content_file:
            data = json.load(content_file)
        return data
    except:
        return {}



perfect_offers = loadJson()
searchIndeed("https://www.indeed.fr/jobs?q=stage+%28C%2B%2B+or+C+or+JAVA+or+Python+or+stage+or+intern+or+BAC%2B4+or+software+or+D%C3%A9veloppement+or+dev+or+developer%29&l=Paris+%2875%29&jt=internship&ts=1590924912532&pts=1590663558146&rq=1&rsIdx=0")
searchIndeed("https://www.indeed.fr/emplois?q=developpeur&l=Paris+(75)&jt=internship")
displayJobs = pprint.pformat(perfect_offers, indent=4, width=90)

saveData(displayJobs, "jobsDisplay.txt", False)