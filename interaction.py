class FollowInteraction:
    """
    Predstavlja jednu novu follow interakciju nastalu tokom
    trenutnog pokretanja programa.
    """

    def __init__(self, sequence_number, follower_id, followed_id):
        self.sequence_number = sequence_number
        self.follower_id = follower_id
        self.followed_id = followed_id
