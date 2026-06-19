import os
import pyperclip
import app.config as config
import app.speaker as speaker

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

def resolve_path(filename):
    if os.path.isabs(filename):
        return filename
    candidate = os.path.join(config.current_dir, filename)
    if os.path.exists(candidate):
        return candidate
    for base in [os.getcwd(), os.path.expanduser("~")]:
        candidate = os.path.join(base, filename)
        if os.path.exists(candidate):
            return candidate
    return None

def read_text_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.strip():
            return "The file is empty."
        return content
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
            return content
        except Exception:
            return "Could not read the file. It may be a binary file."

def read_pdf(filepath):
    if not HAS_PDF:
        return "PDF reading is not available. Install PyPDF2: pip install PyPDF2"
    try:
        text = []
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        content = "\n".join(filter(None, text))
        return content if content.strip() else "No readable text found in the PDF."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def read_docx(filepath):
    if not HAS_DOCX:
        return "Word document reading is not available. Install python-docx: pip install python-docx"
    try:
        doc = docx.Document(filepath)
        text = "\n".join(p.text for p in doc.paragraphs)
        return text if text.strip() else "The document appears to be empty."
    except Exception as e:
        return f"Error reading Word document: {str(e)}"

def read_image(filepath):
    if not HAS_OCR:
        return "OCR is not available. Install pytesseract and Pillow: pip install pytesseract Pillow, and install Tesseract from github.com/UB-Mannheim/tesseract/wiki"
    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else "No text found in the image."
    except Exception as e:
        return f"Error reading image: {str(e)}"

def read_clipboard():
    try:
        text = pyperclip.paste()
        if text and text.strip():
            return text.strip()
        return "The clipboard is empty."
    except Exception:
        return "Could not access the clipboard."

def handle_read_command(command):
    cmd = command.lower()

    if "clipboard" in cmd:
        text = read_clipboard()
        speaker.speak(text)
        return True

    if "pdf" in cmd:
        parts = cmd.replace("read", "").replace("pdf", "").strip()
        path = resolve_path(parts) if parts else None
        if path:
            speaker.speak(f"Reading PDF: {os.path.basename(path)}")
            text = read_pdf(path)
            speaker.speak(text[:2000])
        else:
            speaker.speak("Which PDF file should I read?")
        return True

    if "word" in cmd or " doc" in cmd:
        parts = cmd.replace("read", "").replace("word", "").replace("doc", "").strip()
        path = resolve_path(parts) if parts else None
        if path:
            speaker.speak(f"Reading document: {os.path.basename(path)}")
            text = read_docx(path)
            speaker.speak(text[:2000])
        else:
            speaker.speak("Which Word document should I read?")
        return True

    if "image" in cmd or "picture" in cmd or "photo" in cmd or "scan" in cmd:
        parts = cmd.replace("read", "").replace("image", "").replace("picture", "").replace("photo", "").replace("scan", "").strip()
        path = resolve_path(parts) if parts else None
        if path:
            speaker.speak(f"Reading text from image: {os.path.basename(path)}")
            text = read_image(path)
            speaker.speak(text[:2000])
        else:
            speaker.speak("Which image file should I read?")
        return True

    if "read" in cmd:
        parts = cmd.replace("read", "").strip()
        if parts and not any(w in parts for w in ["the", "a ", "my "]):
            path = resolve_path(parts)
            if path and os.path.isfile(path):
                speaker.speak(f"Reading file: {os.path.basename(path)}")
                text = read_text_file(path)
                speaker.speak(text[:2000])
                return True
        speaker.speak("I can read text files, PDFs, Word documents, images, or the clipboard. Try: read clipboard, read PDF filename, read image filename, or read filename.txt")
        return True

    return False

def handle_file_navigation(command):
    import app.config as config
    cmd = command.lower()

    if "list files" in cmd or "show files" in cmd:
        try:
            items = [f for f in os.listdir(config.current_dir) if os.path.isfile(os.path.join(config.current_dir, f))]
            if items:
                names = ", ".join(items[:20])
                speaker.speak(f"Files in current directory: {names}")
                if len(items) > 20:
                    speaker.speak(f"And {len(items) - 20} more files.")
            else:
                speaker.speak("No files in the current directory.")
        except Exception as e:
            speaker.speak(f"Error listing files: {str(e)}")
        return True

    if "list folders" in cmd or "list directories" in cmd or "show folders" in cmd:
        try:
            items = [f for f in os.listdir(config.current_dir) if os.path.isdir(os.path.join(config.current_dir, f))]
            if items:
                names = ", ".join(items[:20])
                speaker.speak(f"Folders: {names}")
                if len(items) > 20:
                    speaker.speak(f"And {len(items) - 20} more folders.")
            else:
                speaker.speak("No folders in the current directory.")
        except Exception as e:
            speaker.speak(f"Error listing folders: {str(e)}")
        return True

    if "where am i" in cmd or "current directory" in cmd or "current folder" in cmd:
        speaker.speak(f"You are in {config.current_dir}")
        return True

    if "go to" in cmd or "open folder" in cmd or "change directory" in cmd:
        parts = cmd.replace("go to", "").replace("open folder", "").replace("change directory", "").strip()
        if parts:
            target = resolve_path(parts)
            if target and os.path.isdir(target):
                config.current_dir = target
                speaker.speak(f"Moved to {target}")
            else:
                speaker.speak(f"Folder not found: {parts}")
        return True

    if "go back" in cmd or "parent folder" in cmd or "go up" in cmd:
        parent = os.path.dirname(config.current_dir)
        if parent and parent != config.current_dir:
            config.current_dir = parent
            speaker.speak(f"Moved back to {config.current_dir}")
        else:
            speaker.speak("Already at the root directory.")
        return True

    if "go home" in cmd:
        config.current_dir = config.home_dir
        speaker.speak(f"Moved to home directory: {config.home_dir}")
        return True

    return False
