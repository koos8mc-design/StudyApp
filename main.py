# -*- coding: utf-8 -*-
"""
Grieks Woordjes Oefenen
Een klein oefenprogramma voor Grieks-Nederlandse woordenschat.
Donker thema, met tips, hints en een herkansing voor foute woorden.
"""
import random
import tkinter as tk
from tkinter import font

from vocab_data import ALL_LESSONS, TIPS

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
        self.geometry("720x560")
        self.minsize(620, 480)
        self.configure(bg=BG)

        self.greek_font = font.Font(family="Arial", size=21)
        self.normal_font = font.Font(family="Arial", size=13)
        self.small_font = font.Font(family="Arial", size=11)
        self.title_font = font.Font(family="Arial", size=19, weight="bold")

        self.lesson_vars = {}
        self.direction = tk.StringVar(value="gr_nl")
        self.mode = tk.StringVar(value="multiple_choice")
        self.retry_wrong_only = False

        self.quiz_pool = []
        self.wrong_this_round = []
        self.current_index = 0
        self.score = 0
        self.total = 0
        self.streak = 0
        self.best_streak = 0
        self.current_pair = None
        self.hint_used = False

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.show_start_screen()

    # ---------- helpers ----------
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def styled_button(self, parent, text, command, bg=ACCENT, fg="#0a0a0a", **kwargs):
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                         activebackground=bg, activeforeground=fg,
                         font=self.normal_font, relief="flat", bd=0,
                         padx=16, pady=8, cursor="hand2", **kwargs)
        return btn

    # ---------- start screen ----------
    def show_start_screen(self):
        self.clear_container()
        f = self.container

        tk.Label(f, text="Grieks Woordjes Oefenen", font=self.title_font,
                 bg=BG, fg=FG).pack(pady=(28, 4))

        tip = random.choice(TIPS)
        tk.Label(f, text=f"Tip: {tip}", font=self.small_font, bg=BG, fg=ACCENT,
                 wraplength=600, justify="center").pack(pady=(0, 16))

        # Lesson selection
        lesson_frame = tk.LabelFrame(f, text="Kies welke lessen je wilt oefenen",
                                      font=self.normal_font, bg=BG_CARD, fg=FG,
                                      bd=1, relief="solid", highlightbackground=BORDER,
                                      padx=15, pady=10)
        lesson_frame.pack(pady=8, padx=30, fill="x")

        self.lesson_vars = {}
        for name in ALL_LESSONS:
            var = tk.BooleanVar(value=True)
            self.lesson_vars[name] = var
            tk.Checkbutton(lesson_frame, text=name, variable=var,
                           font=self.normal_font, bg=BG_CARD, fg=FG,
                           selectcolor=BG_INPUT, activebackground=BG_CARD,
                           activeforeground=FG, anchor="w").pack(fill="x", pady=2)

        # Direction + mode side by side
        row = tk.Frame(f, bg=BG)
        row.pack(pady=8, padx=30, fill="x")

        dir_frame = tk.LabelFrame(row, text="Richting", font=self.normal_font,
                                   bg=BG_CARD, fg=FG, bd=1, relief="solid",
                                   highlightbackground=BORDER, padx=12, pady=8)
        dir_frame.pack(side="left", padx=(0, 8), fill="both", expand=True)

        for label, val in [("Grieks -> Nederlands", "gr_nl"),
                            ("Nederlands -> Grieks", "nl_gr"),
                            ("Gemengd", "mixed")]:
            tk.Radiobutton(dir_frame, text=label, variable=self.direction, value=val,
                           font=self.small_font, bg=BG_CARD, fg=FG,
                           selectcolor=BG_INPUT, activebackground=BG_CARD,
                           activeforeground=FG).pack(anchor="w")

        mode_frame = tk.LabelFrame(row, text="Oefenvorm", font=self.normal_font,
                                    bg=BG_CARD, fg=FG, bd=1, relief="solid",
                                    highlightbackground=BORDER, padx=12, pady=8)
        mode_frame.pack(side="left", padx=(8, 0), fill="both", expand=True)

        for label, val in [("Meerkeuze", "multiple_choice"),
                            ("Zelf typen", "typing"),
                            ("Flashcards", "flashcard")]:
            tk.Radiobutton(mode_frame, text=label, variable=self.mode, value=val,
                           font=self.small_font, bg=BG_CARD, fg=FG,
                           selectcolor=BG_INPUT, activebackground=BG_CARD,
                           activeforeground=FG).pack(anchor="w")

        self.styled_button(f, "Start oefenen", self.start_quiz).pack(pady=22)

        stats = f"Beste reeks tot nu toe: {self.best_streak}" if self.best_streak else ""
        if stats:
            tk.Label(f, text=stats, font=self.small_font, bg=BG, fg=FG_DIM).pack()

    # ---------- build quiz pool ----------
    def start_quiz(self, wrong_only=False):
        if wrong_only and self.wrong_this_round:
            pool = list(self.wrong_this_round)
        else:
            pool = []
            for name, var in self.lesson_vars.items():
                if var.get():
                    pool.extend(ALL_LESSONS[name])

        if not pool:
            return

        random.shuffle(pool)
        self.quiz_pool = pool
        self.wrong_this_round = []
        self.current_index = 0
        self.score = 0
        self.total = 0
        self.streak = 0
        self.next_question()

    def get_direction_for_pair(self):
        d = self.direction.get()
        if d == "mixed":
            return random.choice(["gr_nl", "nl_gr"])
        return d

    # ---------- question flow ----------
    def next_question(self):
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
        progress = f"Woord {self.current_index + 1} / {len(self.quiz_pool)}"
        tk.Label(top, text=progress, font=self.small_font, bg=BG, fg=FG_DIM).pack(side="left")
        tk.Label(top, text=f"Score: {self.score}   Reeks: {self.streak}", font=self.small_font,
                 bg=BG, fg=FG_DIM).pack(side="right")

        card = tk.Frame(f, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(pady=18, padx=40, fill="x")

        q_font = self.greek_font if q_direction == "gr_nl" else self.normal_font
        tk.Label(card, text=question, font=q_font, bg=BG_CARD, fg=FG,
                 wraplength=580, justify="center", pady=24).pack()

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

    def build_multiple_choice(self, correct_answer, q_direction):
        idx = 1 if q_direction == "gr_nl" else 0
        others = [p[idx] for p in self.quiz_pool if p[idx] != correct_answer]
        distractors = random.sample(others, min(3, len(others)))
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
            self.bind(str(i + 1), lambda e, n=i: self.mc_buttons[n].invoke()
                      if n < len(self.mc_buttons) and self.mc_buttons[n]["state"] != "disabled" else None)

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
            first_letters = self.current_answer.strip()[0]
            self.hint_label.config(text=f"Hint: het antwoord begint met '{first_letters}'")

        entry.bind("<Return>", submit)

        btn_row = tk.Frame(self.answer_area, bg=BG)
        btn_row.pack(pady=8)
        self.styled_button(btn_row, "Controleer", submit).pack(side="left", padx=6)
        self.styled_button(btn_row, "Hint", show_hint, bg=BG_INPUT, fg=FG).pack(side="left", padx=6)

    def build_flashcard(self, answer, q_direction):
        ans_font = self.greek_font if q_direction == "nl_gr" else self.normal_font
        reveal_label = tk.Label(self.answer_area, text="", font=ans_font, bg=BG,
                                 fg=ACCENT, wraplength=580, justify="center")

        def reveal():
            reveal_label.config(text=answer)
            reveal_label.pack(pady=12)
            know_row.pack(pady=14)
            show_btn.pack_forget()

        def mark(knew_it):
            self.total += 1
            if knew_it:
                self.score += 1
                self.streak += 1
                self.best_streak = max(self.best_streak, self.streak)
            else:
                self.streak = 0
                self.wrong_this_round.append(self.current_pair)
            self.advance()

        show_btn = self.styled_button(self.answer_area, "Toon antwoord", reveal)
        show_btn.pack(pady=16)

        know_row = tk.Frame(self.answer_area, bg=BG)
        self.styled_button(know_row, "Ik wist het!", lambda: mark(True), bg=GOOD, fg="#0a0a0a").pack(side="left", padx=6)
        self.styled_button(know_row, "Nog niet", lambda: mark(False), bg=BAD, fg="#0a0a0a").pack(side="left", padx=6)

    def check_answer(self, given, correct, is_typing=False):
        self.total += 1
        correct_norm = correct.split("/")[0].split(",")[0].strip().lower()
        given_norm = given.strip().lower()

        is_correct = (given == correct) if not is_typing else (
            given_norm in correct.lower() or correct_norm in given_norm
        )
        if is_correct and self.hint_used:
            is_correct = True  # hint gebruikt telt nog als goed, maar reeks resetten
            self.streak = 0
        elif is_correct:
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
        else:
            self.streak = 0

        if is_correct:
            self.score += 1
            self.feedback_label.config(text="Goed zo!", fg=GOOD)
        else:
            self.wrong_this_round.append(self.current_pair)
            self.feedback_label.config(text=f"Helaas. Juiste antwoord: {correct}", fg=BAD)

        for widget in self.answer_area.winfo_children():
            for child in ([widget] + widget.winfo_children() if isinstance(widget, tk.Frame) else [widget]):
                if isinstance(child, tk.Button):
                    child.config(state="disabled")

        next_btn = self.styled_button(self.container, "Volgende woord ->", self.advance)
        next_btn.pack(pady=14)
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
        f = self.container

        tk.Label(f, text="Klaar!", font=self.title_font, bg=BG, fg=FG).pack(pady=(50, 10))

        if self.total > 0:
            pct = round(100 * self.score / self.total)
            result_text = f"Je score: {self.score} / {self.total}  ({pct}%)"
        else:
            result_text = "Flashcards doorgenomen!"

        tk.Label(f, text=result_text, font=self.normal_font, bg=BG, fg=FG).pack(pady=6)
        tk.Label(f, text=f"Beste reeks: {self.best_streak}", font=self.small_font,
                 bg=BG, fg=FG_DIM).pack(pady=(0, 20))

        if self.wrong_this_round:
            n = len(self.wrong_this_round)
            self.styled_button(f, f"Oefen je {n} foute woord(en) opnieuw",
                                lambda: self.start_quiz(wrong_only=True),
                                bg=BAD, fg="#0a0a0a").pack(pady=6)

        self.styled_button(f, "Opnieuw oefenen", self.show_start_screen).pack(pady=6)


if __name__ == "__main__":
    app = VocabApp()
    app.mainloop()
