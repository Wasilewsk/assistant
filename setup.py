from setuptools import setup, find_packages

setup(
    name="Project-Cortana",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "pyttsx3",
        "SpeechRecognition",
        "PyAudio",
        "pywhatkit",
        "wikipedia",
        "requests",
        "beautifulsoup4",
        "PyPDF2",
        "python-docx",
        "pytesseract",
        "Pillow",
        "pyperclip",
        "feedparser",
        "pycaw",
        "comtypes",
    ],
    url="https://github.com/skywalkerSam/Project-Cortana",
    license="MIT",
    author="Starboy",
    author_email="starboy@skywalkersam.dev",
    description="Project-Cortana - Voice assistant for the blind.",
)
