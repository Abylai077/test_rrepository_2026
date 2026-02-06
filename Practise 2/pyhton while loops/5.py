secret_number = 7
guess = 0

while guess != secret_number:
    guess = int(input("Guess the number between 1 and 10: "))
    if guess < secret_number:
        print("Too low, try again!")
    elif guess > secret_number:
        print("Too high, try again!")
    else:
        print("Congratulations! You guessed it.")