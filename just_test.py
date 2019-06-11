import ipaddress
import re
import socket
from datetime import date

import requests

# rank_checker_response = requests.post("https://www.checkpagerank.net/index.php", {
#     "name": "www.palvps.com"
# })
# print(rank_checker_response.text)
import sslcheck
# try:
#     x = sslcheck.final_check_certificate("www.palvps.com","www.palvps.com",443)
#     print(x)
# except:
#     print(False)
import whois
#
whois_response = whois.whois("www.palvps.com")
# print(whois_response)
# ipaddress.ip_address(socket.gethostbyname("www.google.com"))

# rank_checker_response = requests.post("https://www.checkpagerank.net/index.php", {
#     "name": "www.iugaza.edu.ps"
# })
# print(rank_checker_response.text)
# global_rank = int(re.findall(r"Global Rank: ([0-9]+)", rank_checker_response.text)[0])
# print(global_rank)
from bs4 import BeautifulSoup
import urllib.request
# url = "https://www.google.com"
# rank = \
# BeautifulSoup(urllib.request.urlopen("http://data.alexa.com/data?cli=100&dat=s&url=" + url).read(), "xml").find("REACH")[
#     'RANK']
# print(rank)
import requests
# url = "google.com"
# # res = requests.get("https://www.similarweb.com/website/iugaza.edu.ps")
# r = urllib.request.urlopen("https://www.similarweb.com/website/gazaskygeeks.com").read()
# # print("ok")
# # print(res.text)
# soup = BeautifulSoup(r)
# spans = soup.find_all('span', attrs={'class':'engagementInfo-valueNumber js-countValue'})
#
# num = str(spans[0].string).lower()
# if "k" in num:
#     num = num[:len(num)-1]
#     print (float(num)*1000)



##############
# age_of_domain
from dateutil.parser import parse as date_parse

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

try:
    registration_date = re.findall(r'Registration Date:</div><div class="df-value">([^<]+)</div>', whois_response.text)[
        0]
    if diff_month(date.today(), date_parse(registration_date)) >= 6:
        print(-1)
    else:
        print(1)
except:
    print(1)