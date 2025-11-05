"""Configuration management for GhostCommenter-X"""

import os
from typing import Dict
from dotenv import load_dotenv


class ConfigManager:
    """Manages application configuration and credentials"""
    
    def __init__(self):
        load_dotenv('config/.env')
        load_dotenv('.env')  # Fallback to root .env
    
    def load_api_key(self, filename: str = "OpenAI_API_Key.txt") -> str:
        """Load OpenAI API key from file or environment"""
        api_key = os.getenv("OPENAI_API_KEY", "")
        
        if not api_key and os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            api_key = line
                            break
            except Exception as e:
                print(f"Error reading API key file: {e}")
        
        return api_key
    
    def load_saved_credentials(self) -> Dict[str, str]:
        """Load saved login credentials from environment"""
        credentials = {}
        
        for key, value in os.environ.items():
            if key.startswith("LOGIN_USER_"):
                num = key.replace("LOGIN_USER_", "")
                username = value
                password = os.getenv(f"LOGIN_PASS_{num}", "")
                if username and password:
                    credentials[username] = password
        
        return credentials
    
    def load_prompts(self, filename: str = "config/prompts.txt") -> Dict[str, str]:
        """Load AI prompts from configuration file"""
        prompts = {'title': '', 'content': '', 'comment': ''}
        
        if not os.path.exists(filename):
            self._create_default_prompts(filename)
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '[TITLE_PROMPT]' in content:
                title_section = content.split('[TITLE_PROMPT]')[1]
                if '[CONTENT_PROMPT]' in title_section:
                    prompts['title'] = title_section.split('[CONTENT_PROMPT]')[0].strip()
            
            if '[CONTENT_PROMPT]' in content:
                content_section = content.split('[CONTENT_PROMPT]')[1]
                if '[COMMENT_PROMPT]' in content_section:
                    prompts['content'] = content_section.split('[COMMENT_PROMPT]')[0].strip()
            
            if '[COMMENT_PROMPT]' in content:
                prompts['comment'] = content.split('[COMMENT_PROMPT]')[1].strip()
            
            print("AI prompts loaded successfully")
        except Exception as e:
            print(f"Error loading prompts: {e}")
        
        return prompts
    
    def _create_default_prompts(self, filename: str):
        """Create default prompt configuration file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        default_prompts = """[TITLE_PROMPT]
Generate a short forum thread title about: {topic}
Write like a regular person, not a journalist:
- 60-100 characters
- No exclamation marks or quotes
- Can include typos or slang
- Sounds casual and relaxed
- WRITE IN RUSSIAN ONLY
Examples: "кто шарит в этой теме", "короче наткнулся на одну штуку"
Just the title, nothing extra.

[CONTENT_PROMPT]
You are a regular forum user, not an expert or journalist. Write a simple post about: {topic}
HOW TO WRITE:
- First person ("I", "me", "my")
- Short simple sentences
- Conversational style, like messaging
- Can have minor errors (missing commas, lowercase)
- Use words: "короче", "вообще", "кстати", "блин", "в общем", "ну", "типа"
- DO NOT use numbered lists at all
STRUCTURE:
- 1 short paragraph
- 60-100 letters maximum
- Write like casual forum chat without punctuation and commas
- Start with personal experience or just a thought
- Write as you think, don't structure
- WRITE IN RUSSIAN ONLY
- SENTENCE MUST BE COMPLETE

[COMMENT_PROMPT]
Read the forum post and write a natural comment.
Post title: {title}
Post text: {content}

CRITICALLY IMPORTANT:
- Length: STRICTLY 20 to 100 CHARACTERS (not words!)
- Write WITHOUT ALL punctuation - no periods no commas no exclamations no questions no dashes NOTHING AT ALL
- Write like quick messaging in messenger one stream of thoughts
- Style: very natural conversational like typing fast on phone
- Use words: вобще короче щас кстати блин ну типа чето
- SENTENCE MUST BE COMPLETE

Examples of CORRECT style (20-100 characters):
"да у меня так же было недавно интересно"
"вобще годная тема надо попробовать"
"согласен кстати у меня похоже"
"интересно а ты долго с этим парился"
"ну вот у меня было так же только дольше"

IMPORTANT: write exactly like this without a single punctuation mark and 20-60 characters long WRITE IN RUSSIAN ONLY
Write only the comment itself without greetings and signature
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(default_prompts)
        
        print(f"Created default prompts file: {filename}")
    
    def save_prompts(self, prompts: Dict[str, str], filename: str = "config/prompts.txt"):
        """Save prompts to configuration file"""
        content = f"""[TITLE_PROMPT]
{prompts.get('title', '')}

[CONTENT_PROMPT]
{prompts.get('content', '')}

[COMMENT_PROMPT]
{prompts.get('comment', '')}
"""
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Prompts saved successfully")