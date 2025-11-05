"""AI Training Module - Learn from user evaluations"""

import json
import os
from typing import Dict, List, Tuple
from datetime import datetime


class CommentTrainer:
    """Trains AI by learning from user evaluations"""
    
    def __init__(self, data_file: str = "data/training_data.json"):
        self.data_file = data_file
        self.training_data = self._load_training_data()
    
    def _load_training_data(self) -> List[Dict]:
        """Load existing training data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading training data: {e}")
                return []
        return []
    
    def save_evaluation(self, title: str, content: str, comment: str, 
                       rating: int, feedback: str = ""):
        """Save user evaluation of a comment"""
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'content': content[:500],  # Truncate for storage
            'comment': comment,
            'rating': rating,
            'feedback': feedback,
            'comment_length': len(comment)
        }
        
        self.training_data.append(evaluation)
        self._save_training_data()
    
    def _save_training_data(self):
        """Save training data to file"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_data, f, ensure_ascii=False, indent=2)
    
    def get_statistics(self) -> Dict:
        """Get training statistics"""
        if not self.training_data:
            return {
                'total_evaluations': 0,
                'average_rating': 0,
                'rating_distribution': {},
                'average_length': 0
            }
        
        ratings = [d['rating'] for d in self.training_data]
        lengths = [d['comment_length'] for d in self.training_data]
        
        rating_dist = {}
        for i in range(1, 6):
            rating_dist[i] = ratings.count(i)
        
        return {
            'total_evaluations': len(self.training_data),
            'average_rating': sum(ratings) / len(ratings),
            'rating_distribution': rating_dist,
            'average_length': sum(lengths) / len(lengths),
            'high_rated_comments': self._get_high_rated_comments()
        }
    
    def _get_high_rated_comments(self, min_rating: int = 4) -> List[Dict]:
        """Get comments with high ratings"""
        return [
            {
                'comment': d['comment'],
                'rating': d['rating'],
                'length': d['comment_length']
            }
            for d in self.training_data 
            if d['rating'] >= min_rating
        ]
    
    def analyze_patterns(self) -> Dict[str, any]:
        """Analyze patterns in high-rated comments"""
        high_rated = [d for d in self.training_data if d['rating'] >= 4]
        low_rated = [d for d in self.training_data if d['rating'] <= 2]
        
        if not high_rated:
            return {}
        
        # Analyze word usage
        common_words = self._extract_common_words(high_rated)
        avoid_words = self._extract_common_words(low_rated)
        
        # Analyze length patterns
        high_lengths = [d['comment_length'] for d in high_rated]
        optimal_length = sum(high_lengths) / len(high_lengths) if high_lengths else 40
        
        return {
            'preferred_words': common_words[:20],
            'avoid_words': avoid_words[:10],
            'optimal_length': optimal_length,
            'sample_comments': [d['comment'] for d in high_rated[:5]]
        }
    
    def _extract_common_words(self, data: List[Dict]) -> List[str]:
        """Extract commonly used words from comments"""
        word_freq = {}
        
        for item in data:
            words = item['comment'].lower().split()
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words]
    
    def generate_improved_prompt(self, base_prompt: str) -> str:
        """Generate improved prompt based on training data"""
        patterns = self.analyze_patterns()
        
        if not patterns:
            return base_prompt
        
        # Add learned patterns to prompt
        improvements = "\n\nLEARNED PATTERNS FROM TRAINING:\n"
        
        if 'preferred_words' in patterns:
            improvements += f"- Preferred words: {', '.join(patterns['preferred_words'][:10])}\n"
        
        if 'optimal_length' in patterns:
            improvements += f"- Optimal length: ~{int(patterns['optimal_length'])} characters\n"
        
        if 'sample_comments' in patterns:
            improvements += "\nHigh-rated examples:\n"
            for comment in patterns['sample_comments']:
                improvements += f'"{comment}"\n'
        
        return base_prompt + improvements
    
    def export_training_summary(self, output_file: str = "data/training_summary.txt"):
        """Export human-readable training summary"""
        stats = self.get_statistics()
        patterns = self.analyze_patterns()
        
        summary = f"""GhostCommenter-X Training Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STATISTICS:
- Total Evaluations: {stats['total_evaluations']}
- Average Rating: {stats['average_rating']:.2f}/5
- Average Length: {stats['average_length']:.1f} characters

RATING DISTRIBUTION:
"""
        for rating in range(5, 0, -1):
            count = stats['rating_distribution'].get(rating, 0)
            bar = '█' * count
            summary += f"{rating}⭐: {count:3d} {bar}\n"
        
        if patterns:
            summary += f"\nPATTERNS:\n"
            summary += f"Optimal Length: {patterns.get('optimal_length', 0):.0f} characters\n"
            summary += f"\nPreferred Words: {', '.join(patterns.get('preferred_words', [])[:15])}\n"
            
            if 'sample_comments' in patterns:
                summary += "\nTop Rated Comments:\n"
                for i, comment in enumerate(patterns['sample_comments'], 1):
                    summary += f"{i}. {comment}\n"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return summary