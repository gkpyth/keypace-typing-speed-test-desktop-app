import customtkinter as ctk
import tkinter as tk

from logic import get_random_text, calculate_wpm, load_leaderboard, save_score

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Globals
durations = [("1:00", 60), ("2:00", 120), ("3:00", 180), ("4:00", 240), ("5:00", 300)]

# Color Palettes ─────────────────────────────────────────────────────────────────
DARK = {
    "bg_main":         "#2B2D42",   # Main background
    "bg_frame":        "#3D3F5A",   # Card/frame background
    "text_primary":    "#D4C5A9",   # Body text
    "accent":          "#F4A261",   # Coral accent (titles, highlights)
    "accent_hover":    "#7B6FA0",   # Hover state for most buttons
    "border":          "#C9B8E8",   # Lavender border/input
    "correct":         "#A8C5A0",   # Sage green — correct character
    "incorrect":       "#C47C7C",   # Muted red — incorrect character
    "incorrect_hover": "#A85C5C",   # Darker red hover (Quit button)
    "text_on_accent":  "#2B2D42",   # Dark text on light/accent backgrounds
    "saved_btn":       "#555555",   # Disabled saved button color
    "passage_bg":      "#3D3F5A",   # tk.Text widget background
    "passage_fg":      "#D4C5A9",   # tk.Text widget foreground
}

LIGHT = {
    "bg_main":         "#F0EBE3",   # Main background
    "bg_frame":        "#DDD5C8",   # Card/frame background
    "text_primary":    "#3D3F5A",   # Body text
    "accent":          "#E07A3E",   # Slightly darker coral for readability on light bg
    "accent_hover":    "#B5611A",   # Hover state for most buttons
    "border":          "#9B8BC8",   # Slightly darker lavender border
    "correct":         "#4A7A42",   # Darker sage green for light background
    "incorrect":       "#C47C7C",   # Same muted red
    "incorrect_hover": "#A85C5C",   # Same darker red hover
    "text_on_accent":  "#FFFFFF",   # White text on accent backgrounds
    "saved_btn":       "#AAAAAA",   # Disabled saved button color
    "passage_bg":      "#DDD5C8",   # tk.Text widget background
    "passage_fg":      "#3D3F5A",   # tk.Text widget foreground
}

# Active palette — starts on dark mode
C = DARK


class TypingSpeedApp(ctk.CTk):
    def __init__(self):
        """Initialize the application window."""
        super().__init__()
        self.title("KeyPace")
        self.geometry("1300x800")
        self.resizable(False, False)
        self.current_state = "welcome"                  # values: "welcome", "active", "results"
        self.displayed_text = None
        self.selected_timer = 60                        # In seconds
        self.timer_on = False
        self.time_elapsed_sec = 0                       # In seconds
        self.timer_job = None
        self.final_wpm = 0
        self.final_accuracy = 0
        self.final_duration = 0
        self.duration_buttons = {}                      # Dictionary to store duration toggle buttons
        self.current_char_index = 0                     # Index of the current character being typed
        self.correct_char_count = 0                     # Count of correct characters
        self.correct_chars_log = []                     # List to store correct characters
        self.chunk_offset = 0
        self.chars_per_chunk = 300
        self.build_ui()
        self.show_welcome()

    # Add this method to handle the theme switch button click
    def toggle_theme(self):
        """Toggle between light and dark mode by switching the active color palette."""
        global C
        # Switch palette based on switch value
        if self.theme_switch.get() == "light":
            C = LIGHT
            ctk.set_appearance_mode("light")
        else:
            C = DARK
            ctk.set_appearance_mode("dark")

        # Top bar ───────────────────────────────────────────────────────────────
        self.top_bar_frame.configure(fg_color=C["bg_main"])
        self.title_label.configure(text_color=C["accent"])
        self.leaderboard_btn.configure(hover_color=C["accent_hover"])

        # Welcome frame ─────────────────────────────────────────────────────────
        self.welcome_frame.configure(fg_color=C["bg_main"])
        self.welcome_container.configure(fg_color="transparent")
        self.instructions_frame.configure(fg_color=C["bg_frame"])
        self.instructions_title_label.configure(text_color=C["text_primary"])
        self.instructions_text_label.configure(text_color=C["text_primary"])
        self.duration_toggles_frame.configure(fg_color="transparent")
        for btn in self.duration_buttons.values():
            btn.configure(fg_color=C["bg_frame"], hover_color=C["accent_hover"],
                          text_color=C["text_primary"])
        self.start_btn.configure(fg_color=C["accent"], hover_color=C["accent_hover"],
                                 text_color=C["text_on_accent"])

        # Active frame ──────────────────────────────────────────────────────────
        self.active_frame.configure(fg_color=C["bg_main"])
        self.active_container.configure(fg_color="transparent")
        self.sample_text_frame.configure(fg_color=C["bg_frame"])
        self.sample_title_row.configure(fg_color="transparent")
        self.sample_title_label.configure(text_color=C["text_primary"])
        self.refresh_btn.configure(hover_color=C["accent_hover"], text_color=C["accent"])
        self.passage_text.configure(bg=C["passage_bg"], fg=C["passage_fg"])
        self.passage_text.tag_config("correct", foreground=C["correct"])
        self.passage_text.tag_config("incorrect", foreground=C["incorrect"])
        self.stats_frame.configure(fg_color=C["bg_frame"])
        self.timer_label.configure(text_color=C["accent"])
        self.wpm_label.configure(text_color=C["text_primary"])
        self.accuracy_label.configure(text_color=C["text_primary"])
        self.cancel_btn.configure(hover_color=C["accent_hover"], text_color=C["text_primary"])

        # Results frame ─────────────────────────────────────────────────────────
        self.results_frame.configure(fg_color=C["bg_main"])
        self.results_container.configure(fg_color="transparent")
        self.score_box.configure(fg_color=C["bg_frame"])
        self.results_title_label.configure(text_color=C["text_primary"])
        self.results_wpm_label.configure(text_color=C["accent"])
        self.results_accuracy_label.configure(text_color=C["text_primary"])
        self.results_time_label.configure(text_color=C["text_primary"])
        self.results_divider.configure(fg_color=C["bg_frame"])
        self.initials_label.configure(text_color=C["text_primary"])
        self.initials_entry.configure(fg_color=C["bg_main"], border_color=C["border"],
                                      text_color=C["text_primary"])
        self.submit_score_btn.configure(fg_color=C["correct"], hover_color=C["accent_hover"],
                                        text_color=C["text_on_accent"])
        self.quit_retry_btns.configure(fg_color="transparent")
        self.quit_btn.configure(fg_color=C["incorrect"], hover_color=C["incorrect_hover"],
                                text_color=C["text_on_accent"])
        self.try_again_btn.configure(fg_color=C["accent"], hover_color=C["accent_hover"],
                                     text_color=C["text_on_accent"])

    # Add this method to open the leaderboard
    def show_leaderboard(self):
        """Show the leaderboard."""
        top = ctk.CTkToplevel(self)
        top.after(10, lambda: top.focus())
        top.title("Leaderboard")
        top.geometry("400x600")
        top.resizable(False, False)
        top.configure(fg_color=C["bg_main"])
        top.grab_set()

        # Title label
        ctk.CTkLabel(top, text="🏆 Leaderboard", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=C["accent"]).pack(pady=20)

        # Header row
        header_frame = ctk.CTkFrame(top, fg_color=C["bg_frame"], corner_radius=8)
        header_frame.pack(fill="x", padx=20, pady=(0, 5))
        for col, text in enumerate(["Rank", "Initials", "WPM", "Accuracy", "Time"]):
            ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=C["accent"]).grid(row=0, column=col, padx=10, pady=8)
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Score rows
        scores = load_leaderboard()
        if not scores:
            ctk.CTkLabel(top, text="No scores yet!", font=ctk.CTkFont(size=20),
                         text_color=C["text_primary"]).pack(pady=20)
        else:
            for i, entry in enumerate(scores):
                row_frame = ctk.CTkFrame(top, fg_color=C["bg_frame"] if i % 2 == 0 else C["bg_main"],
                                         corner_radius=8)
                row_frame.pack(fill="x", padx=20, pady=2)
                row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
                for col, value in enumerate(
                        [i + 1, entry["initials"], entry["wpm"], f"{entry['accuracy']}%", entry["duration"]]):
                    ctk.CTkLabel(row_frame, text=str(value), font=ctk.CTkFont(size=13),
                                 text_color=C["text_primary"]).grid(row=0, column=col, padx=10, pady=6)

    # Add this method to handle the duration toggle button click
    def set_duration(self, seconds):
        """Set the duration of the typing test."""
        self.selected_timer = seconds
        for s, btn in self.duration_buttons.items():
            if s == seconds:
                btn.configure(fg_color=C["accent"], text_color=C["text_on_accent"])
            else:
                btn.configure(fg_color=C["bg_frame"], text_color=C["text_primary"])

    def start_test(self):
        """Start the typing test."""
        max_chars = self.selected_timer * 8

        # Normalize displayed text to remove any special characters
        self.displayed_text = (get_random_text()[:max_chars]
                               .replace("\u2018", "'")  # left single quote '
                               .replace("\u2019", "'")  # right single quote '
                               .replace("\u201c", '"')  # left double quote "
                               .replace("\u201d", '"')  # right double quote "
                               .replace("\u2014", "-")  # em dash —
                               .replace("\u2013", "-")  # en dash –
                               )

        # Reset all state
        self.time_elapsed_sec = 0
        self.timer_on = False
        self.current_char_index = 0
        self.correct_char_count = 0
        self.correct_chars_log = []

        # Reset passage text and chunk offset
        self.chunk_offset = 0
        self.load_chunk(0)

        # Reset stat labels
        self.timer_label.configure(text="⏱ 0:00")
        self.wpm_label.configure(text="💬 0 WPM")
        self.accuracy_label.configure(text="🎯 0%")

        # Bind keys to window and switch state
        self.bind("<Key>", self.on_key)
        self.show_active()

    def end_test(self):
        """End the typing test."""
        self.after_cancel(self.timer_job)
        self.timer_on = False
        self.final_wpm = round(calculate_wpm(self.current_char_index, self.time_elapsed_sec))
        self.final_accuracy = round(
            (self.correct_char_count / self.current_char_index) * 100) if self.current_char_index > 0 else 0
        minutes = self.time_elapsed_sec // 60
        seconds = self.time_elapsed_sec % 60
        self.final_duration = f"{minutes}:{seconds:02d}"
        self.results_wpm_label.configure(text=f"WPM: {self.final_wpm}")
        self.results_accuracy_label.configure(text=f"🎯 {self.final_accuracy}%")
        self.results_time_label.configure(text=f"Time: {self.final_duration}")
        self.unbind("<Key>")
        self.show_results()

    def cancel_test(self):
        """Cancel the typing test."""
        if not self.timer_on:
            self.show_welcome()
        else:
            self.end_test()

    def submit_score(self):
        """Submit the score to the leaderboard."""
        initials = self.initials_entry.get().strip().upper()

        if initials:
            save_score(initials, self.final_wpm, self.final_accuracy, duration=self.final_duration)
            self.initials_entry.delete(0, "end")
            self.initials_entry.configure(border_color=C["border"])
            self.submit_score_btn.configure(text="✓ Saved!", state="disabled", fg_color=C["saved_btn"])
            self.after(2000, lambda: self.submit_score_btn.configure(text="Save to Leaderboard", state="normal",
                                                                     fg_color=C["correct"]))
            self.show_leaderboard()
        else:
            self.initials_entry.configure(border_color=C["incorrect"])
            self.initials_entry.delete(0, "end")

    def reset_initials_entry(self, event):
        """Reset the initials entry border color when user clicks on it."""
        self.initials_entry.configure(border_color=C["border"])

    def refresh_text(self):
        """Refresh the displayed text."""
        max_chars = self.selected_timer * 8
        self.displayed_text = (get_random_text()[:max_chars]
                               .replace("\u2018", "'")  # left single quote '
                               .replace("\u2019", "'")  # right single quote '
                               .replace("\u201c", '"')  # left double quote "
                               .replace("\u201d", '"')  # right double quote "
                               .replace("\u2014", "-")  # em dash —
                               .replace("\u2013", "-")  # en dash –
                               )
        self.chunk_offset = 0
        self.load_chunk(0)

    def get_chunk(self, start):
        """Return a chunk of text starting at 'start' that fits ~4 lines, ending at a word boundary."""
        target_length = self.chars_per_chunk
        end = start + target_length

        if end >= len(self.displayed_text):
            return self.displayed_text[start:]

        # Walk back from target end until we hit a space (word boundary)
        while end > start and self.displayed_text[end] != " ":
            end -= 1

        return self.displayed_text[start:end]

    def load_chunk(self, start):
        """Load a chunk of text into the passage Text widget starting at character index 'start'."""
        self.chunk_offset = start
        chunk = self.get_chunk(start)
        self.passage_text.configure(state="normal")
        self.passage_text.delete("1.0", "end")
        self.passage_text.insert("1.0", chunk)

        # Re-apply tags for characters already typed within this chunk
        for i in range(start, min(self.current_char_index, start + len(chunk))):
            widget_pos = i - start
            pos = f"1.{widget_pos}"
            was_correct = self.correct_chars_log[i] if i < len(self.correct_chars_log) else False
            tag = "correct" if was_correct else "incorrect"
            self.passage_text.tag_add(tag, pos, f"{pos}+1c")

        self.passage_text.configure(state="disabled")

    def tick_timer(self):
        """A recursive function to update the timer label every second."""
        self.time_elapsed_sec += 1
        remaining = self.selected_timer - self.time_elapsed_sec
        minutes = remaining // 60
        seconds = remaining % 60
        self.timer_label.configure(text=f"⏱ {minutes}:{seconds:02d}")

        if remaining <= 0:
            self.end_test()
        else:
            self.timer_job = self.after(1000, self.tick_timer)

    def on_key(self, event):
        """Handle each keypress during the test."""
        # Ignore if not in active state
        if self.current_state != "active":
            return

        # Start timer on first real character
        if not self.timer_on and len(event.char) == 1:
            self.timer_on = True
            self.tick_timer()

        # Handle backspace key
        if event.keysym == "BackSpace":
            if self.current_char_index > 0:
                self.current_char_index -= 1
                was_correct = self.correct_chars_log.pop()
                if was_correct:
                    self.correct_char_count -= 1

                # Convert index to Text widget position
                pos = f"1.{self.current_char_index - self.chunk_offset}"        # Remove any tag from that character
                self.passage_text.configure(state="normal")
                self.passage_text.tag_remove("correct", pos, f"{pos}+1c")
                self.passage_text.tag_remove("incorrect", pos, f"{pos}+1c")
                self.passage_text.configure(state="disabled")

                # Convert index to Text widget position
                pos = f"1.{self.current_char_index - self.chunk_offset}"
                self.passage_text.configure(state="normal")
                self.passage_text.tag_remove("correct", pos, f"{pos}+1c")
                self.passage_text.tag_remove("incorrect", pos, f"{pos}+1c")
                # Move current position underline back
                self.passage_text.tag_remove("current", "1.0", "end")
                self.passage_text.tag_add("current", pos, f"{pos}+1c")
                self.passage_text.configure(state="disabled")

            return

        # Ignore non-printable characters (shift, ctrl, etc.)
        if len(event.char) != 1:
            return

        # Don't go beyond the end of the passage
        if self.current_char_index >= len(self.displayed_text):
            return

        # Compare typed character to expected character
        expected = self.displayed_text[self.current_char_index]
        typed = event.char
        if typed == expected:
            tag = "correct"
            self.correct_char_count += 1
            self.correct_chars_log.append(True)
        else:
            tag = "incorrect"
            self.correct_chars_log.append(False)

        # Apply tag to the character at current position
        pos = f"1.{self.current_char_index - self.chunk_offset}"
        self.passage_text.configure(state="normal")
        self.passage_text.tag_add(tag, pos, f"{pos}+1c")
        self.passage_text.configure(state="disabled")

        self.current_char_index += 1

        # Move current position underline to next character
        self.passage_text.configure(state="normal")
        self.passage_text.tag_remove("current", "1.0", "end")
        cur_pos = f"1.{self.current_char_index - self.chunk_offset}"
        self.passage_text.tag_add("current", cur_pos, f"{cur_pos}+1c")
        self.passage_text.configure(state="disabled")

        # Detect if user has moved past line 1 using the widget's actual geometry
        widget_pos = self.current_char_index - self.chunk_offset
        try:
            # Get pixel y-coordinate of line 1 and its height
            first_dline = self.passage_text.dlineinfo("1.0")
            if first_dline:
                line1_y = first_dline[1]
                line1_height = first_dline[3]
                # Find the first character of visual line 2
                line2_char = self.passage_text.index(f"@0,{line1_y + line1_height + 1}")
                line2_pos = int(line2_char.split(".")[1])
                # If current position has reached or passed line 2, shift the window
                if widget_pos >= line2_pos and line2_pos > 0:
                    new_offset = self.chunk_offset + line2_pos
                    if new_offset < len(self.displayed_text):
                        self.load_chunk(new_offset)
        except Exception:
            pass

        # Update live WPM and accuracy
        self.update_stats()

    def update_stats(self):
        """Update the WPM and accuracy labels based on the current passage."""
        if self.time_elapsed_sec > 0:
            wpm = calculate_wpm(self.current_char_index, self.time_elapsed_sec)
            self.wpm_label.configure(text=f"💬 {round(wpm)} WPM")

        if self.current_char_index > 0:
            accuracy = (self.correct_char_count / self.current_char_index) * 100
            self.accuracy_label.configure(text=f"🎯 {round(accuracy)}%")

    def build_ui(self):
        """Build the user interface."""
        # Top bar frame with title and trophy button and dark/light mode toggle
        self.top_bar_frame = ctk.CTkFrame(self, height=60, fg_color=C["bg_main"], corner_radius=0)
        self.top_bar_frame.pack(fill="x", side="top", ipady=10)
        self.top_bar_frame.pack_propagate(False)

        # Add & pack title label
        self.title_label = ctk.CTkLabel(self.top_bar_frame, text="KeyPace",
                                        font=ctk.CTkFont(family="Calibri", size=40, weight="bold", slant="italic"),
                                        text_color=C["accent"])
        self.title_label.pack(side="left", padx=80)

        # Right-side container frame to hold Trophy button and dark/light mode toggle button
        self.top_bar_right = ctk.CTkFrame(self.top_bar_frame, fg_color="transparent")
        self.top_bar_right.pack(side="right", padx=25)

        # Add & pack dark/light mode toggle switch button inside right-side container frame
        self.theme_switch = ctk.CTkSwitch(self.top_bar_right, text="", command=self.toggle_theme,
                                          onvalue="light", offvalue="dark")
        self.theme_switch.pack(side="right", padx=0)

        # Add & pack trophy button inside right-side container frame
        self.leaderboard_btn = ctk.CTkButton(self.top_bar_right, text="🏆", width=45, height=35,
                                             font=ctk.CTkFont(size=20), fg_color="transparent", text_color=C["accent"],
                                             hover_color=C["accent_hover"], command=self.show_leaderboard)
        self.leaderboard_btn.pack(side="right", padx=(0, 5))

        # Welcome frame
        self.welcome_frame = ctk.CTkFrame(self, fg_color=C["bg_main"])
        # Call the build_welcome_frame method to build the welcome frame
        self.build_welcome_frame()

        # Active frame
        self.active_frame = ctk.CTkFrame(self, fg_color=C["bg_main"])
        # Call the build_active_frame method to build the active frame
        self.build_active_frame()

        # Results frame
        self.results_frame = ctk.CTkFrame(self, fg_color=C["bg_main"])
        self.build_results_frame()

    def build_welcome_frame(self):
        """Build the welcome frame with instructions, duration toggles, refresh text button, and start button."""
        # Container frame for centering the welcome frame
        self.welcome_container = ctk.CTkFrame(self.welcome_frame, fg_color="transparent", width=640)
        self.welcome_container.pack(pady=20)

        # Instructions frame
        self.instructions_frame = ctk.CTkFrame(self.welcome_container, fg_color=C["bg_frame"], width=640, height=400,
                                               corner_radius=15)
        self.instructions_frame.pack(pady=20)
        self.instructions_frame.pack_propagate(False)
        self.instructions_title_label = ctk.CTkLabel(self.instructions_frame, text="Welcome to KeyPace!",
                                              font=ctk.CTkFont(size=26, weight="bold"), text_color=C["text_primary"])
        self.instructions_text_label = ctk.CTkLabel(self.instructions_frame,
                                                    text="KeyPace measures your typing speed and accuracy in real time."
                                                         "\n\nSelect a duration, read the passage, and start typing - "
                                                         "the timer begins with your first keystroke.\n\nWhen the time "
                                                         "runs out, your results will be displayed.\n\nAverage: 40 WPM "
                                                         "· Good: 60 WPM · Excellent: 80+ WPM",
                                                    font=ctk.CTkFont(size=20, weight="normal"),
                                                    text_color=C["text_primary"],
                                                    anchor="w", justify="left", wraplength=570)
        self.instructions_title_label.pack(pady=40)
        self.instructions_text_label.pack(pady=20, padx=35, fill="x")

        # Duration toggles and refresh frame
        self.duration_toggles_frame = ctk.CTkFrame(self.welcome_container, fg_color="transparent", width=640,
                                                   height=60, corner_radius=15)
        self.duration_toggles_frame.pack(pady=0, padx=0, fill="x")

        # Add duration toggle buttons with a loop starting at the edge of the frame
        for label, seconds in durations:
            btn = ctk.CTkButton(
                self.duration_toggles_frame,
                text=label,
                width=80,
                height=35,
                fg_color=C["bg_frame"],
                hover_color=C["accent_hover"],
                text_color=C["text_primary"],
                corner_radius=8,
                command=lambda s=seconds: self.set_duration(s)
            )
            btn.pack(side="left", padx=30)
            self.duration_buttons[seconds] = btn

        # Add start button under the duration toggle frame
        self.start_btn = ctk.CTkButton(
            self.welcome_container,
            text="Start",
            width=200,
            height=45,
            fg_color=C["accent"],
            hover_color=C["accent_hover"],
            text_color=C["text_on_accent"],
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_test
        )
        self.start_btn.pack(pady=20)

    def build_active_frame(self):
        """Build the active frame with the passage text, real-time results, and timer."""
        self.active_container = ctk.CTkFrame(self.active_frame, fg_color="transparent", width=640)
        self.active_container.pack(pady=20)

        # Sample text frame
        self.sample_text_frame = ctk.CTkFrame(self.active_container, fg_color=C["bg_frame"],
                                              width=640, height=400, corner_radius=15)
        self.sample_text_frame.pack(pady=20)
        self.sample_text_frame.pack_propagate(False)

        # Title row with refresh button
        self.sample_title_row = ctk.CTkFrame(self.sample_text_frame, fg_color="transparent")
        self.sample_title_row.pack(fill="x", padx=35, pady=(15, 5))
        self.sample_title_label = ctk.CTkLabel(self.sample_title_row, text="Typing Passage",
                                               font=ctk.CTkFont(size=20, weight="bold"),
                                               text_color=C["text_primary"])
        self.sample_title_label.pack(side="left")
        self.refresh_btn = ctk.CTkButton(self.sample_title_row, text="⟳", width=35, height=30,
                                         fg_color="transparent", hover_color=C["accent_hover"],
                                         text_color=C["accent"], font=ctk.CTkFont(size=18),
                                         corner_radius=8, command=self.refresh_text)
        self.refresh_btn.pack(side="right")

        # Text widget to display the passage
        # tk.Text is used here instead of CTkLabel because it supports character-level color tags
        self.passage_text = tk.Text(
            self.sample_text_frame,
            wrap="word",                        # wraps at word boundaries, not mid-word
            font=("Segoe UI", 45, "bold"),
            bg=C["passage_bg"],
            fg=C["passage_fg"],
            bd=0,                               # no border
            highlightthickness=0,
            relief="flat",                      # flat appearance
            padx=35,
            pady=10,
            spacing2=6,                         # extra spacing between wrapped lines
            cursor="arrow",                     # no text cursor shown
            state="disabled"                    # read-only — user cannot click and type into it
        )
        self.passage_text.pack(fill="both", expand=True, padx=0, pady=(0, 15))

        # Define color tags for correct and incorrect characters
        self.passage_text.tag_config("correct", foreground=C["correct"])
        self.passage_text.tag_config("incorrect", foreground=C["incorrect"])
        self.passage_text.tag_config("current", underline=True)             # underline current position

        # Stats frame
        self.stats_frame = ctk.CTkFrame(self.active_container, fg_color=C["bg_frame"],
                                        width=640, height=60, corner_radius=15)
        self.stats_frame.pack(pady=(0, 20), fill="x")
        self.stats_frame.pack_propagate(False)
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.timer_label = ctk.CTkLabel(self.stats_frame, text="⏱ 0:00",
                                        font=ctk.CTkFont(size=20, weight="bold"), text_color=C["accent"])
        self.timer_label.grid(row=0, column=0, padx=20, pady=10)
        self.wpm_label = ctk.CTkLabel(self.stats_frame, text="💬 0 WPM",
                                      font=ctk.CTkFont(size=20, weight="bold"), text_color=C["text_primary"])
        self.wpm_label.grid(row=0, column=1, padx=20, pady=10)
        self.accuracy_label = ctk.CTkLabel(self.stats_frame, text="🎯 0%",
                                           font=ctk.CTkFont(size=20, weight="bold"), text_color=C["text_primary"])
        self.accuracy_label.grid(row=0, column=2, padx=20, pady=10)

        # Cancel button
        self.cancel_btn = ctk.CTkButton(self.active_container, text="Cancel", width=200, height=45,
                                        fg_color="transparent", hover_color=C["accent_hover"],
                                        text_color=C["text_primary"], corner_radius=10,
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        command=self.cancel_test)
        self.cancel_btn.pack(pady=10)

    def build_results_frame(self):
        """Build the results frame with the user's score and initials input field."""
        # Container frame for centering the results frame
        self.results_container = ctk.CTkFrame(self.results_frame, fg_color="transparent", width=640)
        self.results_container.pack(pady=20)

        # Score frame containing the user's score, accuracy, and time
        self.score_box = ctk.CTkFrame(self.results_container, fg_color=C["bg_frame"], width=640, height=500,
                                      corner_radius=15)
        self.score_box.pack(pady=20)
        self.score_box.pack_propagate(False)

        # Add & pack title label
        self.results_title_label = ctk.CTkLabel(self.score_box, text="YOUR RESULTS",
                                                font=ctk.CTkFont(size=24, weight="bold"),
                                                text_color=C["text_primary"])
        self.results_title_label.pack(pady=25)

        # Add & pack wpm score label
        self.results_wpm_label = ctk.CTkLabel(self.score_box, text="WPM: ",
                                              font=ctk.CTkFont(size=48, weight="bold"),
                                              text_color=C["accent"])
        self.results_wpm_label.pack(pady=15)

        # Add & pack accuracy score label
        self.results_accuracy_label = ctk.CTkLabel(self.score_box, text="Accuracy: 0%",
                                                   font=ctk.CTkFont(size=20),
                                                   text_color=C["text_primary"])
        self.results_accuracy_label.pack(pady=15)

        # Add & pack time label
        self.results_time_label = ctk.CTkLabel(self.score_box, text="Time: 0:00",
                                               font=ctk.CTkFont(size=20),
                                               text_color=C["text_primary"])
        self.results_time_label.pack(pady=15)

        # Add & pack horizontal divider
        self.results_divider = ctk.CTkLabel(self.score_box, text="─────────────────────",
                                            fg_color=C["bg_frame"], width=640, height=0, corner_radius=15)
        self.results_divider.pack(pady=10)

        # Add & pack initials label
        self.initials_label = ctk.CTkLabel(self.score_box, text="Enter your initials:",
                                           font=ctk.CTkFont(size=14),
                                           text_color=C["text_primary"])
        self.initials_label.pack(pady=10)

        # Add & pack initials input field
        self.initials_entry = ctk.CTkEntry(self.score_box, width=180, height=40, placeholder_text="e.g. 'AKW'",
                                           fg_color=C["bg_main"], border_color=C["border"], corner_radius=10,
                                           font=ctk.CTkFont(size=16), text_color=C["text_primary"])
        self.initials_entry.pack(padx=10)

        # Clear initials entry when user clicks
        self.initials_entry.bind("<FocusIn>", self.reset_initials_entry)

        # Add & pack submit score button
        self.submit_score_btn = ctk.CTkButton(self.score_box, text="Save to Leaderboard", width=180, height=40,
                                              fg_color=C["correct"], hover_color=C["accent_hover"],
                                              text_color=C["text_on_accent"], corner_radius=10,
                                              font=ctk.CTkFont(size=14, weight="bold"), command=self.submit_score)
        self.submit_score_btn.pack(pady=20)

        # Add & pack Quit and Try Again buttons
        self.quit_retry_btns = ctk.CTkFrame(self.results_container, fg_color="transparent", width=640, height=50,
                                            corner_radius=15)
        self.quit_retry_btns.pack(pady=20)
        self.quit_retry_btns.pack_propagate(False)
        self.quit_btn = ctk.CTkButton(self.quit_retry_btns, text="Quit", width=180, height=40,
                                      fg_color=C["incorrect"], hover_color=C["incorrect_hover"],
                                      text_color=C["text_on_accent"], corner_radius=10,
                                      font=ctk.CTkFont(size=14, weight="bold"), command=self.destroy)
        self.quit_btn.pack(side="left", padx=(100, 10))
        self.try_again_btn = ctk.CTkButton(self.quit_retry_btns, text="Try Again", width=180, height=40,
                                           fg_color=C["accent"], hover_color=C["accent_hover"],
                                           text_color=C["text_on_accent"], corner_radius=10,
                                           font=ctk.CTkFont(size=16, weight="bold"), command=self.show_welcome)
        self.try_again_btn.pack(side="right", padx=(10, 100))

    def show_welcome(self):
        """Display the welcome frame and hide all other frames."""
        self.active_frame.pack_forget()
        self.results_frame.pack_forget()
        self.current_state = "welcome"
        self.welcome_frame.pack(fill="both", expand=True)

    def show_active(self):
        """Display the active frame and hide all other frames."""
        self.welcome_frame.pack_forget()
        self.results_frame.pack_forget()
        self.current_state = "active"
        self.active_frame.pack(fill="both", expand=True)

    def show_results(self):
        """Display the results frame and hide all other frames."""
        self.welcome_frame.pack_forget()
        self.active_frame.pack_forget()
        self.current_state = "results"
        self.results_frame.pack(fill="both", expand=True)
