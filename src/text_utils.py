"""Text processing utilities for natural language generation"""

import random


def humanize_text(text: str) -> str:
    """Make text more human-like by removing formatting and adding natural imperfections"""
    # Remove list markers
    text = text.replace('1) ', '').replace('2) ', '').replace('3) ', '')
    text = text.replace('• ', '').replace('- ', '', 2)
    text = text.replace('**', '').replace('*', '')
    
    # Remove all punctuation
    punctuation = '.,!?;:—–-«»""'
    for char in punctuation:
        text = text.replace(char, '')
    
    # Remove ellipsis
    text = text.replace('...', ' ')
    text = text.replace('..', ' ')
    
    # Clean extra spaces
    text = ' '.join(text.split())
    
    # Randomly lowercase first letter (30% chance)
    if random.random() < 0.3 and text:
        text = text[0].lower() + text[1:]
    
    text = add_typos(text)
    
    return text

def is_sentence_complete(text: str) -> bool:
    """Check if a sentence appears to be complete"""
    if not text or len(text.strip()) < 10:
        return False
    
    text = text.strip()
    words = text.split()
    
    # Need at least 3 words
    if len(words) < 3:
        return False
    
    # Check last word - should be a complete word
    last_word = words[-1].lower()
    
    # Incomplete indicators - words that suggest sentence is cut off
    incomplete_endings = [
        'и', 'но', 'а', 'или', 'что', 'как', 'когда', 'где',
        'с', 'в', 'на', 'по', 'к', 'у', 'о', 'от', 'до',
        'для', 'про', 'без', 'через', 'над', 'под', 'при',
        'очень', 'более', 'менее', 'самый', 'такой', 'этот',
        'мой', 'твой', 'наш', 'ваш', 'их', 'его', 'ее'
    ]
    
    if last_word in incomplete_endings:
        return False
    
    # Check for incomplete verb forms
    incomplete_verbs = ['буд', 'мог', 'дела', 'сдела', 'сказа', 'говор']
    for verb in incomplete_verbs:
        if last_word.startswith(verb) and len(last_word) < len(verb) + 2:
            return False
    
    return True


def complete_sentence(text: str) -> str:
    """Try to complete an incomplete sentence naturally"""
    if is_sentence_complete(text):
        return text
    
    words = text.split()
    last_word = words[-1].lower() if words else ""
    
    # Completion patterns based on last word
    completions = {
        'и': ['все', 'нормально', 'ладно', 'так'],
        'но': ['нормально', 'ладно', 'хорошо'],
        'а': ['норм', 'ладно', 'так'],
        'что': ['интересно', 'думаешь', 'скажешь'],
        'как': ['думаешь', 'считаешь', 'так'],
        'с': ['этим', 'ним', 'тем'],
        'в': ['этом', 'общем', 'итоге'],
        'на': ['это', 'самом деле'],
        'для': ['этого', 'начала'],
        'про': ['это', 'него'],
        'очень': ['интересно', 'круто', 'неплохо'],
        'более': ['менее', 'интересно'],
        'такой': ['же', 'вариант'],
        'этот': ['момент', 'случай'],
    }
    
    # Try to complete based on last word
    if last_word in completions:
        completion = random.choice(completions[last_word])
        return text + ' ' + completion
    
    # Fallback completions
    fallback_endings = [
        'норм', 'годно', 'неплохо', 'интересно', 
        'в общем', 'короче', 'кстати'
    ]
    
    return text + ' ' + random.choice(fallback_endings)


def add_typos(text: str) -> str:
    """Add natural typos to make text more human-like"""
    typo_patterns = [
        ('что', 'че'), ('чтобы', 'чтобы'), ('потому что', 'потому что'),
        ('также', 'так же'), ('сейчас', 'щас'),
        ('ничего', 'ниче'), ('что-то', 'че то'), ('как-то', 'как то'),
        ('вроде', 'вродь'), ('конечно', 'канешно'), ('наверное', 'наверно'),
        ('его', 'ево'), ('блин',''), ('вообще', ''), ('жесть', ''),
    ]
    
    num_errors = random.randint(1, 2)
    errors_added = 0
    random.shuffle(typo_patterns)
    
    for original, typo in typo_patterns:
        if errors_added >= num_errors:
            break
        if original in text.lower():
            words = text.split()
            for i, word in enumerate(words):
                if original in word.lower() and errors_added < num_errors:
                    if random.random() < 0.1:
                        words[i] = word.lower().replace(original, typo)
                        errors_added += 1
                        break
            text = ' '.join(words)
    
    return text


def generate_random_comment(title: str, content: str) -> str:
    """Generate a random template-based comment"""
    templates = [
        "да у меня так же было",
        "не знал об этом честно",
        "да тоже заметил это недавно",
        "согласен с этим полностью",
        "ну да логично звучит",
    ]
    
    comment = random.choice(templates)
    comment = add_typos(comment)
    
    # Ensure minimum length
    if len(comment) < 20:
        additions = [" интересно", " кстати", " щас попробую", " годно"]
        comment += random.choice(additions)
    
    # Ensure maximum length
    if len(comment) > 60:
        comment = comment[:60].rsplit(' ', 1)[0]
    
    return comment


def validate_comment_length(comment: str, min_length: int = 20, max_length: int = 60) -> str:
    """Ensure comment meets length requirements and is complete"""
    
    # First check if sentence is complete
    if not is_sentence_complete(comment):
        comment = complete_sentence(comment)
    
    # Now handle length
    if len(comment) < min_length:
        # Add natural extensions
        extensions = [" интересно", " кстати", " вобще", " норм", " годно"]
        while len(comment) < min_length and extensions:
            ext = random.choice(extensions)
            if ext not in comment:  # Avoid duplicates
                comment += ext
                extensions.remove(ext)
    
    # Handle maximum length - cut at word boundary
    if len(comment) > max_length:
        words = comment[:max_length].split()
        
        if words:
            truncated = ' '.join(words[:-1])
            
            if is_sentence_complete(truncated):
                comment = truncated
            else:
                truncated_with_last = ' '.join(words)
                if is_sentence_complete(truncated_with_last) and len(truncated_with_last) <= max_length + 5:
                    comment = truncated_with_last
                else:
                    comment = complete_sentence(truncated)
    
    # Final verification
    if not is_sentence_complete(comment):
        comment = complete_sentence(comment)
    
    # Final length check
    if len(comment) > max_length + 10:
        words = comment.split()
        while len(' '.join(words)) > max_length and len(words) > 3:
            words.pop()
        comment = ' '.join(words)
        
        if not is_sentence_complete(comment):
            comment = complete_sentence(comment)
    
    return comment.strip()