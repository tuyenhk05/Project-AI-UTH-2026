import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import whois
from datetime import datetime
import socket
import warnings

warnings.filterwarnings('ignore')


class PhishingFeatureExtractor:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc.replace("www.", "")
        self.html_content = None
        self.soup = None
        self.fetch_page_content()

    def fetch_page_content(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(self.url, timeout=5, verify=False, headers=headers)
            if res.status_code == 200:
                self.html_content = res.text
                self.soup = BeautifulSoup(self.html_content, 'html.parser')
        except:
            self.soup = None

    # ================= FEATURE =================

    def having_ip_address(self):
        try:
            socket.inet_aton(self.domain)
            return -1
        except:
            return 1

    def url_length(self):
        l = len(self.url)
        if l < 54:
            return 1
        elif l <= 75:
            return 0
        return -1

    def shortening_service(self):
        return -1 if re.search(r'bit\.ly|tinyurl|goo\.gl|t\.co', self.url) else 1

    def having_at_symbol(self):
        return -1 if '@' in self.url else 1

    def double_slash_redirecting(self):
        return -1 if self.url.find('//', 8) != -1 else 1

    def prefix_suffix(self):
        return -1 if '-' in self.domain else 1

    def having_subdomain(self):
        parts = self.domain.split('.')
        if len(parts) <= 2:
            return 1
        elif len(parts) == 3:
            return 0
        return -1

    def ssl_state(self):
        return 1 if self.parsed_url.scheme == 'https' else -1

    def domain_registration_length(self):
        try:
            w = whois.whois(self.domain)
            if not w or not w.creation_date:
                return 0
            creation = w.creation_date
            if isinstance(creation, list):
                creation = creation[0]
            age = (datetime.now() - creation).days
            return 1 if age > 365 else -1
        except:
            return 0

    def request_url(self):
        if not self.soup:
            return 0
        imgs = self.soup.find_all('img', src=True)
        if not imgs:
            return 1
        ext = sum(
            1 for img in imgs
            if urlparse(urljoin(self.url, img['src'])).netloc != self.domain
        )
        r = ext / len(imgs)
        if r < 0.3:
            return 1
        elif r <= 0.7:
            return 0
        return -1

    def url_of_anchor(self):
        if not self.soup:
            return 0
        links = self.soup.find_all('a', href=True)
        if not links:
            return 1
        ext = sum(
            1 for a in links
            if urlparse(urljoin(self.url, a['href'])).netloc != self.domain
        )
        r = ext / len(links)
        if r < 0.3:
            return 1
        elif r <= 0.7:
            return 0
        return -1

    def links_in_tags(self):
        if not self.soup:
            return 0
        total, ext = 0, 0
        for tag in ['meta', 'script', 'link']:
            for e in self.soup.find_all(tag):
                attr = e.get('src') or e.get('href')
                if attr:
                    total += 1
                    if urlparse(urljoin(self.url, attr)).netloc != self.domain:
                        ext += 1
        if total == 0:
            return 1
        r = ext / total
        if r < 0.3:
            return 1
        elif r <= 0.7:
            return 0
        return -1

    def sfh(self):
        if not self.soup:
            return 0
        forms = self.soup.find_all('form')
        if not forms:
            return 1
        for f in forms:
            action = f.get('action', '')
            if action in ['', '#'] or action.lower().startswith('javascript'):
                return -1
        return 1

    def web_traffic(self):
        try:
            if len(self.domain) < 10:
                return 1
            elif len(self.domain) < 20:
                return 0
            return -1
        except:
            return 0

    def google_index(self):
        return 0

    # ================= FINAL =================
    def extract_all_features(self):
        return [
            self.having_ip_address(),
            self.url_length(),
            self.shortening_service(),
            self.having_at_symbol(),
            self.double_slash_redirecting(),
            self.prefix_suffix(),
            self.having_subdomain(),
            self.ssl_state(),
            self.domain_registration_length(),
            self.request_url(),
            self.url_of_anchor(),
            self.links_in_tags(),
            self.sfh(),
            self.web_traffic(),
            self.google_index()
        ]