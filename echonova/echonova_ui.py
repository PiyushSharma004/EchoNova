"""
EchoNova — Desktop Voice Assistant UI
Full Tkinter GUI with Hindi + English language support
Run: python echonova_ui.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import datetime
import os
import random
import math
import time

# ── Try importing voice/assistant libraries ───────────────────────────────────
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import wikipedia
    WIKI_AVAILABLE = True
except ImportError:
    WIKI_AVAILABLE = False

try:
    import webbrowser as wb
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import pyjokes
    JOKES_AVAILABLE = True
except ImportError:
    JOKES_AVAILABLE = False


# ── Colors & Theme ────────────────────────────────────────────────────────────
BG          = "#050a12"
SURFACE     = "#0a1628"
SURFACE2    = "#0d1f38"
BORDER      = "#0e2a4a"
ACCENT      = "#00d4ff"
ACCENT2     = "#0055cc"
ACCENT3     = "#00ff88"
ACCENT_HI   = "#ff9933"
TEXT        = "#c8e0f0"
TEXT_DIM    = "#4a7a99"
ERROR       = "#ff4444"
SUCCESS     = "#00ff88"

FONT_TITLE  = ("Courier New", 18, "bold")
FONT_MONO   = ("Courier New", 10)
FONT_MONO_S = ("Courier New", 9)
FONT_BODY   = ("Courier New", 11)
FONT_SMALL  = ("Courier New", 8)
FONT_CMD    = ("Courier New", 10, "bold")

# ── Responses ─────────────────────────────────────────────────────────────────
HINDI_RESPONSES = {
    "greet_morning":   "Suprabhat! Main EchoNova hoon, aapki seva mein hazir hoon.",
    "greet_afternoon": "Namaskar! Dopahar ki shubhkamnayein. Main aapki kya madad kar sakta hoon?",
    "greet_evening":   "Shubh sandhya! Main EchoNova hoon, aapki seva mein hazir hoon.",
    "time":            "Abhi ka samay hai: {time}.",
    "date":            "Aaj ki taareekh hai: {date}.",
    "hello":           "Namaskar! Aap kaise hain? Main aapki kya madad kar sakta hoon?",
    "joke":            "Ek joke suniye: Ek programmer apni patni se bola - Jao bazaar se ek litre doodh lao, aur agar ande mile toh das lana. Patni gayi aur das litre doodh laayi. Kyunki ande mil gaye the!",
    "youtube":         "YouTube aapke liye khol raha hoon.",
    "google":          "Google aapke liye khol raha hoon.",
    "screenshot":      "Screenshot le liya gaya hai aur Pictures folder mein save ho gaya hai.",
    "music_play":      "{song} baja raha hoon.",
    "music_none":      "Aapke Music folder mein koi gaana nahi mila.",
    "wiki_search":     "Wikipedia par khoj raha hoon...",
    "wiki_none":       "Is vishay par kuch nahi mila. Kripya aur spasht karein.",
    "wiki_multi":      "Kai parinaam mile hain. Kripya aur spasht karein.",
    "shutdown":        "System band ho raha hai. Phir milenge!",
    "restart":         "System restart ho raha hai. Thoda rukiye!",
    "exit":            "Alvida! Aapka din shubh ho!",
    "name_ask":        "Aap mujhe kya naam dena chahte hain? Bol dijiye...",
    "name_set":        "Theek hai! Ab se mera naam {name} hoga.",
    "name_fail":       "Maaf kijiye, naam samajh nahi aaya.",
    "not_understood":  "Maaf kijiye, mujhe samajh nahi aaya. Kripya dobara boliye.",
    "no_mic":          "Microphone ka upyog nahi ho sakta.",
    "network_error":   "Network error hai. Kripya internet connection check karein.",
}

ENGLISH_RESPONSES = {
    "greet_morning":   "Good morning! EchoNova at your service.",
    "greet_afternoon": "Good afternoon! How can I help you today?",
    "greet_evening":   "Good evening! EchoNova at your service.",
    "time":            "The current time is {time}.",
    "date":            "Today's date is {date}.",
    "hello":           "Hello sir! How can I assist you today?",
    "joke":            None,
    "youtube":         "Opening YouTube for you, sir.",
    "google":          "Opening Google for you, sir.",
    "screenshot":      "Screenshot saved to your Pictures folder.",
    "music_play":      "Playing {song}.",
    "music_none":      "No songs found in your Music folder.",
    "wiki_search":     "Searching Wikipedia...",
    "wiki_none":       "Couldn't find anything on Wikipedia for that topic.",
    "wiki_multi":      "Multiple results found. Please be more specific.",
    "shutdown":        "Shutting down the system. Goodbye, sir!",
    "restart":         "Restarting the system. Please wait!",
    "exit":            "Going offline. Have a great day, sir!",
    "name_ask":        "What would you like to name me? Listening...",
    "name_set":        "Alright! I'll be called {name} from now on.",
    "name_fail":       "Sorry, I couldn't catch that name.",
    "not_understood":  "Sorry, I'm not sure how to handle that yet.",
    "no_mic":          "Speech recognition unavailable.",
    "network_error":   "Network error. Check your internet connection.",
}


class EchoNovaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ECHONOVA — Desktop Voice Assistant")
        self.root.configure(bg=BG)
        self.root.geometry("950x780")
        self.root.minsize(800, 680)
        self.root.resizable(True, True)

        self.is_listening = False
        self.orb_angle    = 0
        self.orb_pulse    = 0
        self.wave_phase   = 0
        self.particles    = []
        self.lang         = "en"   # "en" or "hi"

        self._build_ui()
        self._animate()
        self._greet()

    # ── Language helpers ──────────────────────────────────────────────────────
    def _r(self, key, **kwargs):
        responses = HINDI_RESPONSES if self.lang == "hi" else ENGLISH_RESPONSES
        text = responses.get(key, "")
        return text.format(**kwargs) if text else ""

    def _toggle_language(self):
        if self.lang == "en":
            self.lang = "hi"
            self.lang_btn.config(text="🇮🇳 हिंदी", fg=ACCENT_HI, highlightbackground=ACCENT_HI)
            self.lang_indicator.config(text="🇮🇳  हिंदी मोड", fg=ACCENT_HI)
            self._speak_and_show("Hindi mode chalu ho gaya! Ab aap Hindi mein bol sakte hain.")
            self._add_log("Hindi mode activated", "ok")
        else:
            self.lang = "en"
            self.lang_btn.config(text="🇬🇧 English", fg=TEXT, highlightbackground=BORDER)
            self.lang_indicator.config(text="🇬🇧  English Mode", fg=TEXT_DIM)
            self._speak_and_show("English mode activated! You can speak in English now.")
            self._add_log("English mode activated", "ok")

    # ── UI Build ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        topbar = tk.Frame(self.root, bg=BG, height=60)
        topbar.pack(fill=tk.X, padx=20, pady=(15, 0))
        topbar.pack_propagate(False)

        logo_frame = tk.Frame(topbar, bg=BG)
        logo_frame.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(logo_frame, text="◈ ECHONOVA", font=("Courier New", 20, "bold"),
                 fg=ACCENT, bg=BG).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(logo_frame, text="DESKTOP VOICE ASSISTANT",
                 font=FONT_SMALL, fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT, pady=(8, 0))

        right_top = tk.Frame(topbar, bg=BG)
        right_top.pack(side=tk.RIGHT, fill=tk.Y, pady=8)

        self.lang_btn = tk.Button(
            right_top, text="🇬🇧 English",
            font=FONT_CMD, fg=TEXT, bg=SURFACE2,
            activeforeground=ACCENT_HI, activebackground=SURFACE,
            bd=0, padx=12, pady=6,
            highlightbackground=BORDER, highlightthickness=1,
            cursor="hand2", command=self._toggle_language)
        self.lang_btn.pack(side=tk.LEFT, padx=(0, 10))

        status_frame = tk.Frame(right_top, bg=SURFACE, bd=0,
                                highlightbackground=BORDER, highlightthickness=1)
        status_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.status_dot = tk.Label(status_frame, text="●", font=("Courier New", 10),
                                   fg=ACCENT3, bg=SURFACE)
        self.status_dot.pack(side=tk.LEFT, padx=(10, 4))
        self.status_label = tk.Label(status_frame, text="ONLINE",
                                     font=FONT_SMALL, fg=TEXT_DIM, bg=SURFACE)
        self.status_label.pack(side=tk.LEFT, padx=(0, 12))

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X, padx=20, pady=(10, 0))

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left = tk.Frame(main, bg=BG, width=320)
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left.pack_propagate(False)

        self.canvas = tk.Canvas(left, width=300, height=280, bg=BG, highlightthickness=0)
        self.canvas.pack(pady=(5, 0))
        self.canvas.bind("<Button-1>", lambda e: self._on_orb_click(e))
        self._init_particles()

        self.orb_label = tk.Label(left, text="[ CLICK ORB TO ACTIVATE ]",
                                  font=FONT_SMALL, fg=TEXT_DIM, bg=BG)
        self.orb_label.pack(pady=(0, 4))

        self.lang_indicator = tk.Label(left, text="🇬🇧  English Mode",
                                       font=FONT_SMALL, fg=TEXT_DIM, bg=BG)
        self.lang_indicator.pack(pady=(0, 6))

        resp_frame = tk.Frame(left, bg=SURFACE, highlightbackground=ACCENT, highlightthickness=1)
        resp_frame.pack(fill=tk.X, padx=4)
        tk.Label(resp_frame, text="◈ ECHONOVA RESPONSE",
                 font=FONT_SMALL, fg=TEXT_DIM, bg=SURFACE,
                 anchor='w').pack(fill=tk.X, padx=10, pady=(8, 0))
        self.response_text = tk.Text(resp_frame, height=5, wrap=tk.WORD,
                                     font=FONT_BODY, fg=TEXT, bg=SURFACE,
                                     bd=0, padx=10, pady=8,
                                     insertbackground=ACCENT,
                                     selectbackground=ACCENT2,
                                     relief=tk.FLAT)
        self.response_text.pack(fill=tk.BOTH, padx=2, pady=(0, 8))
        self.response_text.config(state=tk.DISABLED)

        right = tk.Frame(main, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cmd_header = tk.Frame(right, bg=BG)
        cmd_header.pack(fill=tk.X, pady=(0, 8))
        tk.Label(cmd_header, text="QUICK COMMANDS", font=FONT_SMALL, fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
        tk.Frame(cmd_header, bg=BORDER, height=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), pady=7)

        cmd_grid = tk.Frame(right, bg=BG)
        cmd_grid.pack(fill=tk.X)

        commands = [
            ("🕐  TIME / समय",     "What is the time"),
            ("📅  DATE / तारीख",   "What is the date"),
            ("▶   YOUTUBE",        "Open YouTube"),
            ("🔍  GOOGLE",         "Open Google"),
            ("😄  JOKE / मजाक",    "Tell me a joke"),
            ("🎵  MUSIC / गाना",   "Play music"),
            ("📸  SCREENSHOT",     "Take a screenshot"),
            ("📖  WIKIPEDIA",      "Search Wikipedia about"),
            ("🔄  RESTART",        "Restart"),
            ("⚙   CHANGE NAME",   "Change your name"),
        ]

        for i, (label, cmd) in enumerate(commands):
            row, col = divmod(i, 2)
            btn = tk.Button(cmd_grid, text=label,
                            font=FONT_CMD, fg=TEXT, bg=SURFACE2,
                            activeforeground=ACCENT, activebackground=SURFACE,
                            bd=0, padx=12, pady=10, anchor='w',
                            highlightbackground=BORDER, highlightthickness=1,
                            cursor="hand2",
                            command=lambda c=cmd: self._process_command(c))
            btn.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
            cmd_grid.columnconfigure(col, weight=1)
            self._btn_hover(btn)

        log_header = tk.Frame(right, bg=BG)
        log_header.pack(fill=tk.X, pady=(12, 6))
        tk.Label(log_header, text="ACTIVITY LOG", font=FONT_SMALL, fg=TEXT_DIM, bg=BG).pack(side=tk.LEFT)
        tk.Frame(log_header, bg=BORDER, height=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), pady=7)

        log_outer = tk.Frame(right, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        log_outer.pack(fill=tk.BOTH, expand=True)
        self.log_box = scrolledtext.ScrolledText(
            log_outer, height=8, wrap=tk.WORD,
            font=FONT_MONO_S, fg=TEXT_DIM, bg=SURFACE,
            bd=0, padx=10, pady=8,
            insertbackground=ACCENT, selectbackground=ACCENT2, relief=tk.FLAT)
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.log_box.config(state=tk.DISABLED)
        self.log_box.tag_config("time",   foreground=TEXT_DIM)
        self.log_box.tag_config("user",   foreground="#6699ff")
        self.log_box.tag_config("system", foreground=ACCENT)
        self.log_box.tag_config("error",  foreground=ERROR)
        self.log_box.tag_config("ok",     foreground=ACCENT3)
        self.log_box.tag_config("hindi",  foreground=ACCENT_HI)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X, padx=20)
        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill=tk.X, padx=20, pady=10)

        self.text_input = tk.Entry(bottom, font=FONT_BODY, fg=TEXT, bg=SURFACE2,
                                   insertbackground=ACCENT, bd=0,
                                   highlightbackground=BORDER, highlightthickness=1, relief=tk.FLAT)
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 8))
        self.text_input.insert(0, "Type a command / यहाँ लिखें...")
        self.text_input.config(fg=TEXT_DIM)
        self.text_input.bind("<FocusIn>",  self._on_entry_focus_in)
        self.text_input.bind("<FocusOut>", self._on_entry_focus_out)
        self.text_input.bind("<Return>",   lambda e: self._send_text())

        tk.Button(bottom, text="SEND", font=FONT_CMD, fg=BG, bg=ACCENT,
                  activeforeground=BG, activebackground=ACCENT2,
                  bd=0, padx=18, pady=10, cursor="hand2",
                  command=self._send_text).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(bottom, text="CLEAR LOG", font=FONT_CMD, fg=TEXT_DIM, bg=SURFACE2,
                  activeforeground=ERROR, activebackground=SURFACE,
                  bd=0, padx=14, pady=10,
                  highlightbackground=BORDER, highlightthickness=1,
                  cursor="hand2", command=self._clear_log).pack(side=tk.LEFT)

    # ── Canvas / Animation ────────────────────────────────────────────────────
    def _init_particles(self):
        self.particles = []
        for _ in range(18):
            self.particles.append({
                'angle':  random.uniform(0, 2 * math.pi),
                'radius': random.uniform(90, 130),
                'speed':  random.uniform(0.005, 0.02),
                'size':   random.uniform(1.5, 3.5),
                'alpha':  random.uniform(0.3, 1.0),
            })

    def _animate(self):
        self.orb_angle  = (self.orb_angle + 1) % 360
        self.orb_pulse  = (self.orb_pulse  + 0.05) % (2 * math.pi)
        self.wave_phase = (self.wave_phase + 0.12) % (2 * math.pi)
        for p in self.particles:
            p['angle'] = (p['angle'] + p['speed']) % (2 * math.pi)
        self._draw_orb()
        self.root.after(30, self._animate)

    def _draw_orb(self):
        c = self.canvas
        c.delete("all")
        cx, cy = 150, 140
        orb_accent = ACCENT_HI if self.lang == "hi" else ACCENT

        for gx in range(0, 300, 30):
            for gy in range(0, 280, 30):
                c.create_oval(gx, gy, gx+1, gy+1, fill="#0a1f35", outline="")

        for i, (r, color, dash) in enumerate([
            (120, BORDER,    (4, 6)),
            (100, "#0a2040", (2, 8)),
            (85,  BORDER,    ()),
        ]):
            pulse = 2 * math.sin(self.orb_pulse + i) if self.is_listening else 0
            c.create_oval(cx-r-pulse, cy-r-pulse, cx+r+pulse, cy+r+pulse,
                          outline=color, width=1, dash=dash if dash else None)

        a = math.radians(self.orb_angle)
        for i in range(6):
            ang = a + i * math.pi / 3
            px = cx + 108 * math.cos(ang)
            py = cy + 108 * math.sin(ang)
            c.create_oval(px-3, py-3, px+3, py+3, fill=orb_accent, outline="")

        for p in self.particles:
            px = cx + p['radius'] * math.cos(p['angle'])
            py = cy + p['radius'] * math.sin(p['angle'])
            s = p['size']
            c.create_oval(px-s, py-s, px+s, py+s,
                          fill=orb_accent if random.random() > 0.5 else ACCENT2, outline="")

        if self.is_listening:
            bars, bar_w = 12, 6
            sx = cx - bars * (bar_w + 3) // 2
            for i in range(bars):
                h = 10 + 22 * abs(math.sin(self.wave_phase + i * 0.5))
                bx = sx + i * (bar_w + 3)
                c.create_rectangle(bx, cy - h, bx + bar_w, cy + h, fill=orb_accent, outline="")

        pulse_r = 4 * math.sin(self.orb_pulse)
        for r2, alpha in [(72, 0.08), (65, 0.15), (58, 0.25)]:
            shade = int(alpha * 255)
            color = f"#{shade:02x}{min(shade+40,255):02x}{min(shade+60,255):02x}"
            c.create_oval(cx-r2-pulse_r, cy-r2-pulse_r, cx+r2+pulse_r, cy+r2+pulse_r, fill=color, outline="")

        orb_color = orb_accent if self.is_listening else ACCENT2
        c.create_oval(cx-55, cy-55, cx+55, cy+55, fill=SURFACE, outline=orb_color, width=2)
        c.create_rectangle(cx-7, cy-20, cx+7, cy+10, fill=orb_accent, outline="")
        c.create_arc(cx-14, cy-5, cx+14, cy+25, start=0, extent=180, style=tk.ARC, outline=orb_accent, width=2)
        c.create_line(cx, cy+25, cx, cy+35, fill=orb_accent, width=2)
        c.create_line(cx-8, cy+35, cx+8, cy+35, fill=orb_accent, width=2)

        if self.lang == "hi":
            hint = "● सुन रहा हूँ" if self.is_listening else "बोलने के लिए क्लिक करें"
        else:
            hint = "● LISTENING" if self.is_listening else "CLICK TO SPEAK"
        c.create_text(cx, cy + 60, text=hint, font=FONT_SMALL,
                      fill=orb_accent if self.is_listening else TEXT_DIM)

    def _on_orb_click(self, event):
        cx, cy = 150, 140
        if math.sqrt((event.x - cx)**2 + (event.y - cy)**2) <= 60:
            self._toggle_listening()

    # ── Listening ─────────────────────────────────────────────────────────────
    def _toggle_listening(self):
        if self.is_listening:
            self.is_listening = False
            self.orb_label.config(text="[ CLICK ORB TO ACTIVATE ]", fg=TEXT_DIM)
            self.status_label.config(text="ONLINE")
            self.status_dot.config(fg=ACCENT3)
        else:
            if not SR_AVAILABLE:
                self._add_log("SpeechRecognition not installed.", "error")
                self._set_response("Please install: pip install speechrecognition")
                return
            threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self):
        self.is_listening = True
        calib = "[ CALIBRATING... ]" if self.lang == "en" else "[ तैयार हो रहा हूँ... ]"
        self.root.after(0, lambda: self.orb_label.config(text=calib, fg=TEXT_DIM))
        self.root.after(0, lambda: self.status_label.config(text="CALIBRATING"))
        self.root.after(0, lambda: self.status_dot.config(fg=ACCENT_HI if self.lang == "hi" else ACCENT))

        lang_code = "hi-IN" if self.lang == "hi" else "en-IN"
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8
        r.phrase_threshold = 0.3

        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.8)
                listen_text = "[ LISTENING... ]" if self.lang == "en" else "[ बोलिए... ]"
                self.root.after(0, lambda: self.orb_label.config(
                    text=listen_text, fg=ACCENT_HI if self.lang == "hi" else ACCENT))
                self.root.after(0, lambda: self.status_label.config(text="LISTENING"))
                audio = r.listen(source, timeout=7, phrase_time_limit=10)

            query = r.recognize_google(audio, language=lang_code).lower()
            self.root.after(0, lambda q=query: self._add_log(f"[{lang_code}] {q}", "user"))
            self.root.after(0, lambda q=query: self._process_command(q))

        except sr.WaitTimeoutError:
            msg = "Koi awaaz nahi aayi. Dobara try karein." if self.lang == "hi" else "I didn't hear anything. Please try again."
            self.root.after(0, lambda: self._add_log("Timeout — no speech detected.", "error"))
            self.root.after(0, lambda: self._set_response(msg))
        except sr.UnknownValueError:
            msg = "Samajh nahi aaya. Spasht boliye." if self.lang == "hi" else "Sorry, I couldn't understand that. Speak clearly and try again."
            self.root.after(0, lambda: self._add_log("Could not understand audio.", "error"))
            self.root.after(0, lambda: self._set_response(msg))
        except sr.RequestError as ex:
            self.root.after(0, lambda: self._add_log(f"Network error: {ex}", "error"))
            self.root.after(0, lambda: self._set_response(self._r("network_error")))
        except Exception as ex:
            self.root.after(0, lambda: self._add_log(f"Error: {ex}", "error"))
        finally:
            self.is_listening = False
            self.root.after(0, lambda: self.orb_label.config(text="[ CLICK ORB TO ACTIVATE ]", fg=TEXT_DIM))
            self.root.after(0, lambda: self.status_label.config(text="ONLINE"))
            self.root.after(0, lambda: self.status_dot.config(fg=ACCENT3))

    # ── Command Processing ────────────────────────────────────────────────────
    def _process_command(self, query):
        query = query.strip().lower()
        if not query or "यहाँ लिखें" in query or query == "type a command...":
            return

        self.root.after(0, lambda q=query: self._add_log(q, "user"))

        if any(w in query for w in ["time", "samay", "baj", "kitne baje"]):
            self._cmd_time()
        elif any(w in query for w in ["date", "taareekh", "aaj kya"]):
            self._cmd_date()
        elif any(w in query for w in ["wikipedia", "khojo"]):
            topic = query.replace("wikipedia","").replace("search","").replace("khojo","").strip()
            threading.Thread(target=self._cmd_wikipedia, args=(topic,), daemon=True).start()
        elif any(w in query for w in ["play music", "music", "gaana", "song", "bajao"]):
            song = query.replace("play music","").replace("music","").replace("gaana","").replace("song","").replace("bajao","").strip()
            threading.Thread(target=self._cmd_music, args=(song,), daemon=True).start()
        elif "youtube" in query:
            self._cmd_open("https://youtube.com", "YouTube")
        elif "google" in query:
            self._cmd_open("https://google.com", "Google")
        elif any(w in query for w in ["screenshot", "photo lo"]):
            threading.Thread(target=self._cmd_screenshot, daemon=True).start()
        elif any(w in query for w in ["joke", "hasao", "funny"]):
            self._cmd_joke()
        elif any(w in query for w in ["change your name", "rename", "naam badlo"]):
            threading.Thread(target=self._cmd_set_name, daemon=True).start()
        elif any(w in query for w in ["shutdown", "band karo"]):
            self._cmd_shutdown()
        elif any(w in query for w in ["restart", "dobara chalu"]):
            self._cmd_restart()
        elif any(w in query for w in ["exit", "offline", "bye", "alvida", "band ho"]):
            self._cmd_exit()
        elif any(w in query for w in ["hello", "hi", "namaskar", "namaste"]):
            self._speak_and_show(self._r("hello"))
        else:
            if self.lang == "hi":
                self._speak_and_show(f'Maaf kijiye, "{query}" samajh nahi aaya.')
            else:
                self._speak_and_show(f'I heard: "{query}". I\'m not sure how to handle that yet.')

    def _cmd_time(self):
        t = datetime.datetime.now().strftime("%I:%M:%S %p")
        self._speak_and_show(self._r("time", time=t))

    def _cmd_date(self):
        now = datetime.datetime.now()
        if self.lang == "hi":
            days_hi = ["Somvaar","Mangalvaar","Budhvaar","Guruvaar","Shukravaar","Shanivaar","Ravivaar"]
            months_hi = ["January","February","March","April","May","June","July","August","September","October","November","December"]
            d = f"{days_hi[now.weekday()]}, {now.day} {months_hi[now.month-1]} {now.year}"
        else:
            d = now.strftime("%A, %d %B %Y")
        self._speak_and_show(self._r("date", date=d))

    def _cmd_wikipedia(self, topic):
        if not topic:
            msg = "Kaunsa topic search karoon?" if self.lang == "hi" else "What topic should I search on Wikipedia?"
            self.root.after(0, lambda: self._speak_and_show(msg))
            return
        if not WIKI_AVAILABLE:
            self.root.after(0, lambda: self._speak_and_show("pip install wikipedia"))
            return
        try:
            self.root.after(0, lambda: self._set_response(self._r("wiki_search")))
            wikipedia.set_lang("hi" if self.lang == "hi" else "en")
            result = wikipedia.summary(topic, sentences=3)
            self.root.after(0, lambda r=result: self._speak_and_show(r))
        except wikipedia.exceptions.DisambiguationError:
            self.root.after(0, lambda: self._speak_and_show(self._r("wiki_multi")))
        except Exception:
            self.root.after(0, lambda: self._speak_and_show(self._r("wiki_none")))

    def _cmd_music(self, song_name):
        song_dir = os.path.expanduser("~/Music")
        try:
            songs = [s for s in os.listdir(song_dir)
                     if s.lower().endswith(('.mp3','.wav','.m4a','.flac','.ogg'))]
        except Exception:
            msg = "Music folder nahi mila." if self.lang == "hi" else "Could not access Music folder."
            self.root.after(0, lambda: self._speak_and_show(msg))
            return
        if song_name:
            songs = [s for s in songs if song_name.lower() in s.lower()]
        if songs:
            song = random.choice(songs)
            try:
                os.startfile(os.path.join(song_dir, song))
            except AttributeError:
                import subprocess
                subprocess.Popen(['xdg-open', os.path.join(song_dir, song)])
            self.root.after(0, lambda s=song: self._speak_and_show(self._r("music_play", song=s)))
        else:
            self.root.after(0, lambda: self._speak_and_show(self._r("music_none")))

    def _cmd_open(self, url, name):
        if WEB_AVAILABLE:
            wb.open(url)
            key = "youtube" if "youtube" in url else "google"
            self._speak_and_show(self._r(key))
        else:
            self._speak_and_show("Webbrowser module unavailable.")

    def _cmd_screenshot(self):
        if not PYAUTOGUI_AVAILABLE:
            self.root.after(0, lambda: self._speak_and_show("pip install pyautogui"))
            return
        img = pyautogui.screenshot()
        path = os.path.expanduser("~/Pictures/echonova_screenshot.png")
        img.save(path)
        self.root.after(0, lambda: self._speak_and_show(self._r("screenshot")))

    def _cmd_joke(self):
        if self.lang == "hi":
            self._speak_and_show(self._r("joke"))
        else:
            if JOKES_AVAILABLE:
                joke = pyjokes.get_joke()
            else:
                jokes = [
                    "Why do programmers prefer dark mode? Because light attracts bugs!",
                    "How many programmers to change a bulb? None — that's a hardware problem.",
                    "I told my computer I needed a break. Now it sends Kit-Kat ads.",
                ]
                joke = random.choice(jokes)
            self._speak_and_show(joke)

    def _cmd_set_name(self):
        self.root.after(0, lambda: self._speak_and_show(self._r("name_ask")))
        if SR_AVAILABLE:
            r = sr.Recognizer()
            lang_code = "hi-IN" if self.lang == "hi" else "en-IN"
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, timeout=5)
                name = r.recognize_google(audio, language=lang_code)
                with open("assistant_name.txt", "w") as f:
                    f.write(name)
                self.root.after(0, lambda n=name: self._speak_and_show(self._r("name_set", name=n)))
            except Exception:
                self.root.after(0, lambda: self._speak_and_show(self._r("name_fail")))
        else:
            self.root.after(0, lambda: self._speak_and_show(self._r("no_mic")))

    def _cmd_shutdown(self):
        self._speak_and_show(self._r("shutdown"))
        self.root.after(2000, lambda: os.system("shutdown /s /f /t 1"))

    def _cmd_restart(self):
        self._speak_and_show(self._r("restart"))
        self.root.after(2000, lambda: os.system("shutdown /r /f /t 1"))

    def _cmd_exit(self):
        self._speak_and_show(self._r("exit"))
        self.root.after(2000, self.root.destroy)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _speak_and_show(self, text):
        self._set_response(text)
        tag = "hindi" if self.lang == "hi" else "system"
        self._add_log(text, tag)
        if TTS_AVAILABLE:
            threading.Thread(target=self._tts, args=(text,), daemon=True).start()

    def _tts(self, text):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if self.lang == "hi":
                hindi_voice = None
                for v in voices:
                    if "hindi" in v.name.lower() or "hi_in" in v.id.lower():
                        hindi_voice = v.id
                        break
                if hindi_voice:
                    engine.setProperty('voice', hindi_voice)
                elif voices and len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)
            else:
                if voices and len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)
            engine.setProperty('rate', 145)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception:
            pass

    def _set_response(self, text):
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert(tk.END, text)
        self.response_text.config(state=tk.DISABLED)

    def _add_log(self, msg, tag="system"):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = {"user":"YOU","system":"NOVA","error":"ERR","ok":"OK","hindi":"नोवा"}.get(tag,"SYS")
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, f"[{t}] ", "time")
        self.log_box.insert(tk.END, f"[{prefix}] ", tag)
        self.log_box.insert(tk.END, f"{msg}\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state=tk.DISABLED)
        self._add_log("Log cleared.", "ok")

    def _send_text(self):
        text = self.text_input.get().strip()
        if text and "यहाँ लिखें" not in text and text != "Type a command...":
            self.text_input.delete(0, tk.END)
            self._process_command(text)

    def _greet(self):
        h = datetime.datetime.now().hour
        key = "greet_morning" if 4 <= h < 12 else "greet_afternoon" if 12 <= h < 16 else "greet_evening"
        name = "EchoNova"
        try:
            with open("assistant_name.txt") as f:
                name = f.read().strip()
        except FileNotFoundError:
            pass
        msg = self._r(key)
        self.root.after(500, lambda: self._speak_and_show(msg))

    def _btn_hover(self, btn):
        btn.bind("<Enter>", lambda e: btn.config(fg=ACCENT, bg=SURFACE, highlightbackground=ACCENT))
        btn.bind("<Leave>", lambda e: btn.config(fg=TEXT,   bg=SURFACE2, highlightbackground=BORDER))

    def _on_entry_focus_in(self, event):
        current = self.text_input.get()
        if "यहाँ लिखें" in current or current == "Type a command...":
            self.text_input.delete(0, tk.END)
            self.text_input.config(fg=TEXT)

    def _on_entry_focus_out(self, event):
        if not self.text_input.get():
            self.text_input.insert(0, "Type a command / यहाँ लिखें...")
            self.text_input.config(fg=TEXT_DIM)


# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = EchoNovaApp(root)
    root.mainloop()
