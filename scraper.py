import requests
from bs4 import BeautifulSoup

def scrape_job_posting(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    # Example: get job description from a div or p
    job_desc = soup.find("p", class_="description").text
    # Get email if available (or you can skip)
    email = None
    for a in soup.find_all("a", href=True):
        if "mailto:" in a['href']:
            email = a['href'].replace("mailto:", "")
            break
    return job_desc, email
