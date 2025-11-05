"""GhostCommenter-X - Main GUI Application"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from browser_automation import run_commenter_script
from ai_generator import generate_ai_comment, G4F_AVAILABLE
from training.trainer import CommentTrainer
from training.evaluator import EvaluatorWindow


class GhostCommenterApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GhostCommenter-X 🚀")
        self.root.geometry("700x750")
        
        self.config = ConfigManager()
        self.trainer = CommentTrainer()
        self.paused = False
        self.commented_threads = set()
        
        self.prompts = self.config.load_prompts()
        self.saved_credentials = self.config.load_saved_credentials()
        
        self._create_menu()
        self._create_ui()
        self._show_welcome_message()
    
    def _create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reload Prompts", command=self._reload_prompts)
        file_menu.add_command(label="Clear History", command=self._clear_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Training menu
        training_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Training", menu=training_menu)
        training_menu.add_command(label="Open Training Mode", command=self._open_training)
        training_menu.add_command(label="View Statistics", command=self._view_stats)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_ui(self):
        """Create main user interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        self._create_settings_tab(settings_frame)
        
        # Log tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="📋 Log")
        self._create_log_tab(log_frame)
        
        # Status bar
        self._create_status_bar()
    
    def _create_settings_tab(self, parent):
        """Create settings tab content"""
        # Credentials section
        cred_frame = ttk.LabelFrame(parent, text="Credentials", padding=10)
        cred_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(cred_frame, text="Login:").grid(row=0, column=0, sticky="w", pady=5)
        self.login_entry = ttk.Entry(cred_frame, width=30)
        self.login_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Add saved credentials dropdown
        if self.saved_credentials:
            ttk.Label(cred_frame, text="Saved:").grid(row=0, column=2, sticky="w", padx=(10, 0))
            self.saved_combo = ttk.Combobox(
                cred_frame, 
                values=list(self.saved_credentials.keys()), 
                state="readonly", 
                width=15
            )
            self.saved_combo.grid(row=0, column=3, padx=5)
            self.saved_combo.bind("<<ComboboxSelected>>", self._load_saved_credential)
        
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(cred_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Timing section
        timing_frame = ttk.LabelFrame(parent, text="Timing", padding=10)
        timing_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(timing_frame, text="Min time (sec):").grid(row=0, column=0, sticky="w", pady=5)
        self.min_time_entry = ttk.Entry(timing_frame, width=15)
        self.min_time_entry.insert(0, "30")
        self.min_time_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(timing_frame, text="Max time (sec):").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.max_time_entry = ttk.Entry(timing_frame, width=15)
        self.max_time_entry.insert(0, "60")
        self.max_time_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Mode section
        mode_frame = ttk.LabelFrame(parent, text="Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.mode_var = tk.StringVar(value="infinite")
        ttk.Radiobutton(
            mode_frame, 
            text="Infinite (until stopped)", 
            variable=self.mode_var, 
            value="infinite"
        ).pack(anchor=tk.W, pady=2)
        
        limited_frame = ttk.Frame(mode_frame)
        limited_frame.pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(
            limited_frame, 
            text="Limited to:", 
            variable=self.mode_var, 
            value="limited"
        ).pack(side=tk.LEFT)
        self.max_comments_entry = ttk.Entry(limited_frame, width=8)
        self.max_comments_entry.insert(0, "10")
        self.max_comments_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(limited_frame, text="comments").pack(side=tk.LEFT)
        
        # AI section
        ai_frame = ttk.LabelFrame(parent, text="AI Generation", padding=10)
        ai_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.ai_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            ai_frame, 
            text="Enable AI Comment Generation", 
            variable=self.ai_var,
            command=self._toggle_ai_fields
        ).pack(anchor=tk.W, pady=5)
        
        provider_frame = ttk.Frame(ai_frame)
        provider_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(provider_frame, text="Provider:").pack(side=tk.LEFT)
        self.provider_var = tk.StringVar(value='g4f')
        self.provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.provider_var,
            values=['g4f', 'openai', 'none'],
            state="readonly",
            width=20
        )
        self.provider_combo.pack(side=tk.LEFT, padx=5)
        self.provider_combo.bind("<<ComboboxSelected>>", lambda e: self._toggle_api_key())
        
        api_frame = ttk.Frame(ai_frame)
        api_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(api_frame, text="OpenAI API Key:").pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(api_frame, width=30, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        
        default_key = self.config.load_api_key()
        if default_key:
            self.api_key_entry.insert(0, default_key)
        
        # Info label
        self.info_label = ttk.Label(
            ai_frame,
            text="💡 G4F is FREE - No API key needed!",
            foreground="green",
            font=("Arial", 9, "bold")
        )
        self.info_label.pack(pady=5)
        
        self._toggle_ai_fields()
        
        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(
            button_frame,
            text="🚀 Start",
            command=self._start_script,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            height=2
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.pause_btn = tk.Button(
            button_frame,
            text="⏸ Pause",
            command=self._toggle_pause,
            bg="#FF9800",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            height=2
        )
        self.pause_btn.pack(side=tk.LEFT, padx=10)
    
    def _create_log_tab(self, parent):
        """Create log tab content"""
        ttk.Label(
            parent,
            text="Activity Log",
            font=("Arial", 10, "bold")
        ).pack(pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            width=80,
            height=30,
            state='disabled',
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        g4f_status = "✓ G4F Available" if G4F_AVAILABLE else "✗ G4F Not Installed"
        status_color = "green" if G4F_AVAILABLE else "red"
        
        self.status_label = ttk.Label(
            status_frame,
            text=f"{g4f_status} | Ready",
            foreground=status_color
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        self.stats_label = ttk.Label(
            status_frame,
            text="Training: 0 evaluations"
        )
        self.stats_label.pack(side=tk.RIGHT, padx=10, pady=2)
        
        self._update_training_stats()
    
    def _show_welcome_message(self):
        """Show welcome message in log"""
        self.log("=" * 70)
        self.log("🚀 GhostCommenter-X with AI Training")
        self.log("=" * 70)
        if G4F_AVAILABLE:
            self.log("✓ G4F is ready! Unlimited FREE comments!")
        else:
            self.log("⚠ G4F not installed. Use: pip install g4f")
        self.log("💡 Use Training menu to improve AI quality")
        self.log("=" * 70 + "\n")
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def _load_saved_credential(self, event=None):
        """Load selected saved credential"""
        selected = self.saved_combo.get()
        if selected in self.saved_credentials:
            self.login_entry.delete(0, tk.END)
            self.login_entry.insert(0, selected)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, self.saved_credentials[selected])
    
    def _toggle_ai_fields(self):
        """Toggle AI-related fields"""
        if self.ai_var.get():
            self.provider_combo.config(state='readonly')
            self._toggle_api_key()
        else:
            self.provider_combo.config(state='disabled')
            self.api_key_entry.config(state='disabled')
    
    def _toggle_api_key(self):
        """Toggle API key field based on provider"""
        if self.ai_var.get() and self.provider_var.get() == 'openai':
            self.api_key_entry.config(state='normal')
        else:
            self.api_key_entry.config(state='disabled')
    
    def _start_script(self):
        """Start the automation script"""
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not login or not password:
            messagebox.showerror("Error", "Please enter login and password!")
            return
        
        try:
            min_time = int(self.min_time_entry.get())
            max_time = int(self.max_time_entry.get())
            mode = self.mode_var.get()
            max_comments = 0
            
            if mode == "limited":
                max_comments = int(self.max_comments_entry.get())
                if max_comments < 1:
                    messagebox.showerror("Error", "Max comments must be at least 1!")
                    return
            
            if min_time < 10:
                messagebox.showerror("Error", "Minimum time must be at least 10 seconds!")
                return
            if max_time < min_time:
                messagebox.showerror("Error", "Maximum time must be greater than minimum!")
                return
        
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
            return
        
        use_ai = self.ai_var.get()
        ai_provider = self.provider_var.get()
        api_key = self.api_key_entry.get().strip()
        
        if use_ai and ai_provider == 'openai' and not api_key:
            messagebox.showerror("Error", "Please enter OpenAI API key!")
            return
        
        if use_ai and ai_provider == 'g4f' and not G4F_AVAILABLE:
            response = messagebox.askyesno(
                "G4F Not Installed",
                "G4F is not installed.\n\nInstall: pip install g4f\n\nContinue with templates?"
            )
            if not response:
                return
            use_ai = False
        
        threading.Thread(
            target=run_commenter_script,
            args=(
                login, password, min_time, max_time, use_ai, api_key,
                self.prompts, mode, max_comments, ai_provider, False,
                self.log, self.commented_threads
            ),
            daemon=True
        ).start()
    
    def _toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        self.pause_btn.config(text="▶ Resume" if self.paused else "⏸ Pause")
        self.log("⏸ Paused" if self.paused else "▶ Resumed")
    
    def _reload_prompts(self):
        """Reload AI prompts from file"""
        self.prompts = self.config.load_prompts()
        self.log("✓ Prompts reloaded successfully")
        messagebox.showinfo("Success", "AI prompts reloaded!")
    
    def _clear_history(self):
        """Clear comment history"""
        self.commented_threads.clear()
        self.log("🗑 Comment history cleared")
        messagebox.showinfo("Success", "History cleared!")
    
    def _open_training(self):
        """Open training mode window"""
        def generate_wrapper(title, content):
            return generate_ai_comment(
                title, content,
                self.api_key_entry.get(),
                self.prompts,
                self.provider_var.get(),
                self.log
            )
        
        EvaluatorWindow(self.trainer, generate_wrapper)
    
    def _view_stats(self):
        """View training statistics"""
        stats = self.trainer.get_statistics()
        
        msg = f"Training Statistics\n\n"
        msg += f"Total Evaluations: {stats['total_evaluations']}\n"
        msg += f"Average Rating: {stats['average_rating']:.2f}/5\n"
        msg += f"Average Length: {stats['average_length']:.0f} chars\n\n"
        msg += "Rating Distribution:\n"
        for i in range(5, 0, -1):
            count = stats['rating_distribution'].get(i, 0)
            msg += f"{i}⭐: {count}\n"
        
        messagebox.showinfo("Training Statistics", msg)
    
    def _update_training_stats(self):
        """Update training statistics in status bar"""
        stats = self.trainer.get_statistics()
        self.stats_label.config(
            text=f"Training: {stats['total_evaluations']} evaluations"
        )
        self.root.after(5000, self._update_training_stats)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """GhostCommenter-X v1.0

AI-powered forum automation with self-learning

Features:
• Free AI with G4F
• Self-improving through training
• Smart comment generation
• Anti-detection measures

GitHub: github.com/yourusername/GhostCommenter-X
"""
        messagebox.showinfo("About", about_text)


def main():
    """Application entry point"""
    root = tk.Tk()
    app = GhostCommenterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()