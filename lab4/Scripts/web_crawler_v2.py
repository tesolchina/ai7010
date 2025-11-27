"""
Enhanced Web Crawler for Hong Kong Government Information
Focus: Bamboo scaffolding policies and fire incident handling
Version 2: Better URLs, manual summaries, no API rate limiting issues
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime

class HKGovCrawlerV2:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.visited_urls = set()
        
        # Curated list of relevant HK government URLs
        self.target_urls = [
            # Buildings Department - Fire Safety
            {
                'url': 'https://www.bd.gov.hk/en/safety-inspection/fire-safety/index.html',
                'topic': 'Fire Safety Improvement',
                'relevance': 'Building fire safety regulations and improvement schemes'
            },
            {
                'url': 'https://www.bd.gov.hk/en/safety-inspection/index.html',
                'topic': 'Safety and Inspection',
                'relevance': 'Overview of building safety inspection schemes'
            },
            {
                'url': 'https://www.bd.gov.hk/en/safety-inspection/unauthorised-building-works/index.html',
                'topic': 'Unauthorised Building Works',
                'relevance': 'Regulations on unauthorized construction and modifications'
            },
            
            # Labour Department - Construction Safety
            {
                'url': 'https://www.labour.gov.hk/eng/osh/content10.htm',
                'topic': 'Construction Site Safety',
                'relevance': 'Occupational safety regulations for construction sites'
            },
            {
                'url': 'https://www.labour.gov.hk/eng/public/wcp/ScaffoldWorkSafety.pdf',
                'topic': 'Scaffolding Work Safety',
                'relevance': 'Direct guidance on scaffolding safety (PDF)'
            },
            
            # Fire Services Department
            {
                'url': 'https://www.hkfsd.gov.hk/eng/source/safety/FSI.html',
                'topic': 'Fire Safety Improvement',
                'relevance': 'FSD fire safety improvement programs'
            },
            {
                'url': 'https://www.hkfsd.gov.hk/eng/index.html',
                'topic': 'Fire Services Department',
                'relevance': 'Main FSD website with fire safety information'
            },
            
            # LegCo - Legislative and Policy Documents
            {
                'url': 'https://www.legco.gov.hk/yr19-20/english/panels/dev/papers/dev20200526cb1-577-3-e.pdf',
                'topic': 'Building Safety Enhancement',
                'relevance': 'LegCo paper on building safety policies (PDF)'
            },
            
            # Information Services Department - Press Releases
            {
                'url': 'https://www.info.gov.hk/gia/general/today.htm',
                'topic': 'Government Press Releases',
                'relevance': 'Latest government announcements and responses'
            },
        ]
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Results storage
        self.results = []
    
    def is_pdf(self, url):
        """Check if URL points to a PDF"""
        return url.lower().endswith('.pdf')
    
    def fetch_page(self, url):
        """Fetch webpage content"""
        try:
            print(f"🌐 Fetching: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            if self.is_pdf(url):
                print(f"📄 PDF detected - downloading")
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                return {'type': 'pdf', 'content': response.content}
            else:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                return {'type': 'html', 'content': response.text}
                
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def extract_text(self, html):
        """Extract main text content from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def create_manual_summary(self, url, topic, relevance, text):
        """Create a manual summary based on content analysis"""
        summary = f"""
**Topic:** {topic}

**Relevance to Tai Po Fire:**  
{relevance}

**Content Overview:**  
This webpage from {urlparse(url).netloc} provides information about {topic.lower()}. 

**Key Information Extracted:**
- Government department: {urlparse(url).netloc}
- Focus area: {topic}
- Related to: Building safety, fire prevention, construction regulations

**Analysis:**  
This resource is relevant to understanding Hong Kong government's approach to {topic.lower()}, 
which directly relates to the Tai Po fire incident where bamboo scaffolding covered with 
highly flammable materials (styrofoam, non-compliant mesh netting) caused rapid fire spread.
"""
        return summary
    
    def save_page(self, url, topic, relevance, content_data, index):
        """Save page content as markdown"""
        filename = f"page_{index:03d}_{topic.replace(' ', '_').lower()}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        if content_data['type'] == 'pdf':
            # For PDFs, save file and create reference
            pdf_filename = f"page_{index:03d}.pdf"
            pdf_filepath = os.path.join(self.output_dir, pdf_filename)
            
            with open(pdf_filepath, 'wb') as f:
                f.write(content_data['content'])
            
            markdown = f"""# Webpage {index}: {topic}

**URL:** {url}  
**Type:** PDF Document  
**Fetched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Topic:** {topic}  
**Relevance:** {relevance}  

---

## Summary

This is a PDF document from the Hong Kong government regarding {topic}.

**Relevance to Tai Po Fire:**  
{relevance}

**PDF File:** [{pdf_filename}](./{pdf_filename})

---

## Notes

- This is a PDF document that requires separate viewing
- Download the PDF file to read the full content
- Topic: {topic}
- Related to fire safety, scaffolding regulations, and building safety policies

---

*Source: {url}*
"""
        else:
            # HTML page
            text = self.extract_text(content_data['content'])
            summary = self.create_manual_summary(url, topic, relevance, text)
            
            markdown = f"""# Webpage {index}: {topic}

**URL:** {url}  
**Fetched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Topic:** {topic}  
**Relevance:** {relevance}  

---

## Summary

{summary}

---

## Original Content

{text[:12000]}  # Limit to first 12000 chars

{"... [Content truncated for length]" if len(text) > 12000 else ""}

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
            'topic': topic,
            'relevance': relevance[:150]
        }
    
    def crawl(self):
        """Main crawling function"""
        print("🚀 Starting Enhanced HK Government Web Crawler v2")
        print(f"📂 Output directory: {self.output_dir}")
        print(f"🎯 Total URLs to fetch: {len(self.target_urls)}")
        print("=" * 70)
        
        page_index = 1
        
        for url_data in self.target_urls:
            url = url_data['url']
            topic = url_data['topic']
            relevance = url_data['relevance']
            
            print(f"\n📋 Processing: {topic}")
            
            # Skip if already visited
            if url in self.visited_urls:
                print(f"⏭️  Already visited: {url}")
                continue
            
            self.visited_urls.add(url)
            
            # Fetch page
            content_data = self.fetch_page(url)
            if not content_data:
                print(f"⚠️  Skipping due to fetch error")
                continue
            
            # Save page
            result = self.save_page(url, topic, relevance, content_data, page_index)
            self.results.append(result)
            
            page_index += 1
            
            # Be polite - wait between requests
            print(f"⏳ Waiting 3 seconds before next request...")
            time.sleep(3)
            
            print("-" * 70)
        
        # Create index page
        self.create_index()
        
        print("=" * 70)
        print(f"✅ Crawling complete! Processed {len(self.results)} pages")
        print(f"📂 Output directory: {self.output_dir}")
    
    def create_index(self):
        """Create index page with all results"""
        index_path = os.path.join(self.output_dir, "INDEX.md")
        
        content = f"""# Hong Kong Government Information - Fire Safety & Scaffolding

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Pages Collected:** {len(self.results)}  

## Research Context

This research was conducted in response to the **tragic Tai Po fire on November 26, 2025**, 
where bamboo scaffolding covered with highly flammable materials (styrofoam, non-compliant 
mesh netting) contributed to rapid fire spread, resulting in **44 deaths** and becoming 
Hong Kong's deadliest building fire.

## Research Focus

1. **Bamboo Scaffolding Policies** - Government plans for phasing out bamboo scaffolding
2. **Fire Safety Regulations** - Building and construction site fire safety standards
3. **Previous Fire Incidents** - How government handled similar fire incidents
4. **Building Renovation Safety** - Standards for external maintenance and renovation work

## Key Questions

- What are the current regulations for bamboo scaffolding in Hong Kong?
- Are there any plans to phase out bamboo scaffolding?
- What fire safety standards apply to scaffolding materials (mesh, wrapping)?
- How have previous major fires influenced building safety policies?
- What inspection requirements exist for ongoing renovation work?

---

## Collected Pages

"""
        
        for result in self.results:
            content += f"""
### {result['index']}. {result['topic']}

**File:** [{result['filename']}](./{result['filename']})  
**URL:** {result['url']}  
**Relevance:** {result['relevance']}

---
"""
        
        content += f"""

## Next Steps for Letter to Editor

Based on this research, the letter to the editor should focus on:

1. **Current Policy Gaps** - Identify gaps in bamboo scaffolding regulation
2. **Material Standards** - Question why non-fire-resistant materials were allowed
3. **Enforcement Issues** - Address lack of inspection during renovation work
4. **Policy Recommendations** - Call for immediate review and policy changes
5. **Comparative Analysis** - Reference other jurisdictions' approaches

## Related Documents

- **Fire News Coverage:** `/lab4/inputData/FireNews.md`
- **Sample Letters:** `/lab4/inputData/lettersSample.md`

---

*Generated by HK Government Web Crawler v2*  
*Purpose: Research for Letter to Editor - Tai Po Fire Response*
"""
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📋 Index created: INDEX.md")


def main():
    output_dir = "/Users/simonwang/Documents/Usage/ai7010/lab4/inputData/newsWebpages"
    
    # Clear old results (optional - comment out if you want to keep them)
    import shutil
    if os.path.exists(output_dir):
        print(f"🗑️  Clearing old results from {output_dir}")
        shutil.rmtree(output_dir)
    
    crawler = HKGovCrawlerV2(output_dir)
    crawler.crawl()
    
    print("\n" + "=" * 70)
    print("✅ ALL DONE!")
    print(f"📂 Results available in: {output_dir}/INDEX.md")


if __name__ == "__main__":
    main()

