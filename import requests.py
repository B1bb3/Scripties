import requests
from bs4 import BeautifulSoup

# Get user input
name = input("Name: ")
name = name.replace(" ", "%20")

# Construct URL
url = f'https://map.krak.dk/?c=56.535373,10.040998&z=14&q="{name}"'

# Send a request to the URL
response = requests.get(url)

# Parse the page with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the information using the appropriate tag or class
info = soup.select_one('body > div:nth-child(3) > div:nth-child(5) > div:nth-child(2) > ul > li > div > div:nth-child(4) > ul:nth-child(2) > li > p')

if info:
    print(info.text)
else:
    print("Information not found!")

# Optional: sleep to keep the program running
import time
time.sleep(600)
