# -*- coding: utf-8 -*-
"""
Grieks Woordjes Oefenen
Een klein oefenprogramma voor Grieks-Nederlandse woordenschat.
"""
import random
import tkinter as tk
from tkinter import ttk, font

from vocab_data import ALL_LESSONS


class VocabApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grieks Woordjes Oefenen")
        self.geometry("700x500")
        self.minsize(600, 450)
        self.configure(bg="#f4f1ea")

        self.greek_font = font.Font(family="Arial", size=20)
        self.normal_font = font.Font(family="Arial", size=13)
        self.title_font = font.Font(family="Arial", size=18, weight="bold")

        self.lesson_vars = {}
        self.direction = tk.StringVar(value="gr_nl")
        self.mode = tk.StringVar(value="multiple_choice")

        self.quiz_pool = []
        self.current_index = 0
        self.score = 0
        self.total = 0
        self.current_pair = None

        self.container = tk.Frame(self, bg="#f4f1ea")
        self.container.pack(fill="both", expand=True)

        self.show_start_screen()

    # ---------- helpers ----------
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ---------- start screen ----------
    def show_start_screen(self):
        self.clear_container()
        f = self.container

        tk.Label(f, text="Grieks Woordjes Oefenen", font=self.title_font,
                 bg="#f4f1ea", fg="#2c3e50").pack(pady=(30, 20))

        # Lesson selection
        lesson_frame = tk.LabelFrame(f, text="Kies welke lessen je wilt oefenen",
                                      font=self.normal_font, bg="#f4f1ea", padx=15, pady=10)
        lesson_frame.pack(pady=10, padx=30, fill="x")

        self.lesson_vars = {}
        for name in ALL_LESSONS:
            var = tk.BooleanVar(value=True)
            self.lesson_vars[name] = var
            tk.Checkbutton(lesson_frame, text=name, variable=var,
                           font=self.normal_font, bg="#f4f1ea",
                           anchor="w").pack(fill="x", pady=2)

        # Direction selection
        dir_frame = tk.LabelFrame(f, text="Richting", font=self.normal_font,
                                   bg="#f4f1ea", padx=15, pady=10)
        dir_frame.pack(pady=10, padx=30, fill="x")

        tk.Radiobutton(dir_frame, text="Grieks -> Nederlands", variable=self.direction,
                       value="gr_nl", font=self.normal_font, bg="#f4f1ea").pack(anchor="w")
        tk.Radiobutton(dir_frame, text="Nederlands -> Grieks", variable=self.direction,
                       value="nl_gr", font=self.normal_font, bg="#f4f1ea").pack(anchor="w")
        tk.Radiobutton(dir_frame, text="Beide richtingen door elkaar", variable=self.direction,
                       value="mixed", font=self.normal_font, bg="#f4f1ea").pack(anchor="w")

        # Mode selection
        mode_frame = tk.LabelFrame(f, text="Oefenvorm", font=self.normal_font,
                                    bg="#f4f1ea", padx=15, pady=10)
        mode_frame.pack(pady=10, padx=30, fill="x")

        tk.Radiobutton(mode_frame, text="Meerkeuze", variable=self.mode,
                       value="multiple_choice", font=self.normal_font, bg="#f4f1ea").pack(anchor="w")
        tk.Radiobutton(mode_frame, text="Zelf typen", variable=self.mode,
                       value="typing", font=self.normal_font, bg="#f4f1ea").pack(anchor="w")
        tk.Radiobutton(mode_frame, text="Flashcards (omdraaien)", variable=self.mode,
                       value="flashcard", font=self.normal_font, bg="#f4f1ea").pack(anchor="w")

        tk.Button(f, text="Start oefenen", font=self.normal_font, bg="#2c3e50", fg="white",
                  padx=20, pady=8, command=self.start_quiz).pack(pady=25)

    # ---------- build quiz pool ----------
    def start_quiz(self):
        pool = []
        for name, var in self.lesson_vars.items():
            if var.get():
                pool.extend(ALL_LESSONS[name])

        if not pool:
            return  # nothing selected, ignore

        random.shuffle(pool)
        self.quiz_pool = pool
        self.current_index = 0
        self.score = 0
        self.total = 0
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
        progress = f"Woord {self.current_index + 1} / {len(self.quiz_pool)}   |   Score: {self.score}"
        tk.Label(f, text=progress, font=self.normal_font, bg="#f4f1ea", fg="#555").pack(pady=(20, 10))

        q_font = self.greek_font if q_direction == "gr_nl" else self.normal_font
        tk.Label(f, text=question, font=q_font, bg="#f4f1ea", fg="#2c3e50",
                 wraplength=600, justify="center").pack(pady=20)

        self.feedback_label = tk.Label(f, text="", font=self.normal_font, bg="#f4f1ea")
        self.feedback_label.pack(pady=5)

        if mode == "multiple_choice":
            self.build_multiple_choice(answer, q_direction)
        elif mode == "typing":
            self.build_typing()
        else:
            self.build_flashcard(answer, q_direction)

    def build_multiple_choice(self, correct_answer, q_direction):
        # gather distractors from the whole pool (opposite side of pair)
        idx = 1 if q_direction == "gr_nl" else 0
        others = [p[idx] for p in self.quiz_pool if p[idx] != correct_answer]
        distractors = random.sample(others, min(3, len(others)))
        options = distractors + [correct_answer]
        random.shuffle(options)

        btn_font = self.greek_font if q_direction == "nl_gr" else self.normal_font

        for opt in options:
            tk.Button(self.container, text=opt, font=btn_font, wraplength=550,
                      bg="#eaeaea", padx=10, pady=8,
                      command=lambda o=opt: self.check_answer(o, correct_answer)).pack(pady=5, fill="x", padx=60)

    def build_typing(self):
        entry_var = tk.StringVar()
        entry = tk.Entry(self.container, textvariable=entry_var, font=self.normal_font, justify="center")
        entry.pack(pady=10, ipadx=10, ipady=5)
        entry.focus()

        def submit(event=None):
            self.check_answer(entry_var.get().strip(), self.current_answer, is_typing=True)

        entry.bind("<Return>", submit)
        tk.Button(self.container, text="Controleer", font=self.normal_font, bg="#2c3e50", fg="white",
                  command=submit).pack(pady=10)

    def build_flashcard(self, answer, q_direction):
        ans_font = self.greek_font if q_direction == "nl_gr" else self.normal_font
        reveal_label = tk.Label(self.container, text="", font=ans_font, bg="#f4f1ea",
                                 fg="#2c3e50", wraplength=600, justify="center")

        def reveal():
            reveal_label.config(text=answer)
            reveal_label.pack(pady=15)
            next_btn.pack(pady=10)
            show_btn.pack_forget()

        show_btn =
