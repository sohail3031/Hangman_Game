from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from words import word_list
from random import randint
from threading import Thread
from pynput.keyboard import Listener, Key
from string import ascii_lowercase


class HangmanWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_name, self.wrong_guessed_words, self.word = "", "", ""
        self.guess_left, self.hints_left = 5, 5
        self.score = 0
        self.button_pressed, self.underscores_list, self.correct_words = [], [], []
        self.letters = list(ascii_lowercase)
        self.running = True

    # Show hints
    def show_hint(self):
        if self.hints_left > 0:
            self.hints_left -= 1
            self.ids.show_hints.text = f"Hints: {self.hints_left}"
            for i in range(len(self.word)):
                if self.word[i] not in self.correct_words:
                    self.button_pressed.append(self.word[i])
                    self.check_word_pressed()
                    self.correct_words.append(self.word[i])
                    break
        else:
            self.running = False
            self.show_popup(title="No hints left", message="You don't have any hints left")

    # Change welcome screen to name screen
    def change_screen(self):
        self.ids.screen_manager.current = "main_screen"
        self.ids.user_name.focus = True

    # Show popup
    def show_popup(self, title, message):
        layout = GridLayout(cols=1, padding=10, spacing=10, size=self.size, pos=self.pos)
        popup_label = Label(text=message, font_size=20, bold=True, pos_hint={"center_x": .5, "center_y": .5})
        popup_button = Button(text="OK", size_hint_y=None, height=50, bold=True, font_size=20, background_normal="",
                              background_color=(.06, .47, .47, 1))
        layout.add_widget(popup_label)
        layout.add_widget(popup_button)
        popup = Popup(title=title, content=layout, size_hint=(None, None), size=(300, 300), auto_dismiss=False)
        popup.open()
        popup_button.bind(on_press=self.run_fun)
        popup_button.bind(on_press=popup.dismiss)

    def run_fun(self, *args):
        self.running = True

    # Check valid user name
    def valid_user_name(self):
        self.user_name = str(self.ids.user_name.text)

        if len(self.user_name) > 0:
            self.ids.screen_manager.current = "game_screen"
            self.ids.label_user_name.text = "Welcome " + self.user_name
            continuous = Thread(target=self.continuous)
            continuous.daemon = True
            continuous.start()
            self.play_game()
        else:
            self.show_popup(title="Invalid Username", message="Please provide a valid username")

    # For handling keyboard events
    def continuous(self):
        def on_press(key):
            pass

        def on_release(key):
            if self.running:
                if "Key" not in str(key):
                    if str(key)[1] in self.letters:
                        self.button_pressed.append(str(key)[1].upper())
                        self.check_word_pressed()
                    if key == Key.esc:
                        exit()

        # Collect events until released
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    # Start the game
    def play_game(self):
        get_word = word_list[randint(0, len(word_list))].upper()
        self.word = get_word
        underscores = "____    "
        self.ids.word_length_underscores.text = underscores * len(get_word)
        self.ids.word_length.text = str(len(get_word))
        self.ids.guess_left.text = str(self.guess_left)
        for i in range(len(get_word)):
            self.underscores_list.append(underscores)

    # Handling game keyboard events
    def text_button_pressed(self, instance):
        if self.running:
            self.button_pressed.append(instance.text)
            self.check_word_pressed()

    # Checking if the alphabet is present in the word or not
    def check_word_pressed(self):
        if self.running:
            new_word = self.button_pressed[len(self.button_pressed) - 1]

            if new_word in self.word:
                for i in range(len(self.word)):
                    if self.word[i] in new_word:
                        self.underscores_list[i] = new_word
                        self.correct_words.append(new_word)

                self.ids.word_length_underscores.text = "    ".join(self.underscores_list)
                result_str = "".join(self.underscores_list)

                if result_str == self.word:
                    self.score = self.score + len(self.word) - (5 - self.guess_left)
                    self.ids.display_score.text = f"Score: {str(self.score)}"
                    self.running = False
                    self.show_popup(title="Hurry! You Won", message=f"The word was {self.word}")
                    self.play_again()
            else:
                if self.guess_left == 1:
                    self.score = self.score + len(self.word) - (5 - self.guess_left)
                    self.ids.display_score.text = f"Score: {str(self.score)}"
                    self.running = False
                    self.show_popup(title="Oops Game Over", message=f"The word was {self.word}")
                    self.play_again()
                else:
                    if new_word not in self.wrong_guessed_words:
                        self.guess_left -= 1
                        self.wrong_guessed_words += new_word + " "
                        self.ids.wrong_guess.text = self.wrong_guessed_words
                        self.ids.guess_left.text = str(self.guess_left)

    # For play again
    def play_again(self):
        self.guess_left = 5
        self.wrong_guessed_words = self.word = self.ids.wrong_guess.text = ""
        self.button_pressed.clear()
        self.underscores_list.clear()
        self.play_game()


class HangmanApp(App):
    def build(self):
        self.title = "Hangman Game"
        Config.set('kivy', 'window_icon', 'images/hangman.jpg')
        return HangmanWindow()


if __name__ == "__main__":
    HangmanApp().run()
