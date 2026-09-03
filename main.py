# -*- coding: utf-8 -*-
"""
Grieks Woordjes Oefenen
Donker thema. Woordenschat + grammatica-oefening (imperfectum), met
voortgangsopslag tussen sessies, optionele timer, focus op moeilijke
woorden, en experimentele (offline) uitspraak.
"""
import random
import threading
import tkinter as tk
from tkinter import font

from vocab_data import ALL_LESSONS, TIPS, GRAMMAR_EXERCISES
from progress_store import (
    load_progress, save_progress, register_result,
    difficult_words_count, word_key,
)

try:
    import pyttsx3
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False

# ---------- kleuren (donker thema) ----------
BG = "#121212"
BG_CARD = "#1e1e1e"
BG_INPUT = "#2a2a2a"
FG = "#e8e8e8"
FG_DIM = "#9a9a9a"
ACCENT = "#4fc3f7"
GOOD = "#66bb6a"
BAD = "#ef5350"
BORDER = "#333333"


class VocabApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grieks Woordjes Oefenen")
        self.geometry("740x620")
        self.minsize(640, 520)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.greek_font = font.Font(family="Arial", size=21)
        self.normal_font = font.Font(family="Arial", size=13)
        self.small_font = font.Font(family="Arial", size=11)
        self.title_font = font.Font(family="Arial", size=19, weight="bold")

        self.progress = load_progress()

        self.lesson_vars = {}
        self.direction = tk.StringVar(value="gr_nl")
        self.mode = tk.StringVar(value="multiple_choice")
        self.practice_type = tk.StringVar(value="vocab")  # vocab of grammar
        self.difficult_focus = tk.BooleanVar(value=False)
        self.timer_enabled = tk.BooleanVar(value=False)
        self.timer_seconds = tk.IntVar(value=10)
        self.audio_enabled = tk.BooleanVar(value=AUDIO_AVAILABLE)

        self.quiz_pool = []
        self.wrong_this_round = []
        self.current_index = 0
        self.score = 0
        self.total = 0
        self.streak = 0
        self.best_streak = 0
        self.current_pair = None
        self.hint_used = False
        self.timer_job = None
        self.time_left = 0

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.show_start_screen()

    # ---------- helpers ----------
    def clear_container(self):
        self.cancel_timer()
        for widget in self.container.winfo_children():
            widget.destroy()

    def styled_button(self, parent, text, command, bg=ACCENT, fg="#0a0a0a", **kwargs):
        return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                          activebackground=bg, activeforeground=fg,
                          font=self.normal_font, relief="flat", bd=0,
                          padx=16, pady=8, cursor="hand2", **kwargs)

    def on_close(self):
        save_progress(self.progress)
        self.destroy()

    # ---------- audio ----------
    def speak(self, text):
        if not (AUDIO_AVAILABLE and self.audio_enabled.get()):
            return

        def worker():
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 140)
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def speak_button(self, parent, text):
        if not (AUDIO_AVAILABLE and self.audio_enabled.get()):
            return None
        return self.styled_button(parent, "\U0001F50A", lambda: self.speak(text),
                                   bg=BG_INPUT, fg=FG, padx=10, pady=4)

    # ---------- start screen ----------
    def show_start_screen(self):
        self.clear_container()
        f = self.container

        tk.Label(f, text="Grieks Woordjes Oefenen", font=self.title_font,
                 bg=BG, fg=FG).pack(pady=(20, 2))

        tip = random.choice(TIPS)
        tk.Label(f, text=f"Tip: {tip}", font=self.small_font, bg=BG, fg=ACCENT,
                 wraplength=640, justify="center").pack(pady=(0, 10))

        # Scroll-achtig canvas zodat alle opties passen op kleinere schermen
        outer = tk.Frame(f, bg=BG)
        outer.pack(fill="both", expand=True, padx=20)

        # Wat wil je oefenen?
        type_frame = tk.LabelFrame(outer, text="Wat wil je oefenen?", font=self.normal_font,
                                    bg=BG_CARD, fg=FG, bd=1, relief="solid",
                                    highlightbackground=BORDER, padx=12, pady=8)
        type_frame.pack(pady=6, fill="x")
        tk.Radiobutton(type_frame, text="Woordenschat (Tekst 8A/8B/8C)", variable=self.practice_type,
                       value="vocab", font=self.small_font, bg=BG_CARD, fg=FG,
                       selectcolor=BG_INPUT, activebackground=BG_CARD, activeforeground=FG,
                       command=lambda: self.refresh_start_screen()).pack(anchor="w")
        tk.Radiobutton(type_frame, text="Werkwoordsvormen (imperfectum)", variable=self.practice_type,
                       value="grammar", font=self.small_font, bg=BG_CARD, fg=FG,
                       selectcolor=BG_INPUT, activebackground=BG_CARD, activeforeground=FG,
                       command=lambda: self.refresh_start_screen()).pack(anchor="w")

        self.options_holder = tk.Frame(outer, bg=BG)
        self.options_holder.pack(fill="both", expand=True)
        self.build_type_specific_options()

        # Extra opties: moeilijke woorden, timer, audio
        extra_frame = tk.LabelFrame(outer, text="Extra opties", font=self.normal_font,
                                     bg=BG_CARD, fg=FG, bd=1, relief="solid",
                                     highlightbackground=BORDER, padx=12, pady=8)
        extra_frame.pack(pady=6, fill="x")

        n_diff = difficult_words_count(self.progress, self._current_full_pool())
        diff_text = "Focus op moeilijke woorden (uit vorige sessies)"
        if n_diff:
            diff_text += f"  -  {n_diff} bekend"
        tk.Checkbutton(extra_frame, text=diff_text, variable=self.difficult_focus,
                       font=self.small_font, bg=BG_CARD, fg=FG, selectcolor=BG_INPUT,
                       activebackground=BG_CARD, activeforeground=FG).pack(anchor="w")

        timer_row = tk.Frame(extra_frame, bg=BG_CARD)
        timer_row.pack(anchor="w", fill="x", pady=2)
        tk.Checkbutton(timer_row, text="Tijdsdruk per vraag:", variable=self.timer_enabled,
                       font=self.small_font, bg=BG_CARD, fg=FG, selectcolor=BG_INPUT,
                       activebackground=BG_CARD, activeforeground=FG).pack(side="left")
        tk.Spinbox(timer_row, from_=5, to=60, increment=5, width=4,
                   textvariable=self.timer_seconds, font=self.small_font,
                   bg=BG_INPUT, fg=FG, buttonbackground=BG_INPUT, relief="flat",
                   insertbackground=FG).pack(side="left", padx=6)
        tk.Label(timer_row, text="seconden", font=self.small_font, bg=BG_CARD, fg=FG_DIM).pack(side="left")

        if AUDIO_AVAILABLE:
            tk.Checkbutton(extra_frame, text="\U0001F50A Uitspraak (experimenteel, geen native Oudgrieks)",
                           variable=self.audio_enabled, font=self.small_font, bg=BG_CARD, fg=FG,
                           selectcolor=BG_INPUT, activebackground=BG_CARD, activeforeground=FG).pack(anchor="w")
        else:
            tk.Label(extra_frame, text="Uitspraak niet beschikbaar op dit systeem.",
                     font=self.small_font, bg=BG_CARD, fg=FG_DIM).pack(anchor="w")

        self.styled_button(f, "Start oefenen", self.start_quiz).pack(pady=16)

        if self.best_streak:
            tk.Label(f, text=f"Beste reeks tot nu toe: {self.best_streak}",
                     font=self.small_font, bg=BG, fg=FG_DIM).pack(pady=(0, 10))

    def refresh_start_screen(self):
        self.show_start_screen()

    def build_type_specific_options(self):
        for w in self.options_holder.winfo_children():
            w.destroy()

        if self.practice_type.get() == "vocab":
            row = tk.Frame(self.options_holder, bg=BG)
            row.pack(fill="x", pady=4)

            lesson_frame = tk.LabelFrame(row, text="Lessen", font=self.normal_font,
                                          bg=BG_CARD, fg=FG, bd=1, relief="solid",
                                          highlightbackground=BORDER, padx=12, pady=8)
            lesson_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

            self.lesson_vars = {}
            for name in ALL_LESSONS:
                var = tk.BooleanVar(value=True)
                self.lesson_vars[name] = var
                tk.Checkbutton(lesson_frame, text=name, variable=var,
                               font=self.small_font, bg=BG_CARD, fg=FG,
                               selectcolor=BG_INPUT, activebackground=BG_CARD,
                               activeforeground=FG, anchor="w").pack(fill="x", pady=1)

            dir_frame = tk.LabelFrame(row, text="Richting", font=self.normal_font,
                                       bg=BG_CARD, fg=FG, bd=1, relief="solid",
                                       highlightbackground=BORDER, padx=12, pady=8)
            dir_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))
            for label, val in [("Grieks -> Nederlands", "gr_nl"),
                                ("Nederlands -> Grieks", "nl_gr"),
                                ("Gemengd", "mixed")]:
                tk.Radiobutton(dir_frame, text=label, variable=self.direction, value=val,
                               font=self.small_font, bg=BG_CARD, fg=FG,
                               selectcolor=BG_INPUT, activebackground=BG_CARD,
                               activeforeground=FG).pack(anchor="w")
        else:
            info = tk.Label(self.options_holder,
                             text="Richting ligt vast: Nederlands -> Grieks (jij vult de vorm in).",
                             font=self.small_font, bg=BG, fg=FG_DIM, wraplength=640, justify="left")
            info.pack(pady=4, anchor="w")

        mode_frame = tk.LabelFrame(self.options_holder, text="Oefenvorm", font=self.normal_font,
                                    bg=BG_CARD, fg=FG, bd=1, relief="solid",
                                    highlightbackground=BORDER, padx=12, pady=8)
        mode_frame.pack(fill="x", pady=4)
        for label, val in [("Meerkeuze", "multiple_choice"),
                            ("Zelf typen", "typing"),
                            ("Flashcards", "flashcard")]:
            tk.Radiobutton(mode_frame, text=label, variable=self.mode, value=val,
                           font=self.small_font, bg=BG_CARD, fg=FG,
                           selectcolor=BG_INPUT, activebackground=BG_CARD,
                           activeforeground=FG).pack(side="left", padx=10)

    def _current_full_pool(self):
        if self.practice_type.get() == "grammar":
            return GRAMMAR_EXERCISES
        pool = []
        for name, var in getattr(self, "lesson_vars", {}).items():
            if var.get():
                pool.extend(ALL_LESSONS[name])
        if not pool:
            for words in ALL_LESSONS.values():
                pool.extend(words)
        return pool

    # ---------- build quiz pool ----------
    def start_quiz(self, wrong_only=False):
        if wrong_only and self.wrong_this_round:
            pool = list(self.wrong_this_round)
        else:
            pool = self._current_full_pool()
            if not pool:
                return
            if self.difficult_focus.get():
                weighted = []
                for pair in pool:
                    w = self.progress.get(word_key(pair), {})
                    weight = 1 + min(w.get("wrong", 0), 5) * 2
                    weighted.extend([pair] * weight)
                pool = weighted

        random.shuffle(pool)
        self.quiz_pool = pool
        self.wrong_this_round = []
        self.current_index = 0
        self.score = 0
        self.total = 0
        self.streak = 0
        self.next_question()

    def get_direction_for_pair(self):
        if self.practice_type.get() == "grammar":
            return "nl_gr"
        d = self.direction.get()
        if d == "mixed":
            return random.choice(["gr_nl", "nl_gr"])
        return d

    # ---------- timer ----------
    def cancel_timer(self):
        if self.timer_job is not None:
            try:
                self.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None

    def start_timer(self):
        if not self.timer_enabled.get():
            return
        self.time_left = self.timer_seconds.get()
        self.update_timer_label()
        self.tick_timer()

    def tick_timer(self):
        if self.time_left <= 0:
            self.timer_job = None
            self.timeout_answer()
            return
        self.time_left -= 1
        self.update_timer_label()
        self.timer_job = self.after(1000, self.tick_timer)

    def update_timer_label(self):
        if hasattr(self, "timer_label") and self.timer_label.winfo_exists():
            color = BAD if self.time_left <= 3 else FG_DIM
            self.timer_label.config(text=f"Tijd: {self.time_left}s", fg=color)

    def timeout_answer(self):
        mode = self.mode.get()
        if mode == "flashcard":
            self.mark_flashcard(False)
        else:
            self.check_answer("", self.current_answer, is_typing=True, timed_out=True)

    # ---------- question flow ----------
    def next_question(self):
        self.cancel_timer()
        if self.current_index >= len(self.quiz_pool):
            self.show_end_screen()
            return

        self.clear_container()
        self.hint_used = False
        pair = self.quiz_pool[self.current_index]
        self.current_pair = pair
        q_direction = self.get_direction_for_pair()

        if q_direction == "gr_nl":
            question, answer = pair[0], pair[1]
        else:
            question, answer = pair[1], pair[0]
        self.current_answer = answer
        self.current_question_direction = q_direction

        mode = self.mode.get()
        f = self.container

        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", pady=(18, 0), padx=20)
        progress = f"Vraag {self.current_index + 1} / {len(self.quiz_pool)}"
        tk.Label(top, text=progress, font=self.small_font, bg=BG, fg=FG_DIM).pack(side="left")

        right_info = tk.Frame(top, bg=BG)
        right_info.pack(side="right")
        tk.Label(right_info, text=f"Score: {self.score}   Reeks: {self.streak}",
                 font=self.small_font, bg=BG, fg=FG_DIM).pack(side="right")
        self.timer_label = tk.Label(right_info, text="", font=self.small_font, bg=BG, fg=FG_DIM)
        self.timer_label.pack(side="right", padx=(0, 12))

        card = tk.Frame(f, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(pady=16, padx=40, fill="x")

        card_inner = tk.Frame(card, bg=BG_CARD)
        card_inner.pack(pady=20)

        q_font = self.greek_font if q_direction == "gr_nl" else self.normal_font
        tk.Label(card_inner, text=question, font=q_font, bg=BG_CARD, fg=FG,
                 wraplength=520, justify="center").pack(side="left")

        if q_direction == "gr_nl":
            btn = self.speak_button(card_inner, question)
            if btn:
                btn.pack(side="left", padx=(10, 0))

        self.feedback_label = tk.Label(f, text="", font=self.normal_font, bg=BG)
        self.feedback_label.pack(pady=6)

        self.answer_area = tk.Frame(f, bg=BG)
        self.answer_area.pack(fill="both", expand=True)

        if mode == "multiple_choice":
            self.build_multiple_choice(answer, q_direction)
        elif mode == "typing":
            self.build_typing()
        else:
            self.build_flashcard(answer, q_direction)

        self.start_timer()

    def build_multiple_choice(self, correct_answer, q_direction):
        idx = 1 if q_direction == "gr_nl" else 0
        others = [p[idx] for p in self.quiz_pool if p[idx] != correct_answer]
        distractors = random.sample(others, min(3, len(others))) if others else []
        options = distractors + [correct_answer]
        random.shuffle(options)

        btn_font = self.greek_font if q_direction == "nl_gr" else self.normal_font

        self.mc_buttons = []
        for i, opt in enumerate(options):
            b = tk.Button(self.answer_area, text=f"{i + 1}.  {opt}", font=btn_font,
                          wraplength=560, bg=BG_INPUT, fg=FG, activebackground=BG_INPUT,
                          activeforeground=FG, relief="flat", bd=0, anchor="w",
                          padx=14, pady=10, cursor="hand2",
                          command=lambda o=opt: self.check_answer(o, correct_answer))
            b.pack(pady=5, fill="x", padx=60)
            self.mc_buttons.append(b)

        for i in range(len(options)):
            self.bind(str(i + 1), lambda e, n=i: self._invoke_mc(n))

    def _invoke_mc(self, n):
        if n < len(self.mc_buttons) and self.mc_buttons[n]["state"] != "disabled":
            self.mc_buttons[n].invoke()

    def build_typing(self):
        entry_var = tk.StringVar()
        entry = tk.Entry(self.answer_area, textvariable=entry_var, font=self.normal_font,
                          justify="center", bg=BG_INPUT, fg=FG, insertbackground=FG,
                          relief="flat", bd=8)
        entry.pack(pady=8, ipadx=10, ipady=6, padx=100, fill="x")
        entry.focus()

        self.hint_label = tk.Label(self.answer_area, text="", font=self.small_font,
                                    bg=BG, fg=ACCENT)
        self.hint_label.pack(pady=(0, 6))

        def submit(event=None):
            self.check_answer(entry_var.get().strip(), self.current_answer, is_typing=True)

        def show_hint():
            self.hint_used = True
            first_letter = self.current_answer.strip()[0]
            self.hint_label.config(text=f"Hint: het antwoord begint met '{first_letter}'")

        entry.bind("<Return>", submit)

        btn_row = tk.Frame(self.answer_area, bg=BG)
        btn_row.pack(pady=8)
        self.styled_button(btn_row, "Controleer", submit).pack(side="left", padx=6)
        self.styled_button(btn_row, "Hint", show_hint, bg=BG_INPUT, fg=FG).pack(side="left", padx=6)

    def build_flashcard(self, answer, q_direction):
        ans_font = self.greek_font if q_direction == "nl_gr" else self.normal_font
        reveal_row = tk.Frame(self.answer_area, bg=BG)
        reveal_label = tk.Label(reveal_row, text="", font=ans_font, bg=BG,
                                 fg=ACCENT, wraplength=520, justify="center")

        def reveal():
            reveal_label.config(text=answer)
            reveal_label.pack(side="left")
            if q_direction == "nl_gr":
                btn = self.speak_button(reveal_row, answer)
                if btn:
                    btn.pack(side="left", padx=(10, 0))
            reveal_row.pack(pady=12)
            know_row.pack(pady=14)
            show_btn.pack_forget()

        show_btn = self.styled_button(self.answer_area, "Toon antwoord", reveal)
        show_btn.pack(pady=16)

        know_row = tk.Frame(self.answer_area, bg=BG)
        self.styled_button(know_row, "Ik wist het!", lambda: self.mark_flashcard(True),
                            bg=GOOD, fg="#0a0a0a").pack(side="left", padx=6)
        self.styled_button(know_row, "Nog niet", lambda: self.mark_flashcard(False),
                            bg=BAD, fg="#0a0a0a").pack(side="left", padx=6)

    def mark_flashcard(self, knew_it):
        self.cancel_timer()
        self.total += 1
        register_result(self.progress, self.current_pair, knew_it)
        if knew_it:
            self.score += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
        else:
            self.streak = 0
            self.wrong_this_round.append(self.current_pair)
        self.advance()

    def check_answer(self, given, correct, is_typing=False, timed_out=False):
        self.cancel_timer()
        self.total += 1
        correct_norm = correct.split("/")[0].split(",")[0].strip().lower()
        given_norm = given.strip().lower()

        if timed_out:
            is_correct = False
        elif is_typing:
            is_correct = given_norm in correct.lower() or correct_norm in given_norm
        else:
            is_correct = given == correct

        register_result(self.progress, self.current_pair, is_correct and not self.hint_used)

        if is_correct and not self.hint_used:
            self.score += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            self.feedback_label.config(text="Goed zo!", fg=GOOD)
        elif is_correct and self.hint_used:
            self.score += 1
            self.streak = 0
            self.feedback_label.config(text="Goed (met hint).", fg=ACCENT)
        else:
            self.streak = 0
            self.wrong_this_round.append(self.current_pair)
            msg = "Tijd voorbij! " if timed_out else "Helaas. "
            self.feedback_label.config(text=f"{msg}Juiste antwoord: {correct}", fg=BAD)

        for widget in self.answer_area.winfo_children():
            children = widget.winfo_children() if isinstance(widget, tk.Frame) else []
            for child in [widget] + list(children):
                if isinstance(child, tk.Button):
                    child.config(state="disabled")

        next_row = tk.Frame(self.container, bg=BG)
        next_row.pack(pady=10)
        self.styled_button(next_row, "Volgende ->", self.advance).pack(side="left", padx=4)
        if self.get_direction_for_pair() == "nl_gr" or self.current_question_direction == "nl_gr":
            btn = self.speak_button(next_row, correct)
            if btn:
                btn.pack(side="left", padx=4)

        self.bind("<Return>", lambda e: self.advance())

    def advance(self):
        self.unbind("<Return>")
        for i in range(1, 5):
            self.unbind(str(i))
        self.current_index += 1
        self.next_question()

    # ---------- end screen ----------
    def show_end_screen(self):
        self.clear_container()
        save_progress(self.progress)
        f = self.container

        tk.Label(f, text="Klaar!", font=self.title_font, bg=BG, fg=FG).pack(pady=(50, 10))

        if self.total > 0:
            pct = round(100 * self.score / self.total)
            result_text = f"Je score: {self.score} / {self.total}  ({pct}%)"
        else:
            result_text = "Ronde afgerond!"

        tk.Label(f, text=result_text, font=self.normal_font, bg=BG, fg=FG).pack(pady=6)
        tk.Label(f, text=f"Beste reeks: {self.best_streak}", font=self.small_font,
                 bg=BG, fg=FG_DIM).pack(pady=(0, 20))

        if self.wrong_this_round:
            n = len(set(word_key(p) for p in self.wrong_this_round))
            self.styled_button(f, f"Oefen je {n} foute woord(en) opnieuw",
                                lambda: self.start_quiz(wrong_only=True),
                                bg=BAD, fg="#0a0a0a").pack(pady=6)

        self.styled_button(f, "Terug naar het menu", self.show_start_screen).pack(pady=6)


if __name__ == "__main__":
    app = VocabApp()
    app.mainloop()
