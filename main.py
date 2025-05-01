from bs4 import BeautifulSoup
import mechanize #https://pypi.org/project/mechanize/
from mechanize.polyglot import HTTPError

import json
import sys
import re

url = 'https://infosimples.com/vagas/desafio/commercia/product.html'

resposta_final = {}

br = mechanize.Browser()
br.set_handle_robots(False)

try:
    br.open("https://infosimples.com/vagas/desafio/commercia/product.html")
except HTTPError as e:
    print("Aconteceu algum erro ao entrar no site! Veja o log:")
    sys.exit(f"{e.code}: {e.msg}")

soup = BeautifulSoup(br.response(), features="html5lib")
#print(soup.prettify())

resposta_final["title"] = soup.find(id="product_title").string

resposta_final["brand"] = soup.find("div", "brand").string

html_nav = soup.nav.find_all("a")
lst_nav = []
for a in html_nav:
    lst_nav.append(a.string)
resposta_final["categories"] = lst_nav

html_descricao = soup.find("div", "proddet")
txt_descricao = ""
for texto in html_descricao.children:
    if texto.string == "Description":
        continue
    txt_descricao = txt_descricao + " " + texto.string.strip()
resposta_final["description"] = txt_descricao

class Skus:
    def __init__(self, name, available, current_price = None, old_price = None):
        self.name = name
        self.current_price = current_price
        self.old_price = old_price
        self.available = available

html_skus = soup.find("div", "skus-area").find_all("div", "card")
lst_skus = []
for card in html_skus:
    avaliable = "not-avaliable" not in card.attrs["class"]
    pnow = card.find("div", "card-container").find("div", "prod-pnow")
    pold = card.find("div", "card-container").find("div", "prod-pold")
    if pnow != None:
        pnow = float(card.find("div", "card-container").find("div", "prod-pnow").string.replace("R$","").replace(",","."))
    if pold != None:
        pold = float(card.find("div", "card-container").find("div", "prod-pold").string.replace("R$","").replace(",","."))
    
    lst_skus.append(Skus(
        card.find("div", "card-container").find("div", "prod-nome").string,
        avaliable,
        pnow,
        pold
    ).__dict__)
resposta_final["skus"] = lst_skus

class Property:
    def __init__(self, label, value=None):
        self.label=label
        self.value=value
html_prop = soup.find_all("table", "pure-table")
lst_prop = []
for prop in html_prop:
    values_tr = prop.tbody.find_all("tr")
    for tr in values_tr:
        values_td = tr.find_all("td")
        lst_prop.append(Property(values_td[0].b.string, values_td[1].string).__dict__)
resposta_final["properties"] = lst_prop

class Reviews:
    def __init__(self, name, date, score, text):
        self.name = name
        self.date = date
        self.score = score
        self.text = text
def starsToInt(stars):
    match stars:
        case "★☆☆☆☆":
            return 1
        case "★★☆☆☆":
            return 2
        case "★★★☆☆":
            return 3
        case "★★★★☆":
            return 4
        case "★★★★★":
            return 5

html_comments = soup.find(id="comments").find_all("div", "analisebox")
lst_comments = []
for comment in html_comments:
    lst_comments.append(Reviews(
        comment.find("div", "pure-u-21-24").find("span", "analiseusername").string,
        comment.find("div", "pure-u-21-24").find("span", "analisedate").string,
        starsToInt(comment.find("div", "pure-u-21-24").find("span", "analisestars").string),
        comment.p.string
        ).__dict__)
resposta_final["reviews"] = lst_comments

resposta_final["reviews_average_score"] = float(soup.find("h4", string=re.compile("Average score:")).string.replace("Average score:", "").replace("/5", ""))

resposta_final["url"] = url

with open("produto.json", "w") as outfile:
    json.dump(resposta_final, outfile)
