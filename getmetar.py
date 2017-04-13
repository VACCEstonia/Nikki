from bs4 import BeautifulSoup
import urllib.request

def extract_metar(icao, info="metar"):
    if info == "":
        __info = "metar"
    else:
        __info = info.lower()
    if __info != "metar" and __info != "taf" and __info != "all":
        print("Sorry, wrong parameter specified")
        quit()

    if len(str(icao)) > 4:
        print("Sorry, " + icao + " is not correct ICAO airport code")
        quit()

    code = str(icao)
    metar_url = 'https://www.aviationweather.gov/metar/data?ids='
    metar_url_params = '&format=raw&date=0&hours=0&taf=on'
    try:
        page = urllib.request.urlopen(metar_url + code + metar_url_params).read()
    except urllib.error.URLError:
        return None
    soup = BeautifulSoup(page, "html.parser")

    if __info == "metar" or __info == "all":
        texts = soup.findAll(text=True)
        METAR = None
        for item in texts:
            if item.strip().find(code) == 0:
                METAR = item.strip()
                break
        if __info == "metar":
            if METAR is None:
                return None
            else:
                METAR = METAR.replace("\r", "")
                METAR = METAR.replace("\n", "")
                return METAR

    if __info == "taf" or __info == "all":
        try:
            TAF = soup.body.code.get_text()
            TAFc = ""
            flag_160 = False
            for i in TAF:
                if ord(i) != 160:
                    TAFc += i
                    flag_160 = False
                else:
                    if flag_160 == False:
                        TAFc += "\n\t"
                        flag_160 = True
                    else:
                        pass
        except AttributeError:
            return None
        if __info == "taf":
            return TAFc

    if __info == "all":
        if METAR is None:
            return "No METAR info \n" + TAFc
        else:
            return METAR + "\n" + TAFc


if __name__ == "__main__":
    print(extract_metar("UKDD", "metar"))
