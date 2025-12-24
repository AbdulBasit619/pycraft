lower_case = list("abcdefghijklmnopqrstuvwxyz")
upper_case = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

all_case = []
for i in range(len(lower_case)):
    all_case.append(upper_case[i])
    all_case.append(lower_case[i])


class Encrypt:
    """
    This class is a blueprint to create an encrypted object from plaintext (alphabets only).

    plain_text is the text to be encrypted

    mode (optional) is the mode in which to encrypt the text:
    1. mode == 0 (Encryption in uppercase, default)
    2. mode == 1 (Encryption in lowercase)
    3. mode == 2 (Encryption using the combination of both cases)
    """

    def __init__(self, plain_text, mode=0):
        # plaintext is the text that is to be encrypted. It should contain only uppercase or lowercase letters, or both.. No other characters (space, period, etc.) are allowed!
        if not plain_text.isalpha():
            raise ValueError(
                "Please ensure that the text contains only lowercase or uppercase alphabets! No other characters are allowed!"
            )
        self.plain_text = plain_text

        # mode defines whether plain_text is to be encrypted using uppercase letters (mode == 0), lowercase letters (mode == 1) or both (mode == 2).
        self.mode = mode

    def encrypt(self, key=1):
        """
        Encrypt the message using the key and mode as specified by user

        Key defines the length by which the letters are to be shifted.
        Positive value means shift right, left otherwise
        Can take on values 1 (default) to 25.
        """

        # Check if key lies in valid range of 1:25 or -25:-1
        if key == 0 or key < -25 or key > 25:
            raise ValueError(
                "Please enter the key in the correct range of 1 (default) to 25, or -1 to -25."
            )

        # Check for mode. If incorrect value, raise valueError and terminate immediately
        if self.mode == 0:
            case = upper_case
        elif self.mode == 1:
            case = lower_case
        elif self.mode == 2:
            case = all_case
        else:
            raise ValueError(
                "Please correctly enter the mode (0 for uppercase, 1 for lowercase and 2 for both)."
            )

        # Check if the case of user supplied input and the case of the mode in which the encryption is to be done is the same
        # If not, raise ValueError and terminate immediately
        if self.mode == 0 and not self.plain_text.isupper():
            raise ValueError(
                "Cannot encrypt uppercase mode: input is not uppercase or some characters are not letters."
            )
        elif self.mode == 1 and not self.plain_text.islower():
            raise ValueError(
                "Cannot encrypt lowercase mode: input is not lowercase or some characters are not letters."
            )
        elif self.mode == 2 and not any(c.isalpha() for c in self.plain_text):
            raise ValueError(
                "Cannot encrypt mixed-case mode: input contains no letters."
            )

        encrypted_message = ""

        for char in self.plain_text:
            for i, letter in enumerate(case):
                if case == lower_case or case == upper_case:
                    mod = 26
                else:
                    mod = 52

                if char == letter:
                    encrypted_message += case[(i + key) % mod]
        return encrypted_message


class Decrypt:
    """
    This class is a blueprint to create a decrypted object from plaintext (alphabets only).

    plain_text is the text to be encrypted

    mode (optional) is the mode in which to encrypt the text:
    1. mode == 0 (Encryption in uppercase, default)
    2. mode == 1 (Encryption in lowercase)
    3. mode == 2 (Encryption using the combination of both cases)
    """

    def __init__(self, cipher_text, mode=0):
        if not cipher_text.isalpha():
            raise ValueError(
                "Please ensure that the text contains only lowercase or uppercase alphabets! No other characters are allowed!"
            )
        self.cipher_text = cipher_text
        self.mode = mode

    def decrypt(self, key=1):
        """
        Decrypt the message using the key and mode as specified by user

        Key defines the length by which the letters are to be shifted.
        Positive value means shift right, left otherwise
        Can take on values 1 (default) to 25.
        """

        # Check if key lies in valid range of 1:25 or -25:-1
        if key == 0 or key < -25 or key > 25:
            raise ValueError(
                "Please enter the key in the correct range of 1 (default) to 25, or -1 to -25."
            )

        # Check for mode. If incorrect value, raise valueError and terminate immediately
        if self.mode == 0:
            case = upper_case
        elif self.mode == 1:
            case = lower_case
        elif self.mode == 2:
            case = all_case
        else:
            raise ValueError(
                "Please correctly enter the mode (0 for uppercase, 1 for lowercase and 2 for both)!"
            )

        # Check if the case of user supplied input and the case of the mode in which the decryption is to be done is the same
        # If not, raise ValueError and terminate immediately
        if self.mode == 0 and not self.cipher_text.isupper():
            raise ValueError(
                "Cannot decrypt uppercase mode: input is not uppercase or some characters are not letters."
            )
        elif self.mode == 1 and not self.cipher_text.islower():
            raise ValueError(
                "Cannot decrypt lowercase mode: input is not lowercase or some characters are not letters."
            )
        elif self.mode == 2 and not any(c.isalpha() for c in self.cipher_text):
            raise ValueError(
                "Cannot decrypt mixed-case mode: input contains no letters."
            )

        decrypted_message = ""

        for char in self.cipher_text:
            for i, letter in enumerate(case):
                if case == lower_case or case == upper_case:
                    mod = 26
                else:
                    mod = 52

                if char == letter:
                    decrypted_message += case[(i - key) % mod]

        return decrypted_message
