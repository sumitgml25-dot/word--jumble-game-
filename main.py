import random

words = {
    "python": "A programming language",
    "computer": "An electronic machine",
    "college": "A place for higher education"
}

def scramble_word(word):
    letters = list(word)
    random.shuffle(letters)
    return ''.join(letters)

def play_game():
    print("Word Jumble Game")
    print("Project structure created successfully.")

if __name__ == "__main__":
    play_game()
