from datetime import datetime

import ipaddress
import re
import time

import requests
import sslcheck
import whois
from datetime import date

from bs4 import BeautifulSoup
from dateutil.parser import parse as date_parse
import socket
# Calculates number of months
def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month
checker = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
# Generate data set by extracting the features from the URL
def generate_data_set(url):

    data_set = []

    # Converts the given URL into standard format
    if not re.match(r"^https?", url):
        url = "http://" + url

    # Stores the response of the given URL
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except:
        response = ""
        soup = -999

    # Extracts domain from the given URL
    domain = re.findall(r"://([^/]+)/?", url)[0]
    print("domain : ", domain)

    # Requests all the information about the domain
    whois_response = whois.whois(domain)
    # print("whos : ",whois_response.text)

    rank_checker_response = requests.post("https://www.checkpagerank.net/index.php", {
        "name": domain
    })
    print("rank_checker_response : ",rank_checker_response)
    # Extracts global rank of the website
    try:
        global_rank = int(re.findall(r"Global Rank: ([0-9]+)", rank_checker_response.text)[0])
        print("global_rank : ", global_rank)
    except:
        global_rank = -1

    #1 having_IP_Address , done
    try:
        ipaddress.ip_address(socket.gethostbyname(domain))
        data_set.append(1)
        print("having ip ")
    except Exception as e :
        data_set.append(-1)
        print(e)
    print(data_set)
    print(checker[:])
    
    #2 URL_Length , done
    if len(url) < 54:
        data_set.append(1)
    elif len(url) >= 54 and len(url) <= 75:
        data_set.append(0)
    else:
        data_set.append(-1)
    print(data_set)
    print(checker[1:])
    
    #3 Shortining_Service , done
    if re.findall("goo.gl|bit.ly", url):
        data_set.append(-1)
    else:
        data_set.append(1)
    print(data_set)
    print(checker[2:])
    #4 having_At_Symbol , done
    if re.findall("@", url):
        data_set.append(-1)
    else:
        data_set.append(1)
    print(data_set)
    print(checker[3:])
    #5 double_slash_redirecting
    list = [x.start(0) for x in re.finditer('//', url)]
    if list[len(list) - 1] > 6:
        data_set.append(-1)
    else:
        data_set.append(1)

    print(data_set)
    print(checker[4:])
    #6 Prefix_Suffix
    if re.findall(r"https?://[^\-]+-[^\-]+/", url):
        data_set.append(-1)
    else:
        data_set.append(1)

    print(data_set)
    print(checker[5:])
    #7 having_Sub_Domain
    if len(re.findall("\.", url)) == 1:
        data_set.append(1)
    elif len(re.findall("\.", url)) == 2:
        data_set.append(0)
    else:
        data_set.append(-1)

    print(data_set)
    print(checker[6:])
    
    #8 SSLfinal_State
    try:
        x = sslcheck.final_check_certificate(domain, domain, 443)
        data_set.append(x)
    except:
        data_set.append(-1)
    print(data_set)
    print(checker[7:])
    #9 Domain_registeration_length
    expiration_date = whois_response.expiration_date
    registration_length = 0
    try:
        expiration_date = min(expiration_date)
        today = time.strftime('%Y-%m-%d')
        today = datetime.strptime(today, '%Y-%m-%d')
        registration_length = abs((expiration_date - today).days)

        if registration_length / 365 <= 1:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(-1)

    print(data_set)
    print(checker[8:])

    #10 Favicon
    fdgfdg= 0
    fgjknfjg = 0
    if soup == -999:
        data_set.append(-1)
    else:
        try:
            for head in soup.find_all('head'):
                fgjknfjg+=1
                for head.link in soup.find_all('link', href=True):
                    fdgfdg+=1
                    dots = [x.start(0) for x in re.finditer('\.', head.link['href'])]
                    if url in head.link['href'] or len(dots) == 1 or domain in head.link['href']:
                        data_set.append(1)
                        raise StopIteration
                    else:
                        data_set.append(-1)
                        raise StopIteration
        except StopIteration:
            fdgfdg+=1
            data_set.append(-1)
            ex = False
            pass
    if fdgfdg <1 or fgjknfjg <1:
        data_set.append(-1)

    print(data_set)
    print(checker[9:])
    if len(data_set) > 10:
        del data_set[-1]

    #11. port
    try:
        port = domain.split(":")[1]
        if port:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(1)

    print(data_set)
    print(checker[10:])
    if len(data_set) > 11:
        del data_set[-1]
    #12. HTTPS_token
    if re.findall(r"^https://", url):
        data_set.append(1)
    else:
        data_set.append(-1)

    print(data_set)
    print(checker[11:])
    if len(data_set) > 12:
        del data_set[-1]
    #13. Request_URL
    i = 0
    success = 0
    if soup == -999:
        data_set.append(-1)
    else:
        for img in soup.find_all('img', src= True):
           dots= [x.start(0) for x in re.finditer('\.', img['src'])]
           if url in img['src'] or domain in img['src'] or len(dots)==1:
              success = success + 1
           i=i+1

        for audio in soup.find_all('audio', src= True):
           dots = [x.start(0) for x in re.finditer('\.', audio['src'])]
           if url in audio['src'] or domain in audio['src'] or len(dots)==1:
              success = success + 1
           i=i+1

        for embed in soup.find_all('embed', src= True):
           dots=[x.start(0) for x in re.finditer('\.',embed['src'])]
           if url in embed['src'] or domain in embed['src'] or len(dots)==1:
              success = success + 1
           i=i+1

        for iframe in soup.find_all('iframe', src= True):
           dots=[x.start(0) for x in re.finditer('\.',iframe['src'])]
           if url in iframe['src'] or domain in iframe['src'] or len(dots)==1:
              success = success + 1
           i=i+1

        try:
           percentage = success/float(i) * 100
           if percentage < 22.0 :
               data_set.append(1)
           elif((percentage >= 22.0) and (percentage < 61.0)) :
              data_set.append(0)
           else :
              data_set.append(-1)
        except:
            data_set.append(1)

    print(data_set)
    print(checker[12:])
    print("dat 12 : ",len(data_set))
    if len(data_set) > 13:
        del data_set[-1]
    #14. URL_of_Anchor
    percentage = 0
    i = 0
    unsafe=0
    if soup == -999:
        data_set.append(-1)
    else:
        for a in soup.find_all('a', href=True):
        # 2nd condition was 'JavaScript ::void(0)' but we put JavaScript because the space between javascript and :: might not be
                # there in the actual a['href']
            if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in a['href'].lower() or not (url in a['href'] or domain in a['href']):
                unsafe = unsafe + 1
            i = i + 1


        try:
            percentage = unsafe / float(i) * 100
        except:
            data_set.append(1)

        if percentage < 31.0:
            data_set.append(1)
        elif ((percentage >= 31.0) and (percentage < 67.0)):
            data_set.append(0)
        else:
            data_set.append(-1)

    print(data_set)
    print(checker[13:])
    if len(data_set) > 14:
        del data_set[-1]
    #15. Links_in_tags
    i=0
    success =0
    if soup == -999:
        data_set.append(-1)
    else:
        for link in soup.find_all('link', href= True):
           dots=[x.start(0) for x in re.finditer('\.',link['href'])]
           if url in link['href'] or domain in link['href'] or len(dots)==1:
              success = success + 1
           i=i+1

        for script in soup.find_all('script', src= True):
           dots=[x.start(0) for x in re.finditer('\.',script['src'])]
           if url in script['src'] or domain in script['src'] or len(dots)==1 :
              success = success + 1
           i=i+1
        try:
            percentage = success / float(i) * 100
            if percentage < 17.0:
                data_set.append(1)
            elif ((percentage >= 17.0) and (percentage < 81.0)):
                data_set.append(0)
            else:
                data_set.append(-1)
        except:
            data_set.append(1)

    if len(data_set) > 15:
        del data_set[-1]

    print(data_set)
    print(checker[14:])

    #16. SFH
    if len(soup.find_all('form', action= True))<1:
        data_set.append(1)
    for form in soup.find_all('form', action= True):

       if form['action'] =="" or form['action'] == "about:blank" :
          data_set.append(-1)
          print("for don \n")
          break
       elif url not in form['action'] and domain not in form['action']:
           data_set.append(0)
           print("for don \n")
           break
       else:
             data_set.append(1)
             print("for don \n")
             break


    print(data_set)
    print(checker[15:])
    if len(data_set) > 16:
        del data_set[-1]
    #17. Submitting_to_email
    if response == "":
        data_set.append(-1)
    else:
        if re.findall(r"[mail\(\)|mailto:?]", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)

    print(data_set)
    print(checker[16:])
    if len(data_set) > 17:
        del data_set[-1]
    #18. Abnormal_URL
    if response == "":
        data_set.append(-1)
    else:
        if response.text == "":
            data_set.append(1)
        else:
            data_set.append(-1)
    if len(data_set) > 18:
        del data_set[-1]
    print(data_set)
    print(checker[17:])

    #19. Redirect
    if response == "":
        data_set.append(-1)
    else:
        if len(response.history) <= 1:
            data_set.append(-1)
        elif len(response.history) <= 4:
            data_set.append(0)
        else:
            data_set.append(1)
    if len(data_set) > 19:
        del data_set[-1]
    print(data_set)
    print(checker[18:])

    # 20. on_mouseover
    if response == "":
        data_set.append(-1)
    else:
        if re.findall("<script>.+onmouseover.+</script>", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)
    if len(data_set) > 20:
        del data_set[-1]
    print(data_set)
    print(checker[19:])

    # 21. RightClick
    if response == "":
        data_set.append(-1)
    else:
        if re.findall(r"event.button ?== ?2", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)
    if len(data_set) > 21:
        del data_set[-1]
    print(data_set)
    print(checker[20:])

    #22 popUpWidnow
    if response == "":
        data_set.append(-1)
    else:
        if re.findall(r"alert\(", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)
    if len(data_set) > 22:
        del data_set[-1]
    print(data_set)
    print(checker[21:])
    #23 Iframe
    if response == "":
        data_set.append(-1)
    else:
        if re.findall(r"[<iframe>|<frameBorder>]", response.text):
            data_set.append(1)
        else:
            data_set.append(-1)
    if len(data_set) > 23:
        del data_set[-1]
    print(data_set)
    print(checker[22:])
    #24 age_of_domain
    try:
        registration_date = re.findall(r'Registration Date:</div><div class="df-value">([^<]+)</div>', whois_response.text)[0]
        if diff_month(date.today(), date_parse(registration_date)) >= 6:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        data_set.append(1)
    print(data_set)
    print(checker[23:])
    if len(data_set) > 24:
        del data_set[-1]
    #25 DNSRecord
    dns = 1
    try:
        d = whois.whois(domain)
    except:
        dns = -1
    if dns == -1:
        data_set.append(-1)
    else:
        if registration_length / 365 <= 1:
            data_set.append(-1)
        else:
            data_set.append(1)
    print(data_set)
    print(checker[24:])
    if len(data_set) > 25:
        del data_set[-1]
    #26 web_traffic
    try:
        if global_rank > 0 and global_rank < 100000:
            data_set.append(1)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)
    print(data_set)
    print(checker[25:])
    if len(data_set) > 26:
        del data_set[-1]
    #27 Page_Rank , done
    try:
        if global_rank > 0 and global_rank < 100000:
            data_set.append(1)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)
    print(data_set)
    print(checker[26:])
    if len(data_set) > 27:
        del data_set[-1]
    #28 Google_Index , done
    try:
        if global_rank > 0 and global_rank < 100000:
            data_set.append(1)
        else:
            data_set.append(-1)
    except:
        data_set.append(-1)
    print(data_set)
    print(checker[27:])
    if len(data_set) > 28:
        del data_set[-1]
    #29 Links_pointing_to_page
    number_of_links = len(re.findall(r"<a href=", response.text))
    if number_of_links == 0:
        data_set.append(-1)
    elif number_of_links <= 5:
        data_set.append(0)
    else:
        data_set.append(1)
    print(data_set)
    print(checker[28:])
    if len(data_set) > 29:
        del data_set[-1]
    #30 Statistical_report
    url_match = re.search(
        'at\.ua|usa\.cc|baltazarpresentes\.com\.br|pe\.hu|esy\.es|hol\.es|sweddy\.com|myjino\.ru|96\.lt|ow\.ly', url)
    try:
        ip_address = socket.gethostbyname(domain)
        ip_match = re.search(
            '146\.112\.61\.108|213\.174\.157\.151|121\.50\.168\.88|192\.185\.217\.116|78\.46\.211\.158|181\.174\.165\.13|46\.242\.145\.103|121\.50\.168\.40|83\.125\.22\.219|46\.242\.145\.98|'
            '107\.151\.148\.44|107\.151\.148\.107|64\.70\.19\.203|199\.184\.144\.27|107\.151\.148\.108|107\.151\.148\.109|119\.28\.52\.61|54\.83\.43\.69|52\.69\.166\.231|216\.58\.192\.225|'
            '118\.184\.25\.86|67\.208\.74\.71|23\.253\.126\.58|104\.239\.157\.210|175\.126\.123\.219|141\.8\.224\.221|10\.10\.10\.10|43\.229\.108\.32|103\.232\.215\.140|69\.172\.201\.153|'
            '216\.218\.185\.162|54\.225\.104\.146|103\.243\.24\.98|199\.59\.243\.120|31\.170\.160\.61|213\.19\.128\.77|62\.113\.226\.131|208\.100\.26\.234|195\.16\.127\.102|195\.16\.127\.157|'
            '34\.196\.13\.28|103\.224\.212\.222|172\.217\.4\.225|54\.72\.9\.51|192\.64\.147\.141|198\.200\.56\.183|23\.253\.164\.103|52\.48\.191\.26|52\.214\.197\.72|87\.98\.255\.18|209\.99\.17\.27|'
            '216\.38\.62\.18|104\.130\.124\.96|47\.89\.58\.141|78\.46\.211\.158|54\.86\.225\.156|54\.82\.156\.19|37\.157\.192\.102|204\.11\.56\.48|110\.34\.231\.42',
            ip_address)
        if url_match:
            data_set.append(-1)
        elif ip_match:
            data_set.append(-1)
        else:
            data_set.append(1)
    except:
        print("error")

    print(data_set)
    print(checker[29:])
    if len(data_set) > 30:
        del data_set[-1]
    print (data_set)
    print("OK")

    return data_set
# generate_data_set("www.google.com")