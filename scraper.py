import requests
from bs4 import BeautifulSoup

def scrape_job_postings(url):
    """
    Scrape all job postings from the page.
    Returns a list of dicts: [{'title': ..., 'description': ..., 'email': ...}, ...]
    """
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    job_postings = []
    for job_div in soup.select(".job-posting"):
        title_tag = job_div.find("h2")
        desc_tag = job_div.find("p", class_="description")

        title = title_tag.get_text(strip=True) if title_tag else "No title"
        description = desc_tag.get_text(strip=True) if desc_tag else "No description"

        # Look for mailto links inside this job_div only
        email = None
        for a in job_div.find_all("a", href=True):
            href = a['href']
            if href.startswith("mailto:"):
                email = href.replace("mailto:", "")
                break

        job_postings.append({
            "title": title,
            "description": description,
            "email": email
        })

    return job_postings
