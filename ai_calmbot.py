#!/usr/bin/env python3
"""
CalmBot: a tiny AI agent for calming, supportive chat.

Features
- Greets the user and keeps a short conversational context
- Detects simple intents via keyword patterns (stress, panic, anger, sleep, etc.)
- Offers exercises: box breathing, 4-7-8 breathing, 5-4-3-2-1 grounding, quick journaling
- Gentle CBT-style reframing prompts
- Crisis safety: if messages look risky, it shares supportive next steps
- No external libraries required

Run
    python calmbot.py
Type `help` inside the chat for commands; `quit` to exit.
"""
from __future__ import annotations
import re
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Callable, Optional

# ---------- Helpers ----------
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def contains_any(text: str, words: List[str]) -> bool:
    """Check whether any keyword in `words` appears in `text`."""
    return any(w in text for w in words)


# ---------- Exercises ----------
def box_breathing(cycles: int = 3, seconds: int = 4, realtime: bool = False) -> str:
    lines = [f"Let's try box breathing (4 steps). We'll do {cycles} cycles."]
    for i in range(1, cycles + 1):
        lines.append(f"Cycle {i}:")
        for step in ("Inhale", "Hold", "Exhale", "Hold"):
            lines.append(f"  {step} for {seconds}…")
            if realtime:
                time.sleep(seconds)
    lines.append("Nice work. Notice any change in your body right now?")
    return "\n".join(lines)


def four_seven_eight(cycles: int = 3, realtime: bool = False) -> str:
    lines = [f"We'll try the 4–7–8 breath. We'll do {cycles} cycles."]
    for i in range(1, cycles + 1):
        lines.append(f"Cycle {i}:")
        lines.append("  Inhale through your nose for 4…")
        if realtime:
            time.sleep(4)
        lines.append("  Hold for 7…")
        if realtime:
            time.sleep(7)
        lines.append("  Exhale slowly through your mouth for 8…")
        if realtime:
            time.sleep(8)
    lines.append("Great. Unclench your jaw and drop your shoulders.")
    return "\n".join(lines)


def grounding_54321() -> str:
    return (
        "Let's do the 5-4-3-2-1 grounding exercise:\n"
        "  • Name 5 things you can see\n"
        "  • 4 things you can feel (chair, clothes, air)\n"
        "  • 3 things you can hear\n"
        "  • 2 things you can smell\n"
        "  • 1 thing you can taste or a slow sip of water\n"
        "Type a few of yours here—I'll listen."
    )


def mini_journal_prompt() -> str:
    return (
        "Mini-journal (2 mins):\n"
        "  1) What happened?\n"
        "  2) What am I feeling (name it)?\n"
        "  3) What do I need right now?\n"
        "  4) One tiny next step?"
    )


# ---------- Safety ----------
RISKY_PATTERNS = [
    r"kill myself", r"suicide", r"end my life", r"self-harm", r"cut myself",
    r"can't go on", r"no reason to live", r"hurt myself"
]

def safety_check(text: str) -> bool:
    """Return True if text contains high-risk patterns."""
    t = normalize(text)
    return any(re.search(p, t) for p in RISKY_PATTERNS)

SAFETY_MESSAGE = (
    "I'm really glad you told me. You deserve support right now.\n"
    "• If you're in immediate danger or thinking about hurting yourself: please contact local emergency services, or reach out to someone you trust nearby.\n"
    "• Consider contacting a mental-health professional or your campus counseling service.\n"
    "• If available, call a national crisis helpline in your country. You're not alone.\n"
    "We can also keep talking. Would you like a grounding exercise or just to vent?"
)


# ---------- Context & Types ----------
@dataclass
class Context:
    name: Optional[str] = None
    last_topics: List[str] = field(default_factory=list)

Response = Tuple[str, str]  # (intent, message)


# ---------- CalmBot ----------
class CalmBot:
    def __init__(self):
        self.ctx = Context()
        # Each tuple: (keywords, handler_function)
        self.handlers: List[Tuple[List[str], Callable[[str], Response]]] = [
            (["hi", "hello", "hey", "good morning", "good evening"], self._handle_greeting),
            (["panic", "anxious", "anxiety", "overwhelmed", "stressed", "stress"], self._handle_stress),
            (["angry", "frustrated", "mad", "irritated"], self._handle_anger),
            (["can't sleep", "insomnia", "sleep"], self._handle_sleep),
            (["ground", "54321", "focus"], self._handle_grounding),
            (["breathe", "breathing", "box", "4-7-8", "478"], self._handle_breathing),
            (["journal", "write", "thoughts"], self._handle_journal),
            (["help", "commands", "menu"], self._handle_help),
        ]

    # ---- Handlers ----
    def _handle_greeting(self, text: str) -> Response:
        msg = (
            "Hi, I'm CalmBot. I'm here to listen.\n"
            "You can type what's on your mind, or say 'breathe', 'ground', or 'journal'."
        )
        return ("greet", msg)

    def _handle_stress(self, text: str) -> Response:
        msg = (
            "That sounds heavy. Let's slow things down.\n"
            + box_breathing(cycles=2, seconds=4, realtime=False)
            + "\nIf you'd rather, we can try grounding—type 'ground'."
        )
        return ("stress", msg)

    def _handle_anger(self, text: str) -> Response:
        msg = (
            "I hear a lot of energy there. Two quick options:\n"
            "• 60-second breath (type 'breathe')\n"
            "• Write the unfiltered thought, then a kinder reframe starting with 'A more helpful way to see this might be…'"
        )
        return ("anger", msg)

    def _handle_sleep(self, text: str) -> Response:
        msg = (
            "Sleep can be tough when the mind is busy.\n"
            + four_seven_eight(cycles=2, realtime=False)
            + "\nTip: keep lights dim, put the phone face down after this."
        )
        return ("sleep", msg)

    def _handle_grounding(self, text: str) -> Response:
        return ("grounding", grounding_54321())

    def _handle_breathing(self, text: str) -> Response:
        return ("breathing", box_breathing(cycles=3, seconds=4, realtime=False))

    def _handle_journal(self, text: str) -> Response:
        return ("journal", mini_journal_prompt())

    def _handle_help(self, text: str) -> Response:
        return ("help", "Commands: 'breathe', 'ground', 'journal', or tell me how you're feeling. Type 'quit' to exit.")

    # ---- Routing ----
    def reply(self, user_text: str) -> str:
        # Safety check first (use original text so safety_check normalizes it internally)
        if safety_check(user_text):
            return SAFETY_MESSAGE

        t = normalize(user_text)

        # Name capture: "I'm <name>" or "I am <name>"
        m = re.search(r"\b(i am|i'm)\s+([a-zA-Z]{2,})\b", t)
        if m:
            # store capitalized name
            self.ctx.name = m.group(2).capitalize()

        for keys, handler in self.handlers:
            if contains_any(t, keys):
                intent, msg = handler(t)
                self.ctx.last_topics.append(intent)
                return self._prefix_name(msg)

        # Default empathetic response
        return self._prefix_name(
            "Thanks for sharing. I'm here with you. Would you like to try 'ground' or 'breathe', or tell me more?"
        )

    def _prefix_name(self, message: str) -> str:
        if self.ctx.name:
            return f"{self.ctx.name}, {message}"
        return message


# ---------- Interactive loop ----------
def chat_loop():
    bot = CalmBot()
    print("CalmBot ready. Type 'help' for options, 'quit' to exit.\n")
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTake care. Bye!")
            break
        if not user:
            continue
        if user.lower() in {"quit", "exit", "bye"}:
            print("CalmBot: Sending you a deep breath. Take care.")
            break
        print("CalmBot:", bot.reply(user))


if __name__ == "__main__":
    chat_loop()
