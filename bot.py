import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

class HackerNewsIntel:
    """Hacker News monitoring and intelligence bot"""
    
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.keywords = os.getenv("KEYWORDS", "startup,SaaS,AI,machine learning").split(",")
        self.min_score = int(os.getenv("MIN_SCORE", "10"))
        self.webhook_url = os.getenv("WEBHOOK_URL")
        self.max_age_hours = int(os.getenv("MAX_AGE_HOURS", "24"))
        
    def get_top_stories(self, limit: int = 100) -> List[int]:
        """Get top story IDs from HN"""
        response = requests.get(f"{self.base_url}/topstories.json")
        response.raise_for_status()
        return response.json()[:limit]
    
    def get_new_stories(self, limit: int = 100) -> List[int]:
        """Get new story IDs from HN"""
        response = requests.get(f"{self.base_url}/newstories.json")
        response.raise_for_status()
        return response.json()[:limit]
    
    def get_story(self, story_id: int) -> Optional[Dict]:
        """Get story details by ID"""
        response = requests.get(f"{self.base_url}/item/{story_id}.json")
        response.raise_for_status()
        return response.json()
    
    def matches_keywords(self, text: str) -> List[str]:
        """Check if text matches any keyword"""
        if not text:
            return []
        text_lower = text.lower()
        matches = []
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                matches.append(keyword)
        return matches
    
    def is_recent(self, timestamp: int) -> bool:
        """Check if story is within max_age_hours"""
        story_time = datetime.fromtimestamp(timestamp)
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        return story_time >= cutoff_time
    
    def analyze_story(self, story: Dict) -> Optional[Dict]:
        """Analyze a story for relevance"""
        if not story or story.get("type") != "story":
            return None
            
        # Check score threshold
        score = story.get("score", 0)
        if score < self.min_score:
            return None
        
        # Check age
        timestamp = story.get("time", 0)
        if not self.is_recent(timestamp):
            return None
        
        # Check keywords in title and text
        title = story.get("title", "")
        text = story.get("text", "")
        content = f"{title} {text}"
        
        matches = self.matches_keywords(content)
        if not matches:
            return None
        
        return {
            "id": story.get("id"),
            "title": title,
            "url": story.get("url", f"https://news.ycombinator.com/item?id={story.get('id')}"),
            "score": score,
            "comments": story.get("descendants", 0),
            "author": story.get("by"),
            "time": datetime.fromtimestamp(timestamp).isoformat(),
            "matched_keywords": matches,
            "hn_url": f"https://news.ycombinator.com/item?id={story.get('id')}"
        }
    
    def scan_stories(self) -> List[Dict]:
        """Scan HN for relevant stories"""
        print(f"🔍 Scanning Hacker News for keywords: {self.keywords}")
        
        # Get both top and new stories
        story_ids = set()
        story_ids.update(self.get_top_stories(100))
        story_ids.update(self.get_new_stories(100))
        
        print(f"📊 Found {len(story_ids)} unique stories to analyze")
        
        relevant_stories = []
        for story_id in story_ids:
            try:
                story = self.get_story(story_id)
                analysis = self.analyze_story(story)
                if analysis:
                    relevant_stories.append(analysis)
                    print(f"✅ Match found: {analysis['title'][:60]}...")
            except Exception as e:
                print(f"⚠️ Error fetching story {story_id}: {e}")
                continue
        
        # Sort by score (descending)
        relevant_stories.sort(key=lambda x: x["score"], reverse=True)
        return relevant_stories
    
    def send_notification(self, stories: List[Dict]):
        """Send notification via webhook"""
        if not self.webhook_url or not stories:
            return
        
        payload = {
            "source": "hacker-news-intel",
            "timestamp": datetime.now().isoformat(),
            "total_matches": len(stories),
            "stories": stories
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            print(f"📤 Notification sent successfully")
        except Exception as e:
            print(f"❌ Failed to send notification: {e}")
    
    def generate_report(self, stories: List[Dict]) -> str:
        """Generate markdown report"""
        if not stories:
            return "# Hacker News Intelligence Report\n\nNo relevant stories found.\n"
        
        report = ["# 🚀 Hacker News Intelligence Report\n"]
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Keywords:** {', '.join(self.keywords)}\n")
        report.append(f"**Matches Found:** {len(stories)}\n")
        report.append("---\n")
        
        for i, story in enumerate(stories, 1):
            report.append(f"\n### {i}. {story['title']}\n")
            report.append(f"- **Score:** ⬆️ {story['score']} | **Comments:** 💬 {story['comments']}\n")
            report.append(f"- **Author:** @{story['author']}\n")
            report.append(f"- **Time:** {story['time']}\n")
            report.append(f"- **Matched Keywords:** {', '.join(story['matched_keywords'])}\n")
            report.append(f"- **HN Link:** {story['hn_url']}\n")
            if story['url'] != story['hn_url']:
                report.append(f"- **External Link:** {story['url']}\n")
            report.append("\n")
        
        return "".join(report)
    
    def run(self):
        """Main execution"""
        print("🚀 Starting Hacker News Intelligence Bot")
        print(f"⏰ Max age: {self.max_age_hours} hours")
        print(f"📊 Min score: {self.min_score}")
        
        stories = self.scan_stories()
        
        print(f"\n🎯 Found {len(stories)} relevant stories")
        
        # Generate and save report
        report = self.generate_report(stories)
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("📝 Report saved to report.md")
        
        # Save JSON data
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "stories": stories
            }, f, indent=2)
        print("💾 Data saved to data.json")
        
        # Send notification if configured
        if self.webhook_url:
            self.send_notification(stories)
        
        print("✅ Done!")
        return stories

if __name__ == "__main__":
    bot = HackerNewsIntel()
    bot.run()
