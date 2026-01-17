from datetime import datetime

def greet():
    return "नमस्ते। म वाणी हुँ।"

def time_now():
    return f"अहिले समय {datetime.now().strftime('%H:%M')} हो।"

def exit_reply():
    return "ठिक छ। फेरि भेटौँला।"

def unknown():
    return "म बुझ्दैछु, तर यो सुविधा अहिले तयार छैन।"