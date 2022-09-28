import requests
from bs4 import BeautifulSoup
import re
import csv
from tkinter import *
import os
import urllib.request
from textwrap import wrap
baseUrl = "http://books.toscrape.com/"
en_tete = ["product_page_url","universal_ product_code (upc)","title","price_including_tax","price_excluding_tax","number_available","product_description","category","review_rating","image_url"]
categoryLinks = []
maxNameSize = 75

def getCategoryLinks():
    page = requests.get(baseUrl)
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

def getInfos(book):
    page = requests.get(book)
    page.encoding = "utf-8"
    if page.ok:
        soup = BeautifulSoup(page.text, "html.parser")
        return [book, getUpc(soup), getTitle(soup), getPriceIncludingTax(soup),
               getPriceExcludingTax(soup), getNumberAvailable(soup), getProductDescription(soup),
               getCategory(soup), getRating(soup), getImgUrl(soup)]

def siteScraping():
    j = 0
    for category in getCategoryLinks():
        with open("data/site/" + getCategoryName(category) + ".csv", "w+", encoding="utf-16", newline="") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow(en_tete)
            i = 0
            for book in getBookLinks(category):
                infos = getInfos(book)
                writer.writerow(infos)
                urllib.request.urlretrieve(infos[9], "data/site/images/" + getBookName(book) + ".jpg")
                print(infos[7] + " - " + infos[2])
                i += 1
                j += 1
            print(str(i) + " livres trouvés dans la catégorie : " + infos[7])
    print(str(j) + " livres trouvés au total")
    print("données du site obtenues avec succés et sauvegardées dans data/site")
    print("images obtenues avec succés et sauvegardées dans data/site/images")

def getCategoryName(category):
    return category.split("books/")[1].split("_")[0]

def selectCategory(window, mode):
    window.destroy()
    window = Tk()
    window.resizable(False, False)
    window.title("Category selection")
    if mode == "bookscraping":
        label = Label(window, text="Selectionnez la catégorie du livre")
    else:
        label = Label(window, text="Quelle catégorie voulez-vous scraper?")
    label.grid(row=0,column=2)
    Button(window, text="retour", command=lambda: mainMenu(window)).grid(row=0, column=3)
    i = 0
    j = 1
    for category in getCategoryLinks():
        if mode == "categoryscraping":
            Button(window, text=getCategoryName(category), command=lambda category=category:categoryScraping(category), width=30).grid(row=j, column=i)
        else:
            Button(window, text=getCategoryName(category), command=lambda category=category:selectBook(window, category), width=30).grid(row=j, column=i)
        i += 1
        if (i%5==0):
            i = 0
            j += 1
    window.mainloop()



def categoryScraping(category):
    with open("data/category/" + getCategoryName(category) + ".csv", "w+", encoding="utf-16", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(en_tete)
        i = 0
        for book in getBookLinks(category):
            infos = getInfos(book)
            writer.writerow(infos)
            urllib.request.urlretrieve(infos[9], "data/category/images/" + getBookName(book) + ".jpg")
            print(infos[7] + " - " + infos[2])
            i += 1
        print(str(i) + " livres trouvés")
        print("données obtenues avec succés et sauvegardées dans data/category/" + getCategoryName(category) + ".csv")
        print("images obtenues avec succés et sauvegardées dans data/category/images")


def getBookName(book):
    name = book.split("catalogue/")[1].split("_")[0]
    if len(name) > maxNameSize:
        name = wrap(name, maxNameSize)[0] + "..."
    return name


def bookScraping(book):
    with open("data/book/" + getBookName(book) + ".csv", "w+", encoding="utf-16", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(en_tete)
        infos = getInfos(book)
        writer.writerow(infos)
        urllib.request.urlretrieve(infos[9], "data/book/images/" + getBookName(book) + ".jpg")
        print(infos[7] + " - " + infos[2])
        print("image obtenue avec succés et sauvegardé dans data/book/images/" + getBookName(book) + ".jpg")
        print("données obtenues avec succés et sauvegardées dans data/book/" + getBookName(book) + ".csv")


def selectBook(window, category):
    window.destroy()
    window = Tk()
    window.resizable(False, False)
    window.title("Book selection")
    label = Label(window, text="Selectionnez le livre à scraper")
    label.grid(row=0,column=1)
    Button(window, text="retour", command=lambda:selectCategory(window, "bookscraping")).grid(row=0, column=2)
    i = 0
    j = 1
    for book in getBookLinks(category):
            Button(window, text=getBookName(book), command=lambda book=book:bookScraping(book), width=60).grid(row=j, column=i)
            i += 1
            if (i%3==0):
                i = 0
                j += 1
    window.mainloop()

def mainMenu(window):
    if window != "firstlaunch":
        window.destroy()
    window = Tk()
    window.resizable(False, False)
    window.title("Web Scraping")
    window.geometry("250x75")
    label = Label(window, text="Quelles informations voulez-vous recuperer?")
    label.pack()
    Button(window, text="livre", command=lambda: selectCategory(window, "bookscraping")).pack(side=LEFT, expand=True)
    Button(window, text="catégorie", command=lambda: selectCategory(window, "categoryscraping")).pack(side=LEFT, expand=True)
    Button(window, text="site", command=siteScraping).pack(side=LEFT, expand=True)
    window.mainloop()

def createDir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def main():
    createDir("data")
    createDir("data/book")
    createDir("data/category")
    createDir("data/site")
    createDir("data/book/images")
    createDir("data/category/images")
    createDir("data/site/images")
    mainMenu("firstlaunch")

if __name__=="__main__":
    main()