from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"})

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        base_domain = urlparse(url).netloc

        all_links = set()
        internal_links = set()
        external_links = set()
        broken_links = set()
        domains = set()

        # Extract links
        for tag in soup.find_all('a', href=True):
            full_link = urljoin(url, tag['href'])

            if not full_link.startswith("http"):
                continue

            all_links.add(full_link)

            link_domain = urlparse(full_link).netloc
            domains.add(link_domain)

            if base_domain in link_domain:
                internal_links.add(full_link)
            else:
                external_links.add(full_link)

        # Check broken links (limit to 10 for speed)
        for link in list(all_links)[:10]:
            try:
                res = requests.head(link, timeout=3)
                if res.status_code >= 400:
                    broken_links.add(link)
            except:
                broken_links.add(link)

        return jsonify({
            "total": len(all_links),
            "internal": len(internal_links),
            "external": len(external_links),
            "broken": len(broken_links),
            "domains": len(domains),
            "links": list(all_links)[:20],
            "broken_list": list(broken_links)
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)