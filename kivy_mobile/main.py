from kivy.app import App
from kivy.uix.label import Label

class JarvisMobileApp(App):
    def build(self):
        return Label(text='Hello from Jarvis Mobile!')

if __name__ == '__main__':
    JarvisMobileApp().run()