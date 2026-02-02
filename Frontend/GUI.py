import os
import sys
import threading
import time
import asyncio
from queue import Queue, Empty
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import scrolledtext
except Exception:
    raise RuntimeError("tkinter is required to run the GUI")

# Ensure Backend folder is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "Backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

# Import backend modules with graceful fallbacks
try:
    import Model
    import Chatbot
    import RealtimeSearchEngine
    import ImageGeneration
    import Automation
    import SpeechToText
    import TextToSpeech
except Exception as e:
    # If any import fails, create dummies to avoid crashing the GUI at import time
    print(f"Warning: backend import failed: {e}")

    class _Dummy:
        def __getattr__(self, name):
            def _f(*a, **k):
                return f"Backend not available: {name}"
            return _f

    Model = Chatbot = RealtimeSearchEngine = ImageGeneration = Automation = SpeechToText = TextToSpeech = _Dummy()


class JarvisAssistantUI:
    """ChatGPT-Style AI Assistant UI"""

    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. - AI Assistant")
        self.root.geometry("1200x800")
        
        # ChatGPT-like color scheme
        self.colors = {
            'bg_dark': '#343541',
            'bg_light': '#40414f',
            'bg_sidebar': '#202123',
            'bg_input': '#40414f',
            'accent': '#10a37f',
            'accent_hover': '#1a7f64',
            'accent_red': '#ef4146',
            'text_primary': '#ececf1',
            'text_secondary': '#8e8ea0',
            'text_muted': '#acacbe',
            'border': '#565869',
            'user_msg': '#343541',
            'assistant_msg': '#444654'
        }
        
        # Fonts (ChatGPT-like)
        self.fonts = {
            'title': ('Segoe UI', 20, 'bold'),
            'heading': ('Segoe UI', 16, 'bold'),
            'body': ('Segoe UI', 14),
            'mono': ('Consolas', 12),
            'small': ('Segoe UI', 12),
            'chat': ('Segoe UI', 14)
        }
        
        # Set window background
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Configure styles
        self.setup_styles()
        
        self.queue = Queue()
        self._build_widgets()
        self._start_queue_poller()

        self.voice_listening = False
        self.tts_enabled = True
        
        # Add window icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

    def setup_styles(self):
        """Setup ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       font=self.fonts['small'],
                       focuscolor='none')
        
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_hover'])])

    def _build_widgets(self):
        """Build all UI widgets"""
        self.create_sidebar()
        self.create_main_area()
        self.create_input_area()

    def create_sidebar(self):
        """Create left sidebar like ChatGPT"""
        sidebar = tk.Frame(self.root, bg=self.colors['bg_sidebar'], width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # New Chat button (top)
        new_chat_btn = tk.Button(sidebar,
                                text="+ New chat",
                                bg=self.colors['bg_sidebar'],
                                fg=self.colors['text_primary'],
                                font=('Segoe UI', 13, 'bold'),
                                relief=tk.FLAT,
                                bd=0,
                                padx=20,
                                pady=15,
                                anchor='w',
                                command=self.clear_chat)
        new_chat_btn.pack(fill=tk.X)
        
        # Separator
        separator = tk.Frame(sidebar, height=1, bg=self.colors['border'])
        separator.pack(fill=tk.X, padx=15, pady=10)
        
        # Chat history title
        
        
        # Chat history items (placeholder)
        
        
        # Bottom section
        bottom_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=15)
        
        # User info
        user_frame = tk.Frame(bottom_frame, bg=self.colors['bg_sidebar'])
        user_frame.pack(fill=tk.X, pady=(0, 15))
        
        user_icon = tk.Label(user_frame,
                            text="👤",
                            font=('Arial', 14),
                            bg=self.colors['bg_sidebar'],
                            fg=self.colors['text_primary'])
        user_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        user_name = tk.Label(user_frame,
                            text="User",
                            bg=self.colors['bg_sidebar'],
                            fg=self.colors['text_primary'],
                            font=('Segoe UI', 11))
        user_name.pack(side=tk.LEFT)
        
        # Voice button (Prominent)
        voice_frame = tk.Frame(bottom_frame, bg=self.colors['bg_sidebar'])
        voice_frame.pack(fill=tk.X)
        
        # Large mic button with highlight
        self.voice_btn = tk.Button(voice_frame,
                                  text="🎤  Voice Input",
                                  bg=self.colors['accent'],
                                  fg=self.colors['text_primary'],
                                  font=('Segoe UI', 12, 'bold'),
                                  relief=tk.FLAT,
                                  bd=0,
                                  padx=15,
                                  pady=12,
                                  width=20,
                                  command=self.on_voice_toggle)
        self.voice_btn.pack(fill=tk.X)
        
        # TTS toggle
        self.tts_var = tk.BooleanVar(value=True)
        tts_check = tk.Checkbutton(bottom_frame,
                                  text="Voice Responses",
                                  variable=self.tts_var,
                                  bg=self.colors['bg_sidebar'],
                                  fg=self.colors['text_primary'],
                                  selectcolor=self.colors['accent'],
                                  activebackground=self.colors['bg_sidebar'],
                                  activeforeground=self.colors['text_primary'],
                                  font=('Segoe UI', 10))
        tts_check.pack(pady=(10, 0))

    def create_main_area(self):
        """Create main chat area like ChatGPT"""
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Top bar
        top_bar = tk.Frame(main_container, bg=self.colors['bg_dark'], height=60)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
        # Assistant title in center
        title_label = tk.Label(top_bar,
                              text="J.A.R.V.I.S.",
                              bg=self.colors['bg_dark'],
                              fg=self.colors['text_primary'],
                              font=self.fonts['title'])
        title_label.pack(expand=True, pady=10)
        
        # Status indicator
        self.status_var = tk.StringVar(value="● Ready")
        status_label = tk.Label(top_bar,
                               textvariable=self.status_var,
                               font=self.fonts['small'],
                               fg=self.colors['accent'],
                               bg=self.colors['bg_dark'])
        status_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Chat display area
        chat_container = tk.Frame(main_container, bg=self.colors['bg_dark'])
        chat_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable chat area
        self.chat = scrolledtext.ScrolledText(chat_container,
                                             bg=self.colors['bg_dark'],
                                             fg=self.colors['text_primary'],
                                             insertbackground=self.colors['text_primary'],
                                             font=self.fonts['chat'],
                                             wrap=tk.WORD,
                                             state=tk.DISABLED,
                                             relief=tk.FLAT,
                                             bd=0,
                                             spacing1=10,
                                             spacing3=10,
                                             padx=20,
                                             pady=10)
        self.chat.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for different message types
        self.chat.tag_config('timestamp', foreground=self.colors['text_muted'], font=('Segoe UI', 10))
        self.chat.tag_config('user', foreground=self.colors['accent'], font=('Segoe UI', 12, 'bold'))
        self.chat.tag_config('assistant', foreground=self.colors['accent'], font=('Segoe UI', 12, 'bold'))
        self.chat.tag_config('system', foreground=self.colors['text_muted'], font=('Segoe UI', 12, 'bold'))

    def create_input_area(self):
        """Create input area at bottom like ChatGPT"""
        input_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        input_container.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        # Input frame
        input_frame = tk.Frame(input_container, bg=self.colors['bg_input'])
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Text input
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(input_frame,
                                   textvariable=self.input_var,
                                   bg=self.colors['bg_input'],
                                   fg=self.colors['text_primary'],
                                   insertbackground=self.colors['text_primary'],
                                   font=self.fonts['body'],
                                   relief=tk.FLAT,
                                   bd=0,
                                   width=50)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=15, ipady=5)
        self.input_entry.bind("<Return>", lambda e: self.on_send())
        
        # Send button
        send_btn = tk.Button(input_frame,
                            text="➤",
                            bg=self.colors['accent'],
                            fg=self.colors['text_primary'],
                            font=('Arial', 14),
                            relief=tk.FLAT,
                            bd=0,
                            width=3,
                            command=self.on_send)
        send_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Quick actions row
        actions_frame = tk.Frame(input_container, bg=self.colors['bg_dark'])
        actions_frame.pack(fill=tk.X)
        
        actions = [
            
        ]
        
        for action_text, action_cmd in actions:
            btn = tk.Button(actions_frame,
                          text=action_text,
                          bg=self.colors['bg_light'],
                          fg=self.colors['text_primary'],
                          font=('Segoe UI', 10),
                          relief=tk.FLAT,
                          bd=0,
                          padx=10,
                          pady=5,
                          command=lambda cmd=action_cmd: self.set_and_send(cmd))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Log display at bottom
        self.log_var = tk.StringVar(value="System: Ready")
        log_label = tk.Label(input_container,
                            textvariable=self.log_var,
                            font=('Segoe UI', 10),
                            fg=self.colors['text_muted'],
                            bg=self.colors['bg_dark'])
        log_label.pack(side=tk.LEFT, pady=(5, 0))

    def load_chat(self, chat_id):
        """Load chat history (placeholder)"""
        self.append_chat("System", f"Loading chat {chat_id}...")

    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%I:%M %p")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)

    def show_progress(self, show=True):
        """Show or hide progress bar"""
        if show:
            self.status_var.set("● Processing...")
        else:
            self.status_var.set("● Ready")

    # ========== Chat Methods ==========
    
    def _start_queue_poller(self):
        def poll():
            try:
                while True:
                    item = self.queue.get_nowait()
                    func, args = item
                    try:
                        func(*args)
                    except Exception as e:
                        print(f"UI queue item error: {e}")
            except Empty:
                pass
            self.root.after(100, poll)
        poll()

    def append_chat(self, who: str, text: str, slow=False):
        timestamp = datetime.now().strftime("%H:%M")
        
        # Define colors for different senders
        bg_colors = {
            'You': self.colors['user_msg'],
            'Jarvis': self.colors['assistant_msg'],
            'System': self.colors['bg_dark']
        }
        
        bg_color = bg_colors.get(who, self.colors['bg_dark'])
        
        def insert_all():
            self.chat.configure(state=tk.NORMAL)
            
            # Configure tag for this message
            tag_name = f"msg_{id(self)}"
            self.chat.tag_config(tag_name, background=bg_color, lmargin1=20, lmargin2=20, rmargin=20, spacing3=10)
            
            # Insert timestamp
            self.chat.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            
            # Insert sender
            if who == 'You':
                self.chat.insert(tk.END, f"You", 'user')
            elif who == 'Jarvis':
                self.chat.insert(tk.END, f"Jarvis", 'assistant')
            else:
                self.chat.insert(tk.END, f"{who}", 'system')
            
            self.chat.insert(tk.END, "\n")
            
            # Insert message with typing effect if enabled
            if slow:
                self.chat.insert(tk.END, "", tag_name)  # Start tag
                self.chat.mark_set("insert", tk.END)
                for ch in text:
                    self.chat.insert(tk.END, ch, tag_name)
                    self.chat.see(tk.END)
                    self.chat.update_idletasks()
                    time.sleep(0.002)
            else:
                self.chat.insert(tk.END, text, tag_name)

            self.chat.insert(tk.END, "\n\n")
            self.chat.configure(state=tk.DISABLED)
            self.chat.see(tk.END)

        self.queue.put((insert_all, ()))

    def set_status(self, text: str):
        self.queue.put((self.status_var.set, (f"● {text}",)))

    def set_log(self, text: str):
        self.queue.put((self.log_var.set, (f"System: {text}",)))

    # Actions
    def set_and_send(self, q: str):
        self.input_var.set(q)
        self.on_send()

    def clear_chat(self):
        def _clear():
            self.chat.configure(state=tk.NORMAL)
            self.chat.delete(1.0, tk.END)
            self.chat.configure(state=tk.DISABLED)
            self.append_chat("System", "New chat started. How can I help you today?")
        self.queue.put((_clear, ()))

    def on_send(self):
        query = self.input_var.get().strip()
        if not query:
            return
        self.input_var.set("")
        self.append_chat("You", query)
        self.show_progress(True)
        threading.Thread(target=self._dispatch_query, args=(query,), daemon=True).start()

    def _dispatch_query(self, query: str):
        self.set_log("Processing your request...")

        try:
            decision = Model.FirstLayerDMM(query)
        except Exception as e:
            decision = [f"general {query}"]

        self.set_log(f"Model output: {decision}")
        # If multiple tasks returned, handle each
        for task in decision:
            task = task.strip()
            if task.startswith("general "):
                prompt = task.removeprefix("general ")
                self.set_status("Thinking...")
                try:
                    answer = Chatbot.ChatBot(prompt)
                except Exception as e:
                    answer = f"I apologize, but I encountered an error: {e}"
                self.append_chat("Jarvis", answer, slow=True)
                if self.tts_var.get():
                    threading.Thread(target=self._speak, args=(answer,), daemon=True).start()

            elif task.startswith("realtime "):
                prompt = task.removeprefix("realtime ")
                self.set_status("Searching...")
                try:
                    answer = RealtimeSearchEngine.RealtimeSearchEngine(prompt)
                except Exception as e:
                    answer = f"Search error: {e}"
                self.append_chat("Jarvis", answer, slow=True)
                if self.tts_var.get():
                    threading.Thread(target=self._speak, args=(answer,), daemon=True).start()

            elif task.startswith("generate image"):
                prompt = task.removeprefix("generate image").strip()
                if not prompt:
                    prompt = query
                self.set_status("Generating...")
                self.append_chat("System", f"Generating image: {prompt}")
                try:
                    ImageGeneration.GenerateImages(prompt)
                    self.append_chat("System", "✓ Image saved in Data folder")
                except Exception as e:
                    self.append_chat("System", f"✗ Image generation failed: {e}")

            elif task.startswith("play "):
                param = task.removeprefix("play ")
                self.set_status("Playing...")
                self.append_chat("System", f"Playing: {param}")
                try:
                    Automation.PlayYoutube(param)
                except Exception as e:
                    self.append_chat("System", f"✗ Play failed: {e}")

            elif task.startswith("open ") or task.startswith("close ") or task.startswith("content ") or task.startswith("google search ") or task.startswith("youtube search ") or task.startswith("system "):
                self.set_status("Executing...")
                try:
                    asyncio.run(Automation.Automation([task]))
                    self.append_chat("System", f"✓ Executed: {task}")
                except Exception as e:
                    self.append_chat("System", f"✗ Automation error: {e}")

            elif task == "exit":
                self.append_chat("System", "Goodbye!")
                self.set_status("Exiting...")
                time.sleep(0.5)
                self.root.quit()

            else:
                self.set_status("Thinking...")
                try:
                    answer = Chatbot.ChatBot(task)
                except Exception as e:
                    answer = f"Error: {e}"
                self.append_chat("Jarvis", answer, slow=True)
                if self.tts_var.get():
                    threading.Thread(target=self._speak, args=(answer,), daemon=True).start()

        self.show_progress(False)
        self.set_status("Ready")
        self.set_log("Ready")

    def on_voice_toggle(self):
        if not self.voice_listening:
            self.voice_listening = True
            self.voice_btn.configure(text="🔴 Listening...", bg=self.colors['accent_red'])
            self.set_status("Listening...")
            threading.Thread(target=self._do_listen, daemon=True).start()
        else:
            self.voice_listening = False
            self.voice_btn.configure(text="🎤  Voice Input", bg=self.colors['accent'])
            self.set_status("Ready")

    def _do_listen(self):
        self.set_log("Listening... Speak now")
        try:
            text = SpeechToText.SpeechRecognition()
            if text:
                self.append_chat("You (voice)", text)
                threading.Thread(target=self._dispatch_query, args=(text,), daemon=True).start()
        except Exception as e:
            self.append_chat("System", f"Voice recognition error: {e}")
        finally:
            self.voice_listening = False
            self.voice_btn.configure(text="🎤  Voice Input", bg=self.colors['accent'])
            self.set_status("Ready")

    def _speak(self, text: str):
        try:
            TextToSpeech.TextToSpeech(text)
        except Exception as e:
            self.append_chat("System", f"TTS error: {e}")


def main():
    root = tk.Tk()
    app = JarvisAssistantUI(root)
    
    # Add welcome message
    root.after(1000, lambda: app.append_chat("Jarvis", 
        "Hello! I'm J.A.R.V.I.S., your AI assistant. How can I help you today?"))
    
    root.mainloop()


if __name__ == "__main__":
    main()