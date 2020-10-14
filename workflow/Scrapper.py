from apps.Scrapper_template import Scrapper

brows = 'chrome'
link = "https://www.google.com/alerts?q=axiata"



Scrap = Scrapper(brows,link)

print(Scrap.snippet())





