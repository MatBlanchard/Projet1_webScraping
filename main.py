import requests
from bs4 import BeautifulSoup
import re
import csv
baseUrl = "http://books.toscrape.com/"
en_tete = ["product_page_url","universal_ product_code (upc)","title","price_including_tax","price_excluding_tax","number_available","product_description","category","review_rating","image_url"]
categoryLinks = []

def getCategoryLinks(url):
    page = requests.get(url)
    if len(categoryLinks) == 0:
        if page.ok:
            soup = BeautifulSoup(page.text, "html.parser")
            links = soup.findAll("a")
            for link in links:
                if len(link["href"].split("/")) > 1 and link["href"].split("/")[1] == "category":
                    categoryLinks.append(baseUrl + link["href"])
        categoryLinks.pop(0)
        return categoryLinks
    else:
        return categoryLinks

def findAllBooks(pageUrl):
    page = requests.get(pageUrl)
    bookLinks = []
    if page.ok:
        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.findAll("a")
        i = 1
        for link in links:
            if len(link["href"].split("../../../")) > 1 and i % 2 != 0 and i != 1:
                bookLinks.append(baseUrl + "catalogue/" + link["href"].split("../../../")[1])
            i += 1
        return bookLinks

def nextExist(pageUrl):
    page = requests.get(pageUrl)
    if page.ok:
        soup = BeautifulSoup(page.text, "html.parser")
        if soup.find("li", class_="next"):
            return True
        else:
            return False
    return False

def getBookLinks(categoryUrl):
    bookLinks = findAllBooks(categoryUrl)
    if nextExist(categoryUrl):
        pageUrl = categoryUrl.split("index.html")[0] + "page-2.html"
        i = 2
        while True:
            bookLinks = bookLinks + findAllBooks(pageUrl)
            if not nextExist(pageUrl):
                break
            else:
                pageUrl = pageUrl.split("-" + str(i) + ".html")[0] + "-" + str(i + 1) + ".html"
                i += 1
    return bookLinks

def ratingToNumber(string):
    if string == "One":
        return 1
    elif string == "Two":
        return 2
    elif string == "Three":
        return 3
    elif string == "Four":
        return 4
    elif string == "Five":
        return 5

def getUpc(soup):
    return soup.findAll("td")[0].text

def getTitle(soup):
    return soup.find("li", class_="active").text

def getPriceIncludingTax(soup):
    return soup.findAll("td")[3].text

def getPriceExcludingTax(soup):
    return soup.findAll("td")[2].text

def getNumberAvailable(soup):
    return re.findall('\d+', soup.findAll("td")[5].text)[0]

def getProductDescription(soup):
    return soup.findAll("p")[3].text

def getCategory(soup):
    return soup.findAll("a")[3].text

def getRating(soup):
    return ratingToNumber(soup.find("p", class_="star-rating")["class"][1])

def getImgUrl(soup):
    return baseUrl + soup.find("img")["src"].split("../../")[1]

#if __main__ ==
j = 0
for category in getCategoryLinks(baseUrl):
    with open("data/" + category.split("books/")[1].split("_")[0] + ".csv", "w+", encoding="utf-16", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(en_tete)
        i = 0
        for book in getBookLinks(category):
            page = requests.get(book)
            page.encoding = "utf-8"
            if page.ok:
                soup = BeautifulSoup(page.text, "html.parser")
                cat = getCategory(soup)
                title = getTitle(soup)
                row = [book,getUpc(soup),title,getPriceIncludingTax(soup),
                       getPriceExcludingTax(soup),getNumberAvailable(soup),getProductDescription(soup),
                       cat,getRating(soup),getImgUrl(soup)]
                writer.writerow(row)
                print(cat + " - " + title)
                i += 1
                j += 1
        print(str(i) + " livres trouvés dans la catégorie: " + cat)
print(str(j) + " livres trouvés au total")

