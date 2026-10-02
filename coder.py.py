import tkinter as tk
from tkinter import scrolledtext
import hashlib
import base64
import os

try:
    from PIL import Image, ImageTk
    PILLOW = True
except ImportError:
    PILLOW = False

BG = "#1e1e1e"
FG = "#ffffff"
ACCENT = "#0088ff"
OK_COLOR = "#00ff88"
ERR_COLOR = "#ff4444"
INPUT_BG = "#2b2b2b"


def derive_key(password, length):
    key = b""
    counter = 0
    while len(key) < length:
        h = hashlib.sha256(password.encode("utf-8") + str(counter).encode()).digest()
        key += h
        counter += 1
    return key[:length]


def xor_bytes(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encrypt(text, password):
    data = text.encode("utf-8")
    key = derive_key(password, len(data) + 32)
    encrypted = xor_bytes(data, key)
    mixed = encrypted[::-1]
    encoded = base64.b64encode(mixed)
    return encoded.decode("utf-8")


def decrypt(cipher, password):
    try:
        data = base64.b64decode(cipher.encode("utf-8"))
        unmixed = data[::-1]
        key = derive_key(password, len(unmixed) + 32)
        decrypted = xor_bytes(unmixed, key)
        return decrypted.decode("utf-8")
    except Exception:
        return None


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Шифровальщик текста")
        self.root.geometry("900x750")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.logo_image = None
        self.build_ui()
        self.bind_shortcuts()

    def build_ui(self):
        title = tk.Label(
            self.root, text="🔐 ШИФРОВАЛЬЩИК ТЕКСТА",
            font=("Segoe UI", 22, "bold"), fg=FG, bg=BG
        )
        title.pack(pady=15)

        subtitle = tk.Label(
            self.root, text="Алгоритм: SHA-256 + XOR + Base64",
            font=("Segoe UI", 11), fg="#888888", bg=BG
        )
        subtitle.pack()

        frame = tk.Frame(self.root, bg=BG)
        frame.pack(padx=30, pady=20, fill="both", expand=True)

        tk.Label(
            frame, text="ИСХОДНЫЙ ТЕКСТ (Ctrl+V — вставить):",
            font=("Segoe UI", 11, "bold"), fg=FG, bg=BG
        ).pack(anchor="w")

        self.input_text = scrolledtext.ScrolledText(
            frame, height=8, font=("Consolas", 11),
            bg=INPUT_BG, fg=FG, insertbackground=FG,
            relief="flat", bd=5, wrap="word"
        )
        self.input_text.pack(fill="x", pady=5)

        tk.Label(
            frame, text="ПАРОЛЬ:",
            font=("Segoe UI", 11, "bold"), fg=FG, bg=BG
        ).pack(anchor="w", pady=(10, 0))

        self.password_entry = tk.Entry(
            frame, font=("Consolas", 13),
            bg=INPUT_BG, fg=FG, insertbackground=FG,
            relief="flat", bd=5
        )
        self.password_entry.pack(fill="x", pady=5)

        btn_frame = tk.Frame(frame, bg=BG)
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame, text="🔒 ЗАШИФРОВАТЬ",
            font=("Segoe UI", 12, "bold"),
            bg=ACCENT, fg="white",
            activebackground="#0066cc", activeforeground="white",
            relief="flat", padx=20, pady=10,
            command=self.do_encrypt
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frame, text="🔓 РАСШИФРОВАТЬ",
            font=("Segoe UI", 12, "bold"),
            bg="#444444", fg="white",
            activebackground="#555555", activeforeground="white",
            relief="flat", padx=20, pady=10,
            command=self.do_decrypt
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frame, text="📋 КОПИРОВАТЬ",
            font=("Segoe UI", 12, "bold"),
            bg="#008844", fg="white",
            activebackground="#006633", activeforeground="white",
            relief="flat", padx=20, pady=10,
            command=self.do_copy
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frame, text="🗑 ОЧИСТИТЬ",
            font=("Segoe UI", 12, "bold"),
            bg="#444444", fg="white",
            activebackground="#555555", activeforeground="white",
            relief="flat", padx=20, pady=10,
            command=self.do_clear
        ).pack(side="left", padx=8)

        tk.Label(
            frame, text="РЕЗУЛЬТАТ (Ctrl+V — вставить сюда, ПКМ — копировать):",
            font=("Segoe UI", 11, "bold"), fg=FG, bg=BG
        ).pack(anchor="w", pady=(10, 0))

        self.output_text = scrolledtext.ScrolledText(
            frame, height=8, font=("Consolas", 11),
            bg=INPUT_BG, fg=OK_COLOR, insertbackground=FG,
            relief="flat", bd=5, wrap="word"
        )
        self.output_text.pack(fill="x", pady=5)

        self.status = tk.Label(
            self.root, text="Готов к работе",
            font=("Segoe UI", 11), fg="#888888", bg=BG
        )
        self.status.pack(pady=5)

        bottom_frame = tk.Frame(self.root, bg=BG)
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=10)

        self.credit = tk.Label(
            bottom_frame, text="Сделал Черкасов Даниэль",
            font=("Segoe UI", 11, "bold"), fg="#ffcc00", bg=BG
        )
        self.credit.pack(side="left")

        self.load_logo(bottom_frame)

    def load_logo(self, parent):
        for name in ("logo.png", "logo.jpg", "logo.jpeg", "logo.gif", "logo.PNG", "logo.JPG"):
            if os.path.exists(name):
                try:
                    if PILLOW:
                        img = Image.open(name)
                        img = img.resize((100, 100))
                        self.logo_image = ImageTk.PhotoImage(img)
                    else:
                        self.logo_image = tk.PhotoImage(file=name)

                    logo_label = tk.Label(parent, image=self.logo_image, bg=BG)
                    logo_label.pack(side="right")
                    return
                except Exception:
                    continue

    def bind_shortcuts(self):
        for widget in (self.input_text, self.output_text, self.password_entry):
            widget.bind("<Control-KeyPress>", self.on_ctrl_key)
            widget.bind("<Button-3>", self.on_right_click)

    def on_ctrl_key(self, event):
        code = event.keycode
        w = event.widget

        if code == 86:
            return self.paste_to_widget(w)
        elif code == 67:
            return self.copy_from_widget(w)
        elif code == 88:
            return self.cut_from_widget(w)
        elif code == 65:
            return self.select_all_widget(w)
        elif code == 76:
            self.do_clear()
            return "break"
        return None

    def on_right_click(self, event):
        w = event.widget
        if w is self.output_text:
            self.output_text.event_generate("<<Copy>>")
            text = self.output_text.get("1.0", "end").strip()
            self.set_status(f"✅ Скопировано ({len(text)} симв.)", OK_COLOR)
        elif w is self.input_text:
            self.input_text.event_generate("<<Paste>>")
            self.set_status("✅ Вставлено", OK_COLOR)
        elif w is self.password_entry:
            self.password_entry.event_generate("<<Paste>>")
            self.set_status("✅ Вставлено", OK_COLOR)

    def paste_to_widget(self, w):
        try:
            text = self.root.clipboard_get()
        except Exception:
            self.set_status("Буфер обмена пуст", ERR_COLOR)
            return "break"

        if isinstance(w, tk.Text):
            try:
                w.delete("sel.first", "sel.last")
            except Exception:
                pass
            w.insert("insert", text)
        elif isinstance(w, tk.Entry):
            try:
                w.delete("sel.first", "sel.last")
            except Exception:
                pass
            w.insert("insert", text)

        self.set_status(f"✅ Вставлено ({len(text)} симв.)", OK_COLOR)
        return "break"

    def copy_from_widget(self, w):
        try:
            if isinstance(w, tk.Text):
                try:
                    text = w.get("sel.first", "sel.last")
                except Exception:
                    text = w.get("1.0", "end").strip()
            else:
                try:
                    text = w.selection_get()
                except Exception:
                    text = w.get()
        except Exception:
            text = ""

        if not text:
            self.set_status("Нечего копировать", ERR_COLOR)
            return "break"

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            self.set_status(f"✅ Скопировано ({len(text)} симв.)", OK_COLOR)
        except Exception as e:
            self.set_status(f"Ошибка: {e}", ERR_COLOR)
        return "break"

    def cut_from_widget(self, w):
        text = ""
        try:
            if isinstance(w, tk.Text):
                try:
                    text = w.get("sel.first", "sel.last")
                except Exception:
                    text = ""
                if text:
                    w.delete("sel.first", "sel.last")
            else:
                try:
                    text = w.selection_get()
                except Exception:
                    text = ""
                if text:
                    w.delete("sel.first", "sel.last")
        except Exception:
            return "break"

        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            self.set_status(f"✂ Вырезано ({len(text)} симв.)", OK_COLOR)
        return "break"

    def select_all_widget(self, w):
        if isinstance(w, tk.Text):
            w.tag_add("sel", "1.0", "end")
            w.mark_set("insert", "1.0")
        elif isinstance(w, tk.Entry):
            w.select_range(0, "end")
            w.icursor("end")
        return "break"

    def do_encrypt(self):
        text = self.input_text.get("1.0", "end").strip()
        password = self.password_entry.get().strip()

        if not text:
            self.set_status("Введи текст для шифрования!", ERR_COLOR)
            return
        if not password:
            self.set_status("Введи пароль!", ERR_COLOR)
            return

        result = encrypt(text, password)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", result)
        self.set_status(f"Зашифровано! Длина: {len(result)} символов", OK_COLOR)

    def do_decrypt(self):
        text = self.input_text.get("1.0", "end").strip()
        password = self.password_entry.get().strip()

        if not text:
            self.set_status("Введи зашифрованный текст!", ERR_COLOR)
            return
        if not password:
            self.set_status("Введи пароль!", ERR_COLOR)
            return

        result = decrypt(text, password)
        if result is None:
            self.output_text.delete("1.0", "end")
            self.set_status("Неверный пароль или повреждённый текст!", ERR_COLOR)
        else:
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", result)
            self.set_status("Расшифровано успешно!", OK_COLOR)

    def do_copy(self):
        text = self.output_text.get("1.0", "end").strip()
        if not text:
            self.set_status("Нет текста для копирования!", ERR_COLOR)
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            self.set_status(f"✅ Скопировано ({len(text)} симв.)", OK_COLOR)
        except Exception as e:
            self.set_status(f"Ошибка: {e}", ERR_COLOR)

    def do_clear(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.password_entry.delete(0, "end")
        self.set_status("Очищено", "#888888")

    def set_status(self, text, color):
        self.status.config(text=text, fg=color)


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()