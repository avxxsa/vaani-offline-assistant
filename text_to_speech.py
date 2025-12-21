import pyttsx3

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)

        voices = self.engine.getProperty("voices")
        self.engine.setProperty('voice', voices[1].id)


    def speak(self, text):
        print ("Vaani:", text)
        self.engine.say(text)
        self.engine.runAndWait()
