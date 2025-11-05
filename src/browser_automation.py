"""Browser automation for forum posting"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, Set
from patchright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from ai_generator import generate_ai_comment
from text_utils import generate_random_comment


def wait_cloudflare(page, log_func=None):
    """Wait for Cloudflare verification to complete"""
    try:
        if page.locator("text=Just a moment").count() > 0 or \
           page.locator("text=Checking your browser").count() > 0:
            if log_func:
                log_func("Cloudflare detected, waiting for verification...")
            page.wait_for_load_state("networkidle", timeout=60000)
            if log_func:
                log_func("Cloudflare check passed.")
    except:
        pass


def run_commenter_script(login: str, password: str, min_time: int, max_time: int, 
                         use_ai: bool, api_key: str, prompts: Dict[str, str], 
                         mode: str, max_comments: int, ai_provider: str = 'g4f', 
                         headless: bool = False, log_func=None, 
                         commented_threads: Set[str] = None):
    """Main automation script for posting comments"""
    
    if commented_threads is None:
        commented_threads = set()
    
    LOGIN_URL = "https://enjoyrc.io/login/"
    NEW_POSTS_URL = "https://enjoyrc.io/whats-new/posts/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            if log_func:
                log_func("Opening login page...")
            
            page.goto(LOGIN_URL, timeout=30000)
            wait_cloudflare(page, log_func)
            
            page.get_by_label("Имя пользователя или email").fill(login)
            page.get_by_label("Пароль").fill(password)
            
            try:
                page.click('button[type="submit"]', timeout=5000)
            except PlaywrightTimeoutError:
                page.get_by_role("button", name="Войти").click()
            
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            wait_cloudflare(page, log_func)
            
            if page.locator("text=Неверный").count() > 0 or page.locator("text=ошибка").count() > 0:
                if log_func:
                    log_func("Login failed - check credentials or CAPTCHA/2FA.")
                return False
            else:
                if log_func:
                    log_func("Login successful.")
                    log_func(f"Time interval: {min_time}-{max_time} seconds")
                    if use_ai:
                        provider_name = "G4F (Free)" if ai_provider == 'g4f' else "OpenAI API"
                        log_func(f"Content mode: AI Generated ({provider_name})")
                    else:
                        log_func(f"Content mode: Template")
                    log_func(f"Comment length: 20-60 characters")
                    if mode == "infinite":
                        log_func(f"Mode: INFINITE (until manual stop)")
                    else:
                        log_func(f"Mode: Limited to {max_comments} comments")
            
            comments_made = 0
            consecutive_failures = 0
            max_consecutive_failures = 5
            
            while True:
                if mode == "limited" and comments_made >= max_comments:
                    if log_func:
                        log_func(f"Limit reached! Total comments: {comments_made}")
                    break
                
                if log_func:
                    log_func("Loading new posts page...")
                
                page.goto(NEW_POSTS_URL, timeout=30000)
                wait_cloudflare(page, log_func)
                time.sleep(random.uniform(2, 4))
                
                try:
                    page.wait_for_selector('.structItem', timeout=10000)
                    posts = page.query_selector_all('.structItem')
                    
                    if not posts or len(posts) == 0:
                        if log_func:
                            log_func("No posts found on page, waiting...")
                        time.sleep(30)
                        continue
                    
                    if log_func:
                        log_func(f"Found {len(posts)} posts on page")
                    
                    post_index = random.randint(0, min(4, len(posts) - 1))
                    selected_post = posts[post_index]
                    
                    post_links = selected_post.query_selector_all('a[href*="/threads/"]')
                    if not post_links:
                        if log_func:
                            log_func("Could not find post link, trying next iteration...")
                        time.sleep(10)
                        continue
                    
                    post_link = post_links[0]
                    post_url = post_link.get_attribute('href')
                    
                    title_elem = selected_post.query_selector('.structItem-title')
                    if title_elem:
                        post_title = title_elem.inner_text().strip()
                    else:
                        post_title = "Unknown title"
                    
                    if post_url.startswith('/'):
                        post_url = f"https://enjoyrc.io{post_url}"
                    
                    clean_url = post_url.replace('/unread', '').rstrip('/')
                    
                    if clean_url in commented_threads:
                        if log_func:
                            log_func(f"Post already commented, skipping: {post_title[:50]}")
                        time.sleep(10)
                        continue
                    
                    if log_func:
                        log_func(f"Selected post: {post_title[:60]}...")
                    
                    page.goto(post_url, timeout=30000)
                    wait_cloudflare(page, log_func)
                    time.sleep(random.uniform(2, 4))
                    
                    try:
                        page.wait_for_selector('.message-body', timeout=10000)
                        
                        first_post = page.query_selector('.message-body')
                        if not first_post:
                            if log_func:
                                log_func("Could not find post content!")
                            continue
                        
                        post_content = first_post.inner_text()[:1500]
                        
                        if log_func:
                            log_func(f"Post content parsed: {len(post_content)} characters")
                        
                        if use_ai:
                            if log_func:
                                log_func(f"Generating AI comment...")
                            
                            comment_text = generate_ai_comment(
                                post_title, post_content, api_key, prompts, 
                                ai_provider, log_func
                            )
                            
                            if not comment_text:
                                if log_func:
                                    log_func("⚠ AI generation failed, using template fallback...")
                                comment_text = generate_random_comment(post_title, post_content)
                                consecutive_failures += 1
                            else:
                                if log_func:
                                    log_func(f"✓ AI comment generated! Length: {len(comment_text)} chars")
                                consecutive_failures = 0
                        else:
                            if log_func:
                                log_func("Generating template comment...")
                            comment_text = generate_random_comment(post_title, post_content)
                        
                        if log_func:
                            log_func(f"Final comment ({len(comment_text)} chars): {comment_text}")
                        
                        if consecutive_failures >= max_consecutive_failures:
                            if log_func:
                                log_func(f"⚠ Too many AI failures ({consecutive_failures}), taking longer break...")
                            time.sleep(60)
                            consecutive_failures = 0
                        
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(random.uniform(1, 2))
                        
                        page.wait_for_selector("div[contenteditable='true']", timeout=10000)
                        
                        editors = page.query_selector_all("div[contenteditable='true']")
                        if not editors:
                            if log_func:
                                log_func("Editor not found!")
                            continue
                        
                        editor = editors[-1]
                        editor.click()
                        time.sleep(random.uniform(0.5, 1))
                        
                        if use_ai:
                            for char in comment_text:
                                editor.type(char)
                                time.sleep(random.uniform(0.02, 0.08))
                        else:
                            page.evaluate(f'arguments[0].textContent = "{comment_text}"', editor)
                        
                        time.sleep(random.uniform(1, 2))
                        
                        submit_buttons = page.query_selector_all('button[type="submit"]')
                        if submit_buttons:
                            submit_buttons[-1].click()
                            if log_func:
                                log_func(f"✓ Comment posted successfully!")
                            commented_threads.add(clean_url)
                            comments_made += 1
                            if mode == "infinite":
                                if log_func:
                                    log_func(f"📊 Total comments made: {comments_made}")
                            else:
                                if log_func:
                                    log_func(f"📊 Comments made: {comments_made}/{max_comments}")
                        else:
                            if log_func:
                                log_func("Reply button not found!")
                    
                    except Exception as e:
                        if log_func:
                            log_func(f"Error parsing/commenting post: {e}")
                        continue
                
                except Exception as e:
                    if log_func:
                        log_func(f"Error finding posts: {e}")
                    time.sleep(30)
                    continue
                
                if mode == "infinite" or comments_made < max_comments:
                    total_seconds = random.randint(min_time, max_time)
                    next_time = (datetime.now() + timedelta(seconds=total_seconds)).strftime('%H:%M:%S')
                    if log_func:
                        log_func(f"⏰ Next comment in {total_seconds} seconds (scheduled at {next_time})")
                    
                    for remaining_sec in range(total_seconds, 0, -10):
                        mins, secs = divmod(remaining_sec, 60)
                        if remaining_sec % 30 == 0 or remaining_sec <= 10:
                            if log_func:
                                log_func(f"⏳ Time left: {mins} min {secs} sec")
                        time.sleep(10)
            
            if mode == "limited":
                if log_func:
                    log_func(f"Session completed! Total comments: {comments_made}")
            
            return True
        
        finally:
            context.close()
            browser.close()
            if log_func:
                log_func("Browser closed.")