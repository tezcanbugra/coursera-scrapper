import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import re
import uuid
from requests import Session
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor


s = Session()
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '\
                         'AppleWebKit/537.36 (KHTML, like Gecko) '\
                         'Chrome/75.0.3770.80 Safari/537.36'}
# Add headers
s.headers.update(headers)

categories = {

    "data-science": "https://www.coursera.org/browse/data-science",
    "business": "https://www.coursera.org/browse/business",
    "computer-science": "https://www.coursera.org/browse/computer-science",
    "personal-development": "https://www.coursera.org/browse/personal-development",
    "information-technology": "https://www.coursera.org/browse/information-technology",
    "language-learning": "https://www.coursera.org/browse/language-learning",
    "health": "https://www.coursera.org/browse/health",
    "math-and-logic": "https://www.coursera.org/browse/math-and-logic",
    "social-sciences": "https://www.coursera.org/browse/social-sciences",
    "physical-science-and-engineering": "https://www.coursera.org/browse/physical-science-and-engineering",
    "arts-and-humanities": "https://www.coursera.org/browse/arts-and-humanities"
}


selectedCategory = ''

types = [
    "degrees",
    "specializations",
    "learn",
    "projects",
    "professional-certificates"
]
courseDetails = [
    'Category',
    'Course Name',
    'First Instructor Name',
    'Course Description',
    '# of Students Enrolled',
    '# of Ratings'
]

df = pd.DataFrame(columns=['Category',
                           'Course Name',
                           'First Instructor Name',
                           'Course Description',
                           '# of Students Enrolled',
                           '# of Ratings'])


def scrapCourses(search):
    print(search)
    courses = []
    category = search.lower().replace(" ", "-").replace("ı","i")
    global selectedCategory
    selectedCategory = category
    if category in categories:
        URL = categories[category]
        response = s.get(URL).text
        soup = bs(response, "lxml")
        tags = soup.findAll("div", class_="rc-BrowseDegreeCard")[0]
        for link in soup.select('a'):
            for type in types:
                if type in link.get('href') and link.get('href').startswith('/'):
                    courses.append(link.get('href'))
        courses = list(set(courses))
    else:
        return -1
    return courses


def visitCourse(courses):
    i=0
    baseURL = "https://www.coursera.org"
    with ThreadPoolExecutor(max_workers=20) as executor:
        [executor.submit(visitPage,courseIndex=i,courses=courses) for i in range(len(courses))]
    filename = str(uuid.uuid4()) + '.csv'
    df.to_csv(filename, sep='\t', encoding='utf-8', index=None)
    return filename

def visitPage(courseIndex,courses):
    baseURL = "https://www.coursera.org"
    courseURL = baseURL + courses[courseIndex]
    response = s.get(courseURL)
    soup = bs(response.text, "lxml")
    try:
        title = soup.select("h1", class_="banner-title")[0].text
        instructor = soup.select(
            "#main > div._12gv18d9 > div > div > div > a > div > div > span")[0].text
        description = soup.select(
            "#main > div > div.rc-XdpSection.cdp-about.css-yw2k7b > div > div > div > div._1b7vhsnq.m-t-2 > div.m-t-1.description > div > div > div > p")[0].text
        enrolled = soup.find("div", class_="_1fpiay2").text.split(' ')[0]
        ratings = soup.select(
            "#main > div._iul6hq > div > div > div.rc-RatingLink > ul > li > a > div > span")[0].text.replace('stars', '')
        re.sub("\+\d more", "", instructor)
        line = [selectedCategory, title, instructor,
                description, enrolled, ratings]
        df.loc[courseIndex+1] = line
        print(line)
    except:
        pass
    return line
