import os
import sys
import re
import threading
import shutil
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import ffmpeg

# --- PORTABLE PATH SETTINGS ---
def get_base_path():
    """Finds the base directory (works for both EXE and Script)"""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()

try:
    import rawpy
    RAW_SUPPORT = True
except ImportError:
    RAW_SUPPORT = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_SUPPORT = True
except ImportError:
    PDF2IMAGE_SUPPORT = False

try:
    from fontTools.ttLib import TTFont
    FONT_SUPPORT = True
except ImportError:
    FONT_SUPPORT = False

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# -----------------------------------------------------------------------
# CONSTANTS (English)
# -----------------------------------------------------------------------
LIBREOFFICE_PATH = os.path.join(BASE_PATH, "LibreOffice", "program", "soffice.exe")

RAW_FORMATS      = {".cr2", ".nef", ".arw", ".dng", ".orf", ".sr2"}
IMAGE_FORMATS    = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".ico"} | RAW_FORMATS
MEDIA_FORMATS    = {".mp4", ".mkv", ".mp3", ".wav", ".opus", ".avi", ".mov", ".m4a", ".flac"}
PRESENTATION_FMT = {".pptx", ".ppt", ".odp"}
SPREADSHEET_FMT  = {".xlsx", ".xls", ".ods", ".csv"}
TEXT_FORMATS     = {".docx", ".doc", ".odt", ".txt", ".html"}
PDF_FORMAT       = {".pdf"}
FONT_FORMATS     = {".ttf", ".otf", ".woff", ".woff2"}
OFFICE_FORMATS   = PRESENTATION_FMT | SPREADSHEET_FMT | TEXT_FORMATS

VIDEO_EXTS       = {".mp4", ".mkv", ".avi", ".mov"}
AUDIO_EXTS       = {".mp3", ".wav", ".opus", ".m4a", ".flac"}

TARGET_IMAGE     = {"jpg", "jpeg", "png", "webp", "gif", "ico"}
TARGET_VIDEO     = {"mp4", "mkv"}
TARGET_AUDIO     = {"mp3", "wav", "opus", "m4a", "flac"}
TARGET_MEDIA     = TARGET_VIDEO | TARGET_AUDIO
TARGET_PRES      = {"pptx", "odp"}
TARGET_SHEET     = {"xlsx"}
TARGET_TEXT      = {"docx", "txt", "html"}
TARGET_PDF       = {"pdf"}
TARGET_OFFICE    = TARGET_PRES | TARGET_SHEET | TARGET_TEXT | TARGET_PDF
TARGET_FONT      = {"ttf", "otf", "woff", "woff2"}

FONT_FLAVOR = {
    "ttf":   None,
    "otf":   None,
    "woff":  "woff",
    "woff2": "woff2",
}

def validation_check(ext: str, target: str) -> str | None:
    if ext == f".{target}":
        return "Source and target formats are identical"

    r   = ext in IMAGE_FORMATS
    mv  = ext in VIDEO_EXTS
    ms  = ext in AUDIO_EXTS
    s   = ext in PRESENTATION_FMT
    t   = ext in SPREADSHEET_FMT
    mt  = ext in TEXT_FORMATS
    txt = ext == ".txt"
    htm = ext == ".html"
    p   = ext in PDF_FORMAT
    fnt = ext in FONT_FORMATS

    hr  = target in TARGET_IMAGE
    hv  = target in TARGET_VIDEO
    hs_s= target in TARGET_AUDIO
    hs  = target in TARGET_PRES
    ht  = target in TARGET_SHEET
    hmt = target in TARGET_TEXT
    hp  = target in TARGET_PDF
    hf  = target in TARGET_FONT

    if r and (hr or hp):                         return None
    if ext == ".gif" and hv:                    return None
    if mv and (hv or hs_s):                      return None
    if ms and hs_s:                              return None
    if ms and hv:
        return "Audio files cannot be converted to video (no video stream)"
    if p and (hr or hs or hmt or ht or hp):      return None
    if mt and not txt and not htm and (hp or hmt or hs): return None
    if txt and (hp or hmt or hhtm):              return None
    if htm and (hp or hmt):                      return None
    if s and (hp or hs):                         return None
    if t and (hp or ht):                         return None
    if fnt and hf:                               return None

    return f"Target '{target}' is not supported for '{ext}' files"

class CustomInfo(ctk.CTkToplevel):
    def __init__(self, parent, title, message, is_error=False):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry("440x280")
        self.attributes("-topmost", True)
        self.overrideredirect(True)

        x = parent.winfo_x() + (parent.winfo_width()  // 2) - 220
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 140
        self.geometry(f"+{x}+{y}")
        self.configure(fg_color="#1e1e1e" if not is_error else "#2c1a1a")

        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=2, pady=2)
        color = "#e74c3c" if is_error else "#3B8ED0"
        ctk.CTkLabel(f, text=title, font=("Arial", 18, "bold"),
                     text_color=color).pack(pady=(20, 8))
        lbl = ctk.CTkLabel(f, text=message, wraplength=400,
                           font=("Arial", 13), justify="center")
        lbl.pack(pady=8, padx=20)
        ctk.CTkLabel(f, text="(Click to close)",
                     font=("Arial", 10, "italic"),
                     text_color="gray").pack(side="bottom", pady=10)

        for w in [self, f, lbl]:
            w.bind("<Button-1>", lambda e: self._close())
        self._bid = parent.bind("<Any-ButtonPress>", lambda e: self._close(), add="+")
        self.after(6000, self._close)

    def _close(self):
        try:   self.parent.unbind("<Any-ButtonPress>", self._bid)
        except: pass
        try:   self.destroy()
        except: pass

class FilenorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Filenor: Optimize Formatter")
        self.geometry("860x700")
        self.minsize(700, 650)

        self.file_paths       = []
        self.converted_temp   = []
        self.error_files      = {}
        self.last_dir         = os.path.join(os.path.expanduser("~"), "Downloads")
        self.tooltip          = None

        ctk.CTkLabel(self, text="FILENOR", font=("Arial", 32, "bold"),
                     text_color="#3B8ED0").pack(pady=(18, 5))

        ctk.CTkButton(self, text="+ Add Files", command=self.add_files,
                      fg_color="#2980b9", width=300).pack(pady=5)

        self.list_frame = ctk.CTkScrollableFrame(
            self, label_text="Files to Process")
        self.list_frame.pack(pady=10, padx=40, fill="both", expand=True)

        self._format_categories = {
            "🖼️  Image":   ["jpg", "jpeg", "png", "webp", "gif", "ico"],
            "🎬  Video":   ["mp4", "mkv"],
            "🎵  Audio":   ["mp3", "wav", "opus", "m4a", "flac"],
            "📄  Document":["pdf", "docx", "txt", "html"],
            "📊  Sheet":   ["xlsx"],
            "📽️  Slide":   ["pptx", "odp"],
            "🔤  Font":    ["ttf", "otf", "woff", "woff2"],
        }
        self._selected_format = ctk.StringVar(value="")
        self._selected_category = None

        cat_panel = ctk.CTkFrame(self, fg_color="transparent")
        cat_panel.pack(pady=(8, 0))

        self._cat_buttons = {}
        for cat in self._format_categories:
            btn = ctk.CTkButton(
                cat_panel, text=cat, width=108, height=32,
                fg_color="#2c3e50", hover_color="#34495e",
                font=("Arial", 11),
                command=lambda k=cat: self._select_category(k)
            )
            btn.pack(side="left", padx=2)
            self._cat_buttons[cat] = btn

        self._sub_fmt_panel = ctk.CTkFrame(self, fg_color="transparent")
        self._sub_fmt_panel.pack(pady=4)

        self._format_label = ctk.CTkLabel(
            self, text="⬆  Select a category first",
            font=("Arial", 11, "italic"), text_color="gray"
        )
        self._format_label.pack(pady=(0, 4))

        ctk.CTkButton(self, text="Start Conversion", fg_color="green",
                      command=self.start_conversion, width=300).pack(pady=8)

        self.bottom_panel = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkButton(self.bottom_panel, text="Download Result",
                      fg_color="#3498db", command=self.download_files,
                      width=145).pack(side="left", padx=5)
        ctk.CTkButton(self.bottom_panel, text="Open Folder",
                      fg_color="#e67e22", command=self.open_folder,
                      width=145).pack(side="left", padx=5)

        self.lbl_status = ctk.CTkLabel(self, text="Status: Waiting...",
                                      font=("Arial", 12, "italic"))
        self.lbl_status.pack(side="bottom", pady=8)

    def msg(self, title, text, err=False):
        CustomInfo(self, title, text, err)

    def _lo_exists(self):
        return os.path.exists(LIBREOFFICE_PATH)

    def _select_category(self, category):
        for k, btn in self._cat_buttons.items():
            btn.configure(fg_color="#3B8ED0" if k == category else "#2c3e50")
        self._selected_category = category
        self._selected_format.set("")
        self._format_label.configure(text="⬆  Select a format", text_color="gray")
        for w in self._sub_fmt_panel.winfo_children(): w.destroy()
        for fmt in self._format_categories[category]:
            btn = ctk.CTkButton(
                self._sub_fmt_panel, text=fmt.upper(), width=75, height=28,
                fg_color="#1a3a1a", hover_color="#27ae60",
                font=("Arial", 11, "bold"),
                command=lambda f=fmt: self._select_format(f)
            )
            btn.pack(side="left", padx=3)

    def _select_format(self, fmt):
        self._selected_format.set(fmt)
        for w in self._sub_fmt_panel.winfo_children():
            is_selected = w.cget("text").lower() == fmt
            w.configure(fg_color="#27ae60" if is_selected else "#1a3a1a")
        self._format_label.configure(text=f"✔  Selected format: {fmt.upper()}", text_color="#2ecc71")

    def validate_format(self, path, target):
        ext = os.path.splitext(path)[1].lower()
        error = validation_check(ext, target)
        if error: return error
        if ext in PDF_FORMAT and target in TARGET_IMAGE and not PDF2IMAGE_SUPPORT:
            return "PDF → Image requires 'pdf2image' and Poppler installed"
        if ext in FONT_FORMATS and target in TARGET_FONT and not FONT_SUPPORT:
            return "Font conversion requires 'fonttools' installed"
        lo_required = ((ext in OFFICE_FORMATS and target in TARGET_OFFICE) or 
                       (ext in PDF_FORMAT and target in TARGET_OFFICE) or 
                       (ext == ".html" and target == "pdf"))
        if lo_required and not self._lo_exists():
            return "LibreOffice folder not found on USB."
        return None

    def update_list(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        for idx, path in enumerate(self.file_paths):
            has_error = path in self.error_files
            f = ctk.CTkFrame(self.list_frame, fg_color="#3a1a1a" if has_error else "transparent")
            f.pack(fill="x", pady=2, padx=5)
            left = ctk.CTkFrame(f, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True, padx=5, pady=4)
            top = ctk.CTkFrame(left, fg_color="transparent")
            top.pack(fill="x")
            if has_error: ctk.CTkLabel(top, text="⚠️", font=("Arial", 14), text_color="orange").pack(side="left", padx=(5, 2))
            ctk.CTkLabel(top, text=os.path.basename(path), anchor="w", font=("Arial", 12)).pack(side="left", padx=2)
            if has_error: ctk.CTkLabel(left, text=f"  ✖ {self.error_files[path]}", text_color="#e07070", font=("Arial", 10, "italic"), anchor="w", wraplength=420).pack(fill="x", padx=5)
            ctk.CTkButton(f, text="X", width=35, fg_color="#c0392b", hover_color="#e74c3c", command=lambda i=idx: self.remove_file(i)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="🔍", width=35, fg_color="#34495e", hover_color="#2c3e50", command=lambda p=path: self.preview_file(p)).pack(side="right", padx=5)

    def preview_file(self, path):
        try:
            if os.name == "nt": os.startfile(path)
            else: subprocess.run(["xdg-open", path])
        except Exception as e: self.msg("Error", f"Could not open: {e}", True)

    def add_files(self):
        new_files = filedialog.askopenfilenames(title="Filenor - Add Files")
        if new_files:
            for f in new_files:
                if f not in self.file_paths: self.file_paths.append(f)
            self.error_files.clear()
            self.update_list()
            self.bottom_panel.pack_forget()

    def remove_file(self, i):
        path = self.file_paths.pop(i)
        self.error_files.pop(path, None)
        self.update_list()

    def start_conversion(self):
        if not self.file_paths: return
        target = self._selected_format.get().lower()
        if not target:
            self.msg("Format Not Selected", "Please select a target format first.", True)
            return
        self.error_files.clear()
        valid = False
        for path in self.file_paths:
            err = self.validate_format(path, target)
            if err: self.error_files[path] = err
            else: valid = True
        self.update_list()
        if not valid:
            self.msg("Process Denied", "None of the selected files are compatible with the target format.", True)
            return
        self.lbl_status.configure(text="Status: Processing...")
        threading.Thread(target=self.process_loop, args=(target,), daemon=True).start()

    def process_loop(self, target):
        success_list = []
        temp_dir = os.path.join(os.environ.get("TEMP", "/tmp"), "Filenor")
        os.makedirs(temp_dir, exist_ok=True)
        for path in self.file_paths:
            if path in self.error_files: continue
            name = os.path.splitext(os.path.basename(path))[0]
            output = os.path.join(temp_dir, f"{name}.{target}")
            ext = os.path.splitext(path)[1].lower()
            try:
                if ext in RAW_FORMATS and target in TARGET_IMAGE:
                    with rawpy.imread(path) as raw: rgb = raw.postprocess(use_camera_wb=True)
                    Image.fromarray(rgb).save(output)
                elif ext in IMAGE_FORMATS and target in TARGET_IMAGE:
                    img = Image.open(path)
                    if ext == ".gif" and target != "gif": img.seek(0)
                    if target in {"jpg", "jpeg"} and img.mode in {"RGBA", "P", "L"}: img = img.convert("RGB")
                    img.save(output)
                elif ext in IMAGE_FORMATS and target == "pdf":
                    img = Image.open(path)
                    if img.mode in {"RGBA", "P"}: img = img.convert("RGB")
                    img.save(output, "PDF")
                elif ext == ".gif" and target in TARGET_VIDEO:
                    stream = ffmpeg.input(path)
                    ffmpeg.output(stream, output, vcodec="libx264", pix_fmt="yuv420p", crf=23).run(overwrite_output=True, quiet=True)
                elif ext in MEDIA_FORMATS and target in TARGET_MEDIA:
                    self._ffmpeg_convert(path, output, ext, target)
                elif ext in PDF_FORMAT and target in TARGET_IMAGE:
                    pages = convert_from_path(path, dpi=150)
                    if len(pages) == 1: pages[0].save(output)
                    else:
                        for i, pg in enumerate(pages, 1):
                            sp = os.path.join(temp_dir, f"{name}_page{i}.{target}")
                            pg.save(sp)
                            success_list.append(sp)
                        continue
                elif ext == ".txt" and target == "pdf": self._txt_to_pdf(path, output)
                elif (ext in PDF_FORMAT or ext in OFFICE_FORMATS) and target in TARGET_OFFICE:
                    self._libreoffice(path, temp_dir, target, output)
                elif ext in FONT_FORMATS and target in TARGET_FONT: self._font_convert(path, output, target)
                else: raise ValueError("Conversion engine error")
                success_list.append(output)
            except Exception as e: self.error_files[path] = str(e)
        self.converted_temp = success_list
        self.after(0, self.process_finished)

    def _ffmpeg_convert(self, source, output, source_ext, target):
        mv = source_ext in VIDEO_EXTS
        inp = ffmpeg.input(source)
        if target in TARGET_AUDIO:
            aud = inp.audio if mv else inp
            ffmpeg.output(aud, output).run(overwrite_output=True, quiet=True)
        elif target in TARGET_VIDEO:
            ffmpeg.output(inp, output, vcodec="libx264", acodec="aac", pix_fmt="yuv420p").run(overwrite_output=True, quiet=True)

    def _libreoffice(self, source, temp, target, expected):
        flags = 0x08000000 if os.name == "nt" else 0
        subprocess.run([LIBREOFFICE_PATH, "--headless", "--convert-to", target, source, "--outdir", temp], creationflags=flags, check=True)
        name = os.path.splitext(os.path.basename(source))[0]
        actual = os.path.join(temp, f"{name}.{target}")
        if os.path.exists(actual) and actual != expected: os.replace(actual, expected)

    def _txt_to_pdf(self, source, output):
        from PIL import ImageDraw
        with open(source, "r", encoding="utf-8", errors="replace") as f: lines = f.readlines()
        pg = Image.new("RGB", (794, 1123), "white")
        draw = ImageDraw.Draw(pg)
        y = 40
        for line in lines:
            draw.text((40, y), line.strip(), fill="black")
            y += 20
        pg.save(output, "PDF")

    def _font_convert(self, source, output, target):
        font = TTFont(source)
        font.flavor = FONT_FLAVOR.get(target)
        font.save(output)

    def process_finished(self):
        self.update_list()
        n_ok = len(self.converted_temp)
        self.lbl_status.configure(text=f"Status: {n_ok} files processed successfully.")
        if n_ok > 0: self.bottom_panel.pack(pady=15)

    def download_files(self):
        target = filedialog.askdirectory(initialdir=self.last_dir)
        if target:
            for d in self.converted_temp: shutil.copy(d, target)
            self.msg("Success", "Files saved successfully.")

    def open_folder(self):
        if os.path.exists(self.last_dir): os.startfile(self.last_dir)

if __name__ == "__main__":
    FilenorApp().mainloop()
