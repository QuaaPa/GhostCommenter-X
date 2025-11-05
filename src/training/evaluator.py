"""Comment Evaluation UI - Rate and train AI"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
from typing import Callable
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.trainer import CommentTrainer


class EvaluatorWindow:
    """Window for evaluating and training AI comments"""
    
    def __init__(self, trainer: CommentTrainer, ai_generator_func: Callable):
        self.trainer = trainer
        self.ai_generator = ai_generator_func
        self.current_sample = None
        
        self.window = tk.Toplevel()
        self.window.title("AI Training - Comment Evaluator")
        self.window.geometry("800x700")
        
        self._create_ui()
        self._load_statistics()
    
    def _create_ui(self):
        """Create evaluation interface"""
        # Title
        title_label = tk.Label(
            self.window, 
            text="🎓 AI Training Mode", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(
            self.window,
            text="Load thread samples and rate AI-generated comments to improve quality",
            wraplength=700
        )
        instructions.pack(pady=5)
        
        # Control frame
        control_frame = tk.Frame(self.window)
        control_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Button(
            control_frame,
            text="📁 Load Thread Sample",
            command=self._load_sample,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="🎲 Generate Comment",
            command=self._generate_comment,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="📊 View Statistics",
            command=self._show_statistics,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Thread info frame
        thread_frame = tk.LabelFrame(self.window, text="Thread Info", padx=10, pady=10)
        thread_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        tk.Label(thread_frame, text="Title:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.title_text = tk.Text(thread_frame, height=2, wrap=tk.WORD)
        self.title_text.pack(fill=tk.X, pady=5)
        
        tk.Label(thread_frame, text="Content:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(thread_frame, height=6, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Comment frame
        comment_frame = tk.LabelFrame(self.window, text="Generated Comment", padx=10, pady=10)
        comment_frame.pack(pady=10, fill=tk.X, padx=20)
        
        self.comment_text = tk.Text(comment_frame, height=3, wrap=tk.WORD, font=("Arial", 10))
        self.comment_text.pack(fill=tk.X, pady=5)
        
        self.char_count_label = tk.Label(comment_frame, text="Length: 0 chars", fg="blue")
        self.char_count_label.pack()
        
        # Rating frame
        rating_frame = tk.LabelFrame(self.window, text="Rate This Comment", padx=10, pady=10)
        rating_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(
            rating_frame,
            text="How human-like and appropriate is this comment?"
        ).pack()
        
        # Star rating
        star_frame = tk.Frame(rating_frame)
        star_frame.pack(pady=10)
        
        self.rating_var = tk.IntVar(value=0)
        for i in range(1, 6):
            tk.Radiobutton(
                star_frame,
                text=f"{'⭐' * i}",
                variable=self.rating_var,
                value=i,
                font=("Arial", 12)
            ).pack(side=tk.LEFT, padx=5)
        
        # Feedback
        tk.Label(rating_frame, text="Optional Feedback:").pack(anchor=tk.W)
        self.feedback_text = tk.Text(rating_frame, height=2, wrap=tk.WORD)
        self.feedback_text.pack(fill=tk.X, pady=5)
        
        # Submit button
        tk.Button(
            rating_frame,
            text="✅ Submit Rating",
            command=self._submit_rating,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=20
        ).pack(pady=10)
        
        # Statistics display
        self.stats_label = tk.Label(
            self.window,
            text="No evaluations yet",
            font=("Arial", 9),
            fg="gray"
        )
        self.stats_label.pack(pady=10)
    
    def _load_sample(self):
        """Load thread sample from JSON file"""
        file_path = filedialog.askopenfilename(
            title="Select Thread Sample",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = json.load(f)
            
            self.current_sample = sample
            self.title_text.delete(1.0, tk.END)
            self.title_text.insert(1.0, sample.get('title', ''))
            
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, sample.get('content', ''))
            
            messagebox.showinfo("Success", "Thread sample loaded successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sample: {e}")
    
    def _generate_comment(self):
        """Generate AI comment for current thread"""
        if not self.current_sample:
            # Use manual input if no sample loaded
            title = self.title_text.get(1.0, tk.END).strip()
            content = self.content_text.get(1.0, tk.END).strip()
            
            if not title or not content:
                messagebox.showwarning("Warning", "Please load a sample or enter title and content manually")
                return
            
            self.current_sample = {'title': title, 'content': content}
        
        try:
            comment = self.ai_generator(
                self.current_sample['title'],
                self.current_sample['content']
            )
            
            if comment:
                self.comment_text.delete(1.0, tk.END)
                self.comment_text.insert(1.0, comment)
                self._update_char_count()
            else:
                messagebox.showerror("Error", "Failed to generate comment")
        
        except Exception as e:
            messagebox.showerror("Error", f"Generation failed: {e}")
    
    def _update_char_count(self):
        """Update character count display"""
        comment = self.comment_text.get(1.0, tk.END).strip()
        length = len(comment)
        
        color = "green" if 20 <= length <= 60 else "red"
        self.char_count_label.config(
            text=f"Length: {length} chars",
            fg=color
        )
    
    def _submit_rating(self):
        """Submit rating and save to training data"""
        if not self.current_sample:
            messagebox.showwarning("Warning", "No sample loaded")
            return
        
        rating = self.rating_var.get()
        if rating == 0:
            messagebox.showwarning("Warning", "Please select a rating")
            return
        
        comment = self.comment_text.get(1.0, tk.END).strip()
        if not comment:
            messagebox.showwarning("Warning", "No comment to rate")
            return
        
        feedback = self.feedback_text.get(1.0, tk.END).strip()
        
        # Save evaluation
        self.trainer.save_evaluation(
            title=self.current_sample['title'],
            content=self.current_sample['content'],
            comment=comment,
            rating=rating,
            feedback=feedback
        )
        
        # Clear form
        self.rating_var.set(0)
        self.feedback_text.delete(1.0, tk.END)
        self.comment_text.delete(1.0, tk.END)
        
        # Update statistics
        self._load_statistics()
        
        messagebox.showinfo("Success", f"Rating saved! (⭐ {rating}/5)")
    
    def _load_statistics(self):
        """Update statistics display"""
        stats = self.trainer.get_statistics()
        
        if stats['total_evaluations'] == 0:
            self.stats_label.config(text="No evaluations yet")
        else:
            text = f"📊 Stats: {stats['total_evaluations']} evaluations | "
            text += f"Avg: {stats['average_rating']:.1f}⭐ | "
            text += f"Avg length: {stats['average_length']:.0f} chars"
            self.stats_label.config(text=text)
    
    def _show_statistics(self):
        """Show detailed statistics window"""
        stats = self.trainer.get_statistics()
        patterns = self.trainer.analyze_patterns()
        
        # Create statistics window
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Training Statistics")
        stats_window.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(
            stats_window,
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Display summary
        summary = self.trainer.export_training_summary()
        text_widget.insert(1.0, summary)
        text_widget.config(state='disabled')
        
        # Export button
        tk.Button(
            stats_window,
            text="📥 Export Summary",
            command=lambda: self._export_summary(summary)
        ).pack(pady=10)
    
    def _export_summary(self, summary: str):
        """Export training summary to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            messagebox.showinfo("Success", "Summary exported successfully!")