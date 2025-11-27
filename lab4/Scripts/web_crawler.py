"""
Web Crawler for Hong Kong Government Information
Focus: Bamboo scaffolding policies and fire incident handling
Domains: gov.hk, legco.gov.hk
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
import sys

# Add parent directory to path for api_key_loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# API configuration - using OpenRouter
def get_api_key():
    """Load API key from lab1/APIkey.txt"""
    api_file = os.path.join(os.path.dirname(__file__), '../../lab1/APIkey.txt')
    with open(api_file, 'r') as f:
        content = f.read()
        # Extract API key
        import re
        match = re.search(r'API key\s*=\s*(sk-[\w-]+)', content)
        if match:
            return match.group(1)
    raise ValueError("API key not found")

OPENROUTER_API_KEY = get_api_key()
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

class HKGovCrawler:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.visited_urls = set()
        self.search_queries = [
            "bamboo scaffolding policy",
            "bamboo scaffold phasing out",
            "fire safety scaffolding regulations",
            "building fire incidents",
            "scaffolding fire safety",
            "construction fire prevention"
        ]
        self.target_domains = ['gov.hk', 'legco.gov.hk']
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Results storage
        self.results = []
        
    def is_target_domain(self, url):
        """Check if URL is from target domains"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return any(target in domain for target in self.target_domains)
    
    def search_google(self, query):
        """Search Google for HK gov sites"""
        # Construct site-specific search query
        site_queries = []
        for domain in self.target_domains:
            site_queries.append(f'site:{domain} {query}')
        
        # For now, we'll use predefined URLs since Google Search API requires setup
        # In production, you'd use Google Custom Search API
        print(f"📝 Searching for: {query}")
        return self.get_known_urls(query)
    
    def get_known_urls(self, query):
        """Get known relevant URLs from HK government sites"""
        urls = []
        
        # Fire Services Department
        if 'fire' in query.lower() or 'safety' in query.lower():
            urls.extend([
                'https://www.hkfsd.gov.hk/eng/aboutus/firestat.html',
                'https://www.hkfsd.gov.hk/eng/education/fire.html',
                'https://www.bd.gov.hk/en/safety-inspection/fire-safety/index.html',
            ])
        
        # Buildings Department - scaffolding
        if 'scaffold' in query.lower():
            urls.extend([
                'https://www.bd.gov.hk/en/safety-inspection/index.html',
                'https://www.bd.gov.hk/en/resources/codes-and-references/code-and-design-manuals/index.html',
                'https://www.labour.gov.hk/eng/osh/content10.htm',
            ])
        
        # LegCo - policy discussions
        if 'policy' in query.lower():
            urls.extend([
                'https://www.legco.gov.hk/general/english/sec/silg/library_guide.htm',
            ])
        
        return urls
    
    def fetch_page(self, url):
        """Fetch webpage content"""
        try:
            print(f"🌐 Fetching: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def extract_text(self, html):
        """Extract main text content from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def generate_summary(self, text, url):
        """Generate summary using OpenRouter API (Gemini)"""
        try:
            print(f"🤖 Generating summary for {url}")
            
            prompt = f"""
            Analyze this webpage content from a Hong Kong government website and provide:
            
            1. A concise 2-3 sentence summary of the main content
            2. Key points related to fire safety, bamboo scaffolding, or building regulations (if any)
            3. Relevance to the Tai Po fire incident (bamboo scaffolding, fire safety policies)
            
            Content:
            {text[:4000]}  # Limit text length
            
            Format your response as:
            SUMMARY: [your summary]
            KEY POINTS: [bullet points]
            RELEVANCE: [how this relates to fire safety/scaffolding]
            """
            
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return "Summary generation failed."
    
    def save_page(self, url, html, text, summary, index):
        """Save page content as markdown"""
        filename = f"page_{index:03d}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create markdown content
        markdown = f"""# Webpage {index}: {url}

**URL:** {url}  
**Fetched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

---

## Summary

{summary}

---

## Original Content

{text[:10000]}  # Limit to first 10000 chars

{"..." if len(text) > 10000 else ""}

---

*Source: {url}*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"✅ Saved: {filename}")
        
        return {
            'index': index,
            'url': url,
            'filename': filename,
            'summary': summary[:200]  # Store short summary for index
        }
    
    def crawl(self):
        """Main crawling function"""
        print("🚀 Starting HK Government Web Crawler")
        print(f"📂 Output directory: {self.output_dir}")
        print("=" * 60)
        
        page_index = 1
        
        for query in self.search_queries:
            urls = self.search_google(query)
            
            for url in urls:
                # Skip if already visited
                if url in self.visited_urls:
                    continue
                
                # Skip if not target domain
                if not self.is_target_domain(url):
                    print(f"⏭️  Skipping (not target domain): {url}")
                    continue
                
                self.visited_urls.add(url)
                
                # Fetch page
                html = self.fetch_page(url)
                if not html:
                    continue
                
                # Extract text
                text = self.extract_text(html)
                
                # Generate summary
                summary = self.generate_summary(text, url)
                
                # Save page
                result = self.save_page(url, html, text, summary, page_index)
                self.results.append(result)
                
                page_index += 1
                
                # Be polite - wait between requests
                time.sleep(2)
                
                print("-" * 60)
        
        # Create index page
        self.create_index()
        
        print("=" * 60)
        print(f"✅ Crawling complete! Processed {len(self.results)} pages")
    
    def create_index(self):
        """Create index page with all results"""
        index_path = os.path.join(self.output_dir, "INDEX.md")
        
        content = f"""# Hong Kong Government Information - Fire Safety & Scaffolding

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Pages:** {len(self.results)}  

## Search Focus
- Bamboo scaffolding policies and phasing out plans
- Fire safety regulations for construction sites
- Previous fire incident handling
- Building renovation safety standards

## Context
This research was conducted in response to the tragic Tai Po fire on November 26, 2025, 
where bamboo scaffolding and highly flammable materials (styrofoam) contributed to rapid 
fire spread, resulting in 44 deaths.

---

## Collected Pages

"""
        
        for result in self.results:
            content += f"""
### {result['index']}. [{result['filename']}](./{result['filename']})

**URL:** {result['url']}

{result['summary']}...

---
"""
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📋 Index created: INDEX.md")


def main():
    output_dir = "/Users/simonwang/Documents/Usage/ai7010/lab4/inputData/newsWebpages"
    
    crawler = HKGovCrawler(output_dir)
    crawler.crawl()


if __name__ == "__main__":
    main()

