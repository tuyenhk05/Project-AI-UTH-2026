import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import socket
import whois
from datetime import datetime
import warnings
import urllib3
import os
import zipfile
import urllib.request
import threading

warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PhishingFeatureExtractor:
    top_domains = set()
    _lock = threading.Lock()

    @classmethod
    def load_top_domains(cls):
        if cls.top_domains: return
        with cls._lock:
            if cls.top_domains: return
            try:
                os.makedirs("data", exist_ok=True)
                top_sites_path = "data/top-1m.csv"
                if not os.path.exists(top_sites_path):
                    zip_url = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
                    zip_path = "data/top-1m.zip"
                    req = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=15) as response, open(zip_path, 'wb') as out_file:
                        out_file.write(response.read())
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall("data")
                    os.remove(zip_path)
                with open(top_sites_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            cls.top_domains.add(parts[1])
            except Exception:
                pass

    def __init__(self, url):
        self.load_top_domains()
        self.original_url = url
        if not url.startswith("http"):
            url = "http://" + url
        
        self.url = url
        self.domain = ""
        self.soup = None
        self.is_accessible = False
        self.redirected_url = url
        
        self.fetch_page_content()

    def fetch_page_content(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            # Cho phép redirect để lấy URL thật đằng sau bit.ly
            with requests.get(self.url, timeout=5, verify=False, headers=headers, allow_redirects=True) as res:
                self.redirected_url = res.url
                self.parsed_url = urlparse(self.redirected_url)
                self.domain = self.parsed_url.netloc.split(':')[0].replace("www.", "")
                
                if res.status_code == 200:
                    self.soup = BeautifulSoup(res.text, 'html.parser')
                    self.is_accessible = True
        except:
            self.is_accessible = False
            self.parsed_url = urlparse(self.url)
            self.domain = self.parsed_url.netloc.split(':')[0].replace("www.", "")

    # --- NHÓM TÍNH TOÁN KỸ THUẬT ---
    def having_ip_address(self):
        try:
            socket.inet_aton(self.domain)
            return -1
        except:
            return 1

    def url_length(self):
        l = len(self.redirected_url)
        return 1 if l < 54 else (0 if l <= 75 else -1)

    def shortening_service(self):
        # Kiểm tra cả URL ban đầu và URL sau redirect
        match = re.search(r'bit\.ly|tinyurl|goo\.gl|t\.co|rebrand\.ly|ow\.ly', self.original_url)
        return -1 if match else 1

    def having_at_symbol(self):
        return -1 if '@' in self.redirected_url else 1

    def double_slash_redirecting(self):
        return -1 if self.redirected_url.find('//', 8) != -1 else 1

    def prefix_suffix(self):
        return -1 if '-' in self.domain else 1

    def having_subdomain(self):
        parts = self.domain.split('.')
        if len(parts) <= 2: return 1
        elif len(parts) == 3: return 0
        return -1

    def ssl_state(self):
        if self.parsed_url.scheme != 'https': return -1
        return 1 if self.is_accessible else 0

    def domain_registration_length(self):
        try:
            w = whois.whois(self.domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list): creation_date = creation_date[0]
            
            age = (datetime.now() - creation_date).days
            return 1 if age > 365 else -1 # Trên 1 năm là an toàn
        except:
            return -1 # Không check được whois thường là domain rác/mới

    def request_url(self):
        if not self.soup: return -1 # Nếu ko truy cập được, khả năng cao là mờ ám
        imgs = self.soup.find_all('img', src=True)
        if not imgs: return 1
        ext = sum(1 for img in imgs if self.domain not in urlparse(urljoin(self.redirected_url, img['src'])).netloc)
        r = ext / len(imgs)
        return 1 if r < 0.22 else (0 if r <= 0.61 else -1)

    def url_of_anchor(self):
        if not self.soup: return -1
        links = self.soup.find_all('a', href=True)
        if not links: return 1
        ext = sum(1 for a in links if self.domain not in urlparse(urljoin(self.redirected_url, a['href'])).netloc)
        r = ext / len(links)
        return 1 if r < 0.31 else (0 if r <= 0.67 else -1)

    def web_traffic(self):
        # Kiểm tra xem tên miền có nằm trong danh sách TOP 1 Triệu Umbrella không.
        # Nếu có mặt thì là an toàn, ngược lại là rủi ro rác.
        if self.domain in self.top_domains:
            return 1
        return -1

    def google_index(self):
        try:
            url = f"https://www.google.com/search?q=site:{self.domain}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            res = requests.get(url, headers=headers, timeout=5)
            if "did not match any documents" in res.text or "không phù hợp với bất kỳ tài liệu nào" in res.text:
                return -1
            return 1
        except:
            return 0

    def links_in_tags(self):
        if not self.soup: return -1
        meta = self.soup.find_all('meta')
        script = self.soup.find_all('script', src=True)
        link = self.soup.find_all('link', href=True)
        
        total = len(meta) + len(script) + len(link)
        if total == 0: return 1
        
        ext = 0
        for tag in meta:
            content = tag.get('content', '')
            if 'http' in content and self.domain not in content:
                ext += 1
        for tag in script:
            if self.domain not in tag.get('src', ''):
               ext += 1
        for tag in link:
            if self.domain not in tag.get('href', ''):
               ext += 1
               
        r = ext / total
        return 1 if r < 0.17 else (0 if r <= 0.81 else -1)

    def extract_all_features(self):
        # Thứ tự phải khớp tuyệt đối với feature_order.pkl của bạn
        features = {
            'having_IP_Address': self.having_ip_address(),
            'URL_Length': self.url_length(),
            'Shortining_Service': self.shortening_service(),
            'having_At_Symbol': self.having_at_symbol(),
            'double_slash_redirecting': self.double_slash_redirecting(),
            'Prefix_Suffix': self.prefix_suffix(),
            'having_Sub_Domain': self.having_subdomain(),
            'SSLfinal_State': self.ssl_state(),
            'Domain_registeration_length': self.domain_registration_length(),
            'Request_URL': self.request_url(),
            'URL_of_Anchor': self.url_of_anchor(),
            'Links_in_tags': self.links_in_tags(),
            'SFH': 1 if self.is_accessible else -1,
            'web_traffic': self.web_traffic(),
            'Google_Index': self.google_index()
        }
        return features