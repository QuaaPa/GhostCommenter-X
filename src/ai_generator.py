"""AI comment generation module"""

import random
import time
from typing import Dict, Optional

try:
    import g4f
    G4F_AVAILABLE = True
except ImportError:
    G4F_AVAILABLE = False

from text_utils import humanize_text, validate_comment_length, is_sentence_complete, complete_sentence

def generate_ai_comment_g4f(title: str, content: str, prompts: Dict[str, str], 
                            retry_count: int = 3, log_func=None) -> Optional[str]:
    """Generate comment using G4F (Free GPT-4)"""
    if not G4F_AVAILABLE:
        if log_func:
            log_func("G4F not installed, falling back to template")
        return None
    
    comment_prompt = prompts['comment'].replace('{title}', title).replace('{content}', content[:1000])
    
    for attempt in range(retry_count):
        try:
            if log_func:
                log_func(f"Generating with G4F (attempt {attempt + 1}/{retry_count})...")
            
            response = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": comment_prompt}],
                timeout=45
            )
            
            if response and len(response.strip()) > 10:
                comment = response.strip()
                comment = humanize_text(comment)
                
                # Check if sentence is complete before validation
                if not is_sentence_complete(comment):
                    if log_func:
                        log_func(f"⚠ Incomplete sentence detected, completing...")
                    comment = complete_sentence(comment)
                
                comment = validate_comment_length(comment)
                
                # Final check
                if is_sentence_complete(comment):
                    if log_func:
                        log_func(f"✓ SUCCESS! Comment ({len(comment)} chars): {comment[:50]}...")
                    return comment
                else:
                    if log_func:
                        log_func(f"✗ Comment still incomplete after processing, retrying...")
                    continue
            else:
                if log_func:
                    log_func(f"✗ G4F returned empty/short response")
        
        except Exception as e:
            error_msg = str(e)[:100]
            if log_func:
                log_func(f"✗ G4F attempt {attempt + 1} failed: {error_msg}")
            
            if attempt == retry_count - 1:
                try:
                    if log_func:
                        log_func("Trying alternative G4F method...")
                    
                    response = g4f.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": comment_prompt}]
                    )
                    
                    if response and len(response.strip()) > 10:
                        comment = response.strip()
                        comment = humanize_text(comment)
                        comment = validate_comment_length(comment)
                        
                        if log_func:
                            log_func(f"✓ SUCCESS via alternative method!")
                        return comment
                except:
                    pass
        
        if attempt < retry_count - 1:
            wait_time = random.uniform(2, 5)
            if log_func:
                log_func(f"Retrying in {wait_time:.1f} seconds...")
            time.sleep(wait_time)
    
    if log_func:
        log_func("All G4F attempts exhausted")
    return None


def generate_ai_comment_openai(title: str, content: str, api_key: str, 
                               prompts: Dict[str, str], log_func=None) -> Optional[str]:
    """Generate comment using OpenAI API"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        comment_prompt = prompts['comment'].replace('{title}', title).replace('{content}', content[:1000])
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": comment_prompt}],
            temperature=0.9,
            max_tokens=150
        )
        
        comment = response.choices[0].message.content.strip()
        comment = humanize_text(comment)
        
        # Check completeness
        if not is_sentence_complete(comment):
            if log_func:
                log_func("⚠ Completing incomplete sentence...")
            comment = complete_sentence(comment)
        
        comment = validate_comment_length(comment)
        
        # Verify final result
        if not is_sentence_complete(comment):
            if log_func:
                log_func("⚠ Warning: Comment may be incomplete")
        
        return comment
    
    except Exception as e:
        if log_func:
            log_func(f"OpenAI generation error: {e}")
        return None


def generate_ai_comment(title: str, content: str, api_key: str, prompts: Dict[str, str], 
                       provider: str = 'g4f', log_func=None) -> Optional[str]:
    """Generate AI comment using specified provider"""
    if provider == 'g4f':
        return generate_ai_comment_g4f(title, content, prompts, retry_count=3, log_func=log_func)
    elif provider == 'openai':
        return generate_ai_comment_openai(title, content, api_key, prompts, log_func=log_func)
    else:
        return None