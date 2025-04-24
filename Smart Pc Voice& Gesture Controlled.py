import tkinter as tk
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import os
import time
from datetime import datetime
from PIL import Image, ImageTk
import pyttsx3
from playsound import playsound
import threading
import subprocess
from tkinter import messagebox
from queue import Queue
import speech_recognition as sr
import ctypes

# ========== Voice Setup ==========
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 160)
speech_queue = Queue()

def speak(message):
    speech_queue.put(message)

def speak_thread():
    while True:
        message = speech_queue.get()
        if message == "STOP":
            break
        engine.say(message)
        engine.runAndWait()

threading.Thread(target=speak_thread, daemon=True).start()

# ========== Alarm Sound ==========
def play_alarm_once():
    threading.Thread(target=playsound, args=(r'C:\Users\ZUBERIYA\Downloads\japan-eas-alarm-277877.mp3',), daemon=True).start()

# ========== MediaPipe Setup ==========
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

# ========== Tkinter GUI ==========
root = tk.Tk()
root.title("Gesture-Based Access Control with Voice")
root.geometry("950x750")
root.configure(bg="#f0f0f5")

frame_webcam = tk.Frame(root, bg="#f0f0f5")
frame_webcam.place(x=50, y=50, width=640, height=480)
label_video = tk.Label(frame_webcam)
label_video.pack()

clock_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#f0f0f5", fg="#333")
clock_label.place(x=700, y=100)

caption_box = tk.Text(root, height=6, width=60, wrap='word', font=("Arial", 10), bg="white", fg="#333")
caption_box.place(x=50, y=680)

# ========== Gesture Recognition ==========
access_granted = False
failed_attempts = 0
lockout_until = 0
alarm_played_for_attempt = False
prev_x = None

def is_open_hand(landmarks):
    fingers = [
        landmarks.landmark[4].x < landmarks.landmark[3].x,
        landmarks.landmark[8].y < landmarks.landmark[6].y,
        landmarks.landmark[12].y < landmarks.landmark[10].y,
        landmarks.landmark[16].y < landmarks.landmark[14].y,
        landmarks.landmark[20].y < landmarks.landmark[18].y
    ]
    return all(fingers)

def is_waving(hand_landmarks):
    global prev_x
    x = hand_landmarks.landmark[0].x
    if prev_x is not None and abs(x - prev_x) > 0.15:
        return True
    prev_x = x
    return False

def update_webcam_feed():
    global access_granted, failed_attempts, lockout_until, alarm_played_for_attempt, prev_x
    ret, frame = cap.read()
    if not ret:
        return
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    now = time.time()

    if access_granted:
        cv2.putText(frame, "ACCESS GRANTED", (180, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    elif now < lockout_until:
        remaining = int(lockout_until - now)
        cv2.putText(frame, f"LOCKED: Wait {remaining}s", (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    elif results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if access_granted and is_waving(hand_landmarks):
                speak("Exiting application.")
                cap.release()
                root.destroy()
                return

            if is_open_hand(hand_landmarks):
                access_granted = True
                alarm_played_for_attempt = False
                speak("Access granted. Welcome!")
                enable_next_button()
                threading.Thread(target=listen_and_execute, daemon=True).start()
                break
            else:
                if not alarm_played_for_attempt:
                    failed_attempts += 1
                    speak("Unauthorized gesture!")
                    play_alarm_once()
                    alarm_played_for_attempt = True
                    if failed_attempts >= 3:
                        lockout_until = time.time() + 30
                        failed_attempts = 0
                        speak("Too many wrong attempts. Locked for 30 seconds.")
                    else:
                        speak(f"{3 - failed_attempts} attempts remaining.")
                break
    else:
        alarm_played_for_attempt = False
        if not access_granted and now >= lockout_until:
            cv2.putText(frame, "Show unlock gesture...", (160, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 2)

    img = Image.fromarray(frame)
    img_tk = ImageTk.PhotoImage(image=img)
    label_video.imgtk = img_tk
    label_video.configure(image=img_tk)
    root.after(10, update_webcam_feed)

# ========== Clock ==========
def update_clock():
    clock_label.config(text="Time: " + time.strftime('%H:%M:%S'))
    root.after(1000, update_clock)

# ========== Actions ==========
def open_notepad():
    try:
        subprocess.Popen([r"C:\Windows\System32\notepad.exe"])
    except Exception as e:
        speak("Unable to open Notepad.")
        print(e)

def lock_screen():
    try:
        ctypes.windll.user32.LockWorkStation()
    except Exception as e:
        speak("Unable to lock screen.")
        print(e)

def log_off():
    try:
        subprocess.call("shutdown -l", shell=True)
    except Exception as e:
        speak("Unable to log off.")
        print(e)

def restart_pc():
    os.system("shutdown /r /t 0")

def shutdown():
    os.system("shutdown /s /t 0")

def open_explorer():
    subprocess.Popen("explorer")

def minimize_all():
    pyautogui.hotkey('win', 'd')

def maximize_window():
    pyautogui.hotkey('win', 'up')

def open_taskbar():
    pyautogui.hotkey('win', 't')

def take_snapshot():
    ret, frame = cap.read()
    if ret:
        filename = f"snapshot_{int(time.time())}.png"
        cv2.imwrite(filename, frame)
        speak("Snapshot saved.")
        messagebox.showinfo("Snapshot", f"Saved as {filename}")

# ========== Buttons (Same Color) ==========
all_buttons = []
button_color = "#1976d2"

btn_styles_grid = [
    ("Open Taskbar", open_taskbar),
    ("Minimize All", minimize_all),
    ("File Explorer", open_explorer),
    ("Log Off", log_off),
    ("Maximize Window", maximize_window),
    ("Restart PC", restart_pc),
    ("Shutdown", shutdown),
    ("Lock Screen", lock_screen),
    ("Open Notepad", open_notepad)
]

grid_start_x = 50
grid_start_y = 550
button_width = 20
button_spacing_x = 200
button_spacing_y = 40

for index, (text, action_func) in enumerate(btn_styles_grid):
    row = index // 3
    col = index % 3
    x = grid_start_x + col * button_spacing_x
    y = grid_start_y + row * button_spacing_y
    btn = tk.Button(root, text=text, command=action_func, state='disabled',
                    width=button_width, bg=button_color, fg="white", font=("Arial", 10), activebackground="#0d47a1")
    btn.place(x=x, y=y)
    all_buttons.append(btn)

def enable_next_button():
    for btn in all_buttons:
        btn.config(state="normal")

# ========== Voice Command ==========
def listen_and_execute():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening for commands...")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            speak(f"Received command: {command}")
            caption_box.insert(tk.END, f"• {command}\n")
            caption_box.see(tk.END)

            if "open taskbar" in command:
                open_taskbar()
            elif "minimize all" in command:
                minimize_all()
            elif "maximize window" in command:
                maximize_window()
            elif "explorer" in command:
                open_explorer()
            elif "log off" in command:
                log_off()
            elif "restart" in command:
                restart_pc()
            elif "shutdown" in command:
                shutdown()
            elif "snapshot" in command:
                take_snapshot()
            elif "open notepad" in command or "open note pad" in command:
                open_notepad()
            else:
                speak("Command not recognized.")
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
        except sr.RequestError:
            speak("Sorry, I'm having trouble connecting to the speech service.")

# ========== Snapshot & Caption ==========
tk.Button(root, text="📸 Snapshot", command=take_snapshot,
          width=15, bg="#388e3c", fg="white").place(x=700, y=150)

tk.Button(root, text="🎤 Voice Command", command=lambda: threading.Thread(target=listen_and_execute, daemon=True).start(),
          bg="#1976d2", fg="white", font=("Arial", 10)).place(x=700, y=200)

# ========== Voice Captioning ==========
live_captioning = False
captioning_thread = None

def voice_to_notes():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Live captioning started.")
        while live_captioning:
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                caption_box.insert(tk.END, f"🗣 {text}\n")
                caption_box.see(tk.END)
            except sr.UnknownValueError:
                caption_box.insert(tk.END, "🚫 Could not understand\n")
            except sr.WaitTimeoutError:
                continue
            except sr.RequestError:
                caption_box.insert(tk.END, "🔌 Network error\n")
            time.sleep(0.1)

def toggle_captioning():
    global live_captioning, captioning_thread
    if not live_captioning:
        live_captioning = True
        captioning_thread = threading.Thread(target=voice_to_notes, daemon=True)
        captioning_thread.start()
        btn_caption.config(text="⏹ Stop Captioning", bg="red")
    else:
        live_captioning = False
        btn_caption.config(text="🎙 Start Captioning", bg="#6a1b9a")
        speak("Live captioning stopped.")

btn_caption = tk.Button(root, text="🎙 Start Captioning", command=toggle_captioning,
                        bg="#6a1b9a", fg="white", font=("Arial", 10))
btn_caption.place(x=700, y=250)

# ========== Start ==========
update_clock()
update_webcam_feed()
root.mainloop()
