from imgfetcher import ImgFetcher
import urllib2
import xml.etree.ElementTree as ET
from lxml import etree
from xml.parsers.expat import ParserCreate
import re

url = "http://dcimg.awalker.jp/img1.php?id=sAyiHSEOO5sEEkFzaxcs7zs11B8BQJ0OpyKWbD2LL6aIJZ0gTTrTRX6n7GWvO048hiLQl0lWK4Nz9yMv0I0htYFkvjJgAG543iZ9IftC8GGHOKqDymb6rGxfGp2lbmzf0TCHHy1elgJAPENEoQzWkDmal12WPEKo4mqv8S9oXTshbZxBQ1BADuzg8o5OpNCNsheEDkMx"
response = urllib2.urlopen(url, timeout = 60).read()
print response
pattern = r'http://dcimg\.awalker\.jp/img2\.php\?sec_key=[a-zA-Z0-9]*'
print re.search(pattern, response).group(0)

# fetcher = ImgFetcher(url=url, verbose=3)
# fetcher.fetch()