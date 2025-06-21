import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# r = requests.get('https://weather-broker-cdn.api.bbci.co.uk/en/forecast/aggregated/264371').json()

# wd = {}

# for forecast in r['forecasts']:
#     report = forecast['summary']['report']
#     desc = report['enhancedWeatherDescription']
#     local_date = report['localDate']
#     wd[local_date] = desc

# with open('f.txt','w') as f:
#     f.write(str(wd))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
r = requests.get('https://en.wikipedia.org/wiki/India')
parsed = BeautifulSoup(r.content)





# print(l)

@app.get('/')
async def index(country: str):
    if len(country.strip()) == 0:
        return "invalid", 500
    url = f'https://en.wikipedia.org/wiki/{country.capitalize()}'
    r = requests.get(url)
    parsed = BeautifulSoup(r.content)
    p = parsed.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    final = ""
    for element in p:
        level = int(element.name.replace('h',''))
        final+="#"*level + " " + element.text + "\n\n"
    return final.strip(), 200

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8000)