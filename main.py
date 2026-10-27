import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import time
from pynput import mouse
from pynput import keyboard as pynput_keyboard
import keyboard

# Dictionary for translations
translations = {
    "en": {
        "title": "AutoClicker Pro",
        "header": "AutoClicker & Recorder",
        "status": "Status: Ready",
        "recorder": "Recorder & Replay",
        "record_btn": "Record Actions (F8)",
        "stop_record_btn": "Stop Recording (F8)",
        "reps_label": "Repetitions (0=Inf):",
        "replay_btn": "Start Replay",
        "replaying": "Replaying...",
        "autoclicker": "AutoClicker",
        "start_click_btn": "Start AutoClick (F9)",
        "stop_all_btn": "Stop All (F11)",
        "autoclicking": "AutoClicking...",
        "start_all_btn": "Start All (F10)",
        "recorded": "Recorded!",
        "warning": "Warning",
        "no_record": "No recording found!",
        "ready": "Ready"
    },
    "ru": {
        "title": "Автокликер Pro",
        "header": "Автокликер и Рекордер",
        "status": "Статус: Готов",
        "recorder": "Запись и Повтор",
        "record_btn": "Записать действия (F8)",
        "stop_record_btn": "Остановить запись (F8)",
        "reps_label": "Повторы (0=Беск):",
        "replay_btn": "Запустить повтор",
        "replaying": "Воспроизведение...",
        "autoclicker": "Автокликер",
        "start_click_btn": "Запустить кликер (F9)",
        "stop_all_btn": "Стоп (F11)",
        "autoclicking": "Работает...",
        "start_all_btn": "Запустить всё (F10)",
        "recorded": "Записано!",
        "warning": "Внимание",
        "no_record": "Запись не найдена!",
        "ready": "Готов"
    }
}

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-topmost", True)  # Always on top
        self.lang = "ru"  # Default language
        
        self.root.title(translations[self.lang]["title"])
        self.root.geometry("400x600")
        
        self.style = ttk.Style(theme="flatly")
        
        self.recording = False
        self.events = []
        self.recording_start_time = 0
        self.autoclicking = False
        self.replaying = False
        
        self.create_widgets()
        
        # Hotkeys
        keyboard.add_hotkey('f8', self.toggle_recording, suppress=False)
        keyboard.add_hotkey('f9', self.toggle_autoclick_simple, suppress=False)
        keyboard.add_hotkey('f10', self.start_all, suppress=False)
        keyboard.add_hotkey('f11', self.stop_all, suppress=False)

    def create_widgets(self):
        # Header with Language & Theme Toggle
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        self.lang_btn = ttk.Button(header_frame, text="EN/RU", command=self.toggle_lang, bootstyle="outline")
        self.lang_btn.pack(side="left")
        
        self.theme_btn = ttk.Button(header_frame, text="🌙/☀️", command=self.toggle_theme, bootstyle="outline")
        self.theme_btn.pack(side="right")
        
        self.header_label = ttk.Label(self.root, text=translations[self.lang]["header"], font=("Helvetica", 16, "bold"))
        self.header_label.pack(pady=5)
        
        # Status Label
        self.status_label = ttk.Label(self.root, text=translations[self.lang]["status"], font=("Helvetica", 10), bootstyle="info")
        self.status_label.pack(pady=10)
        
        # Recorder Section
        self.recorder_frame = ttk.LabelFrame(self.root, text=translations[self.lang]["recorder"], padding=10, bootstyle="primary")
        self.recorder_frame.pack(fill="x", padx=10, pady=5)
        
        self.record_button = ttk.Button(self.recorder_frame, text=translations[self.lang]["record_btn"], command=self.toggle_recording, bootstyle="danger")
        self.record_button.pack(fill="x", pady=5)
        
        reps_frame = ttk.Frame(self.recorder_frame)
        reps_frame.pack(fill="x", pady=5)
        self.reps_label = ttk.Label(reps_frame, text=translations[self.lang]["reps_label"])
        self.reps_label.pack(side="left")
        self.repeat_entry = ttk.Entry(reps_frame, width=10)
        self.repeat_entry.insert(0, "1")
        self.repeat_entry.pack(side="right")
        
        # AutoClicker Section
        self.clicker_frame = ttk.LabelFrame(self.root, text=translations[self.lang]["autoclicker"], padding=10, bootstyle="secondary")
        self.clicker_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_all_button = ttk.Button(self.clicker_frame, text=translations[self.lang]["start_all_btn"], command=self.start_all, bootstyle="success")
        self.start_all_button.pack(fill="x", pady=5)
        
        self.stop_all_button = ttk.Button(self.clicker_frame, text=translations[self.lang]["stop_all_btn"], command=self.stop_all, bootstyle="danger")
        self.stop_all_button.pack(fill="x", pady=5)

    def update_ui_text(self):
        t = translations[self.lang]
        self.root.title(t["title"])
        self.header_label.config(text=t["header"])
        self.status_label.config(text=f"Status: {t['ready']}")
        self.recorder_frame.config(text=t["recorder"])
        self.record_button.config(text=t["record_btn"] if not self.recording else t["stop_record_btn"])
        self.reps_label.config(text=t["reps_label"])
        self.clicker_frame.config(text=t["autoclicker"])
        self.start_all_button.config(text=t["start_all_btn"])
        self.stop_all_button.config(text=t["stop_all_btn"])

    def toggle_lang(self):
        self.lang = "en" if self.lang == "ru" else "ru"
        self.update_ui_text()

    def toggle_theme(self):
        current = self.style.theme_use()
        new_theme = "darkly" if current == "flatly" else "flatly"
        self.style.theme_use(new_theme)

    def update_status(self, text_key, bootstyle="info"):
        text = translations[self.lang].get(text_key, text_key)
        self.status_label.config(text=f"Status: {text}", bootstyle=bootstyle)

    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.events = []
            self.recording_start_time = time.time()
            self.record_button.config(text=translations[self.lang]["stop_record_btn"])
            self.update_status("Recording... (F8 to Stop)", "danger")
            
            self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move)
            self.keyboard_listener_in = pynput_keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.mouse_listener.start()
            self.keyboard_listener_in.start()
        else:
            self.recording = False
            self.mouse_listener.stop()
            self.keyboard_listener_in.stop()
            self.record_button.config(text=translations[self.lang]["record_btn"])
            self.update_status("recorded", "success")

    def toggle_autoclick_simple(self):
        if not self.autoclicking: self.start_autoclick_thread()
        else: self.stop_autoclick()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.events.append(('click', x, y, button, time.time() - self.recording_start_time))

    def on_move(self, x, y):
        self.events.append(('move', x, y, time.time() - self.recording_start_time))

    def on_press(self, key):
        self.events.append(('key_down', key, time.time() - self.recording_start_time))

    def on_release(self, key):
        self.events.append(('key_up', key, time.time() - self.recording_start_time))

    def start_all(self):
        self.start_replay_thread()
        self.start_autoclick_thread()
        self.update_status("autoclicking", "warning")

    def stop_all(self):
        self.replaying = False
        self.autoclicking = False
        self.update_status("ready", "info")

    def start_replay_thread(self):
        if self.events and not self.replaying:
            self.replaying = True
            threading.Thread(target=self.replay, daemon=True).start()
        elif not self.events:
            ttk.messagebox.showwarning(translations[self.lang]["warning"], translations[self.lang]["no_record"])

    def start_autoclick_thread(self):
        if not self.autoclicking:
            self.autoclicking = True
            threading.Thread(target=self.autoclick, daemon=True).start()
            
    def stop_autoclick(self):
        self.autoclicking = False

    def autoclick(self):
        mouse_controller = mouse.Controller()
        while self.autoclicking:
            mouse_controller.click(mouse.Button.left, 1)
            time.sleep(0.1)

    def replay(self):
        try:
            repetitions = int(self.repeat_entry.get())
        except ValueError:
            repetitions = 1
            
        mouse_controller = mouse.Controller()
        keyboard_controller = pynput_keyboard.Controller()
        
        count = 0
        while self.replaying and (repetitions == 0 or count < repetitions):
            start_time = time.time()
            for event in self.events:
                if not self.replaying: break
                
                event_type = event[0]
                event_time = event[-1]
                
                while time.time() - start_time < event_time:
                    time.sleep(0.01)
                    
                if event_type == 'click':
                    mouse_controller.position = (event[1], event[2])
                    mouse_controller.click(event[3])
                elif event_type == 'move':
                    mouse_controller.position = (event[1], event[2])
                elif event_type == 'key_down':
                    keyboard_controller.press(event[1])
                elif event_type == 'key_up':
                    keyboard_controller.release(event[1])
            count += 1
        self.replaying = False
        self.update_status("ready", "info")

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = AutoClickerApp(root)
    root.mainloop()
