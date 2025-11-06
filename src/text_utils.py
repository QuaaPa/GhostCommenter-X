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
    """Ensure comment meets length requirements"""
    if len(comment) < min_length:
        comment += " вобще интересно"
    
    if len(comment) > max_length:
        comment = comment[:max_length].rsplit(' ', 1)[0]
    
    return comment