import requests
import json
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyttsx3

# Set up the OpenRouter API key (replace with your actual key)
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Variable to track the number of decisions
decision_count = 0
max_decisions = 10

# Initialize text-to-speech engine
engine = pyttsx3.init()


def setup_voice_properties():
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'english' in voice.name.lower() and 'united' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)


def read_story_aloud():
    setup_voice_properties()
    story_content = story_text.get(1.0, tk.END).strip()
    if not story_content:
        messagebox.showwarning("No Content", "The story is empty. Start the story first.")
        return
    engine.say(story_content)
    engine.runAndWait()


def ask_ai(messages, max_retries=3):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": "openai/gpt-3.5-turbo", "messages": messages, "max_tokens": 500, "temperature": 0.8}

    for _ in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=data, timeout=10)
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                return response_json["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException:
            time.sleep(2)
    return "⚠️ Failed to get a response from the AI. Please try again later."


def start_story(genre):
    prompt = f"Create a detailed and engaging interactive story in the {genre} genre. Start with an immersive opening scene."
    return ask_ai([{"role": "system", "content": "You are an interactive storyteller."},
                   {"role": "user", "content": prompt}])


def continue_story(messages, decision):
    messages.append({"role": "user", "content": decision})
    return ask_ai(messages)


def on_submit():
    global decision_count
    user_choice = user_input.get()
    if not user_choice.strip():
        messagebox.showwarning("Input Error", "Please enter an action!")
        return

    if decision_count >= max_decisions:
        story_text.insert(tk.END, "\n\nThe story has ended after 10 decisions.\n", "ai_response")
        return

    decision_count += 1
    story_text.insert(tk.END, f"\n\n> {user_choice}\n", "user_input")
    next_part = continue_story(messages, user_choice)
    messages.append({"role": "assistant", "content": next_part})
    story_text.insert(tk.END, f"\n{next_part}\n", "ai_response")
    user_input.delete(0, tk.END)


def start_game():
    genre = genre_input.get()
    if not genre.strip():
        messagebox.showwarning("Input Error", "Please enter a genre!")
        return
    global messages, decision_count
    messages = [{"role": "system", "content": "You are an interactive storyteller."}]
    decision_count = 0
    story = start_story(genre)
    messages.append({"role": "assistant", "content": story})
    story_text.delete(1.0, tk.END)
    story_text.insert(tk.END, story + "\n", "ai_response")


# Create Tkinter root window
tk_root = tk.Tk()
tk_root.title("🔥 Interactive Story Generator 🔥")
tk_root.geometry("800x700")
tk_root.configure(bg="#2e003e")  # Dark Purple background

# Retro Style
style = {"fg": "#ffffff", "bg": "#2e003e", "font": ("Courier", 14, "bold")}


def create_retro_button(parent, text, command):
    button = tk.Button(parent, text=text, command=command, font=("Courier", 12, "bold"),
                       bg="#4B0082", fg="white", padx=20, pady=5, relief="ridge")
    button.pack(pady=10)
    return button


# Title
tk.Label(tk_root, text="Enter Story Genre:", **style).pack(pady=10)

# Genre Input
genre_input = tk.Entry(tk_root, width=50, font=("Courier", 14), bg="#3e0061", fg="white", bd=2, relief="solid")
genre_input.pack(pady=10)

# Start Button
create_retro_button(tk_root, "Start Story", start_game)

# Story Text Area
story_text = scrolledtext.ScrolledText(tk_root, wrap=tk.WORD, width=80, height=25, font=("Courier", 12),
                                       bg="#000000", fg="#ffffff", bd=2, relief="solid")
story_text.pack(pady=20)
story_text.tag_config("user_input", foreground="#00f", font=("Courier", 12, "bold"))
story_text.tag_config("ai_response", foreground="#ffffff", font=("Courier", 12))  # White AI output

# Input & Submit Button in the same frame
input_frame = tk.Frame(tk_root, bg="#2e003e")
input_frame.pack(pady=10)

# User Input Field inside the frame
user_input = tk.Entry(input_frame, width=40, font=("Courier", 14), bg="#3e0061", fg="white", bd=2, relief="solid")
user_input.pack(side=tk.LEFT, padx=10)

# Submit Button beside the input field
submit_button = tk.Button(input_frame, text="Submit", command=on_submit, font=("Courier", 12, "bold"),
                          bg="#4B0082", fg="white", padx=20, pady=5, relief="ridge")
submit_button.pack(side=tk.RIGHT)

# Read Aloud Button
create_retro_button(tk_root, "Read Aloud", read_story_aloud)

# Start the Tkinter main loop
tk_root.mainloop()
