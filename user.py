import re


def tokenize_bio(text):
    """
    Pretvara biografiju u skup normalizovanih reci.
    """
    words = re.findall(r"\w+", text.casefold())
    return set(words)


class User:
    def __init__(self, user_id, username, bio):
        self.id = user_id
        self.username = username
        self.bio = bio

        self.normalized_username = username.casefold()
        self.bio_tokens = tokenize_bio(bio)

    def __str__(self):
        return f"{self.id} | {self.username} | {self.bio}"
