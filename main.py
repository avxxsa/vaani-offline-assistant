from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from brain.brain import process_text

class VaaniApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        self.input = TextInput(hint_text="Say something...")
        self.output = Label(text="Response here")

        btn = Button(text="Ask")
        btn.bind(on_press=self.ask)

        layout.add_widget(self.input)
        layout.add_widget(btn)
        layout.add_widget(self.output)
        return layout

    def ask(self, instance):
        text = self.input.text
        response = process_text(text)
        self.output.text = response

VaaniApp().run()