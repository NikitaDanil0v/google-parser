import requests
from bs4 import BeautifulSoup as bs
from python3_anticaptcha import NoCaptchaTaskProxyless

class GoogleParser():

    def __init__(self):
        self.ANTICAPTCHA_KEY = ""
        self.names = None
        self.services = ["facebook.com", "youtube.com", "twitter.com", "linkedin.com"]
        self.headers = {}

    def writeData(self, name, type, text):
        f = open("./data.txt", "a")
        f.write("{}\t{}\t{}\n".format(name, type, text))
        f.close()

    def checkCaptcha(self, input):
        if "Our systems have detected unusual traffic from your computer network" in input.text:
            SITE_KEY = "6LfwuyUTAAAAAOAmoS0fdqijC2PbbdH4kjq62Y1b"
            PAGE_URL = "https://ipv4.google.com/sorry/index"

            print('got captcha, requesting anticaptcha')
            user_answer = NoCaptchaTaskProxyless.NoCaptchaTaskProxyless(anticaptcha_key=self.ANTICAPTCHA_KEY) \
                .captcha_handler(websiteURL=PAGE_URL,
                                 websiteKey=SITE_KEY)

            inbs = bs(input.text)
            acq = inbs.find("input", {"type": "hidden", "name": "q"}).attrs['value']
            acc = inbs.find("input", {"type": "hidden", "name": "continue"}).attrs['value']
            sr = requests.post("https://ipv4.google.com/sorry/index", {
                "g-recaptcha-response": user_answer['solution']['gRecaptchaResponse'],
                "q": acq,
                "continue": acc,
                "submit": "Submit"
            }, headers=self.headers)
            return self.checkCaptcha(sr)

        return input

    def run(self):
        for name in self.names:

            # SEARCHING FOR PERSONAL WEBSITE
            sk = requests.get("https://www.google.com/search?dcr=0&source=hp&q={}&oq={}&".format(name, name), headers=self.headers)
            sk = self.checkCaptcha(sk)

            skbs = bs(sk.text)
            results = skbs.findAll("div", {"class": "g"})

            i = 0
            for result in results:
                if i < 3:
                    try:
                        title = result.find("a").text
                        desc = result.find("span", {"class": "st"}).text
                        url = result.find("a").attrs['href'].split("url?q=")[1]

                        if name.lower() in title.lower() or name.lower() in desc.lower():
                            bad = False
                            for srvs in self.services:
                                if srvs in url:
                                    bad = True
                            if not bad:
                                self.writeData(name, "website", url.split("&sa")[0])

                        i += 1
                    except:
                        print("picblock")

            # SEARCHING FOR SOCIAL NETWORK PROFILES
            for service in self.services:
                print(name, service)
                search_phrase = "{} site:{}".format(name, service)
                f = requests.get("https://www.google.com/search?dcr=0&source=hp&q={}&oq={}&".format(search_phrase, search_phrase), headers=self.headers)
                f = self.checkCaptcha(f)

                fbs = bs(f.text)
                results = fbs.findAll("div", {"class": "g"})
                links = []
                for result in results:
                    if len(links) < 3:
                        try:
                            link = result.find("a").attrs['href'].split("url?q=")[1].split("&sa")[0]

                            if service == "youtube.com":
                                if "https://www.youtube.com/channel/" in link or "https://www.youtube.com/user/" in link:
                                    links.append(link)
                                continue

                            if service == "facebook.com":
                                if "https://www.facebook.com/public/" not in link:
                                    links.append(link)
                                continue

                            links.append(link)
                        except:
                            print('picblock')

                if len(links)>0:
                    self.writeData(name, service, "; ".join(links))

parser = GoogleParser()
parser.run()