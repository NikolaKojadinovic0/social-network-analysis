from pathlib import Path
from collections import deque
import heapq

from interaction import FollowInteraction
from user import User


class SocialGraph:
    def __init__(self):
        self.users_by_id = {}
        self.user_id_by_username = {}

        self.outgoing_connections = {}
        self.incoming_connections = {}
        self.out_degree = {}

        self.blocked_out = {}
        self.blocked_in = {}

        self.pagerank = {}
        self.interaction_history = {}
        self.next_interaction_sequence = 1
        self.next_user_id = 1

    def load_from_directory(self, data_directory):
        data_path = Path(data_directory)

        self._load_users(data_path / "users.txt")
        self._load_connections(data_path / "connections.txt")
        self._load_blocked(data_path / "blocked.txt")

    def _load_users(self, file_path):
        with file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.rstrip("\r\n")

                if not line:
                    continue

                parts = line.split("|", 2)

                if len(parts) != 3:
                    raise ValueError(
                        f"Neispravan red u {file_path}, "
                        f"linija {line_number}: {line}"
                    )

                user_id_text, username, bio = parts
                user_id = int(user_id_text)

                normalized_username = username.casefold()

                if user_id in self.users_by_id:
                    raise ValueError(
                        f"Dupliran ID korisnika: {user_id}"
                    )

                if normalized_username in self.user_id_by_username:
                    raise ValueError(
                        f"Duplirano korisnicko ime: {username}"
                    )

                user = User(user_id, username, bio)

                self.users_by_id[user_id] = user
                self.user_id_by_username[normalized_username] = user_id

                self.outgoing_connections[user_id] = set()
                self.incoming_connections[user_id] = []
                self.out_degree[user_id] = 0

                self.blocked_out[user_id] = set()
                self.blocked_in[user_id] = set()

                self.interaction_history[user_id] = []

                if user_id >= self.next_user_id:
                    self.next_user_id = user_id + 1

    def _load_connections(self, file_path):
        with file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                parts = line.split("|")

                if len(parts) != 2:
                    raise ValueError(
                        f"Neispravan red u {file_path}, "
                        f"linija {line_number}: {line}"
                    )

                follower_id = int(parts[0])
                followed_id = int(parts[1])

                self._validate_existing_user(
                    follower_id,
                    file_path,
                    line_number
                )

                self._validate_existing_user(
                    followed_id,
                    file_path,
                    line_number
                )

                if follower_id == followed_id:
                    raise ValueError(
                        f"Korisnik {follower_id} "
                        f"ne moze pratiti samog sebe."
                    )

                if followed_id not in self.outgoing_connections[follower_id]:
                    self.outgoing_connections[follower_id].add(
                        followed_id
                    )

                    self.incoming_connections[followed_id].append(
                        follower_id
                    )

                    self.out_degree[follower_id] += 1

    def _load_blocked(self, file_path):
        with file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                parts = line.split("|")

                if len(parts) != 2:
                    raise ValueError(
                        f"Neispravan red u {file_path}, "
                        f"linija {line_number}: {line}"
                    )

                blocker_id = int(parts[0])
                blocked_id = int(parts[1])

                self._validate_existing_user(
                    blocker_id,
                    file_path,
                    line_number
                )

                self._validate_existing_user(
                    blocked_id,
                    file_path,
                    line_number
                )

                if blocker_id == blocked_id:
                    raise ValueError(
                        f"Korisnik {blocker_id} "
                        f"ne moze blokirati samog sebe."
                    )

                self.blocked_out[blocker_id].add(blocked_id)
                self.blocked_in[blocked_id].add(blocker_id)

    def _validate_existing_user(
        self,
        user_id,
        file_path,
        line_number
    ):
        if user_id not in self.users_by_id:
            raise ValueError(
                f"Nepostojeci korisnik {user_id} "
                f"u {file_path}, linija {line_number}."
            )

    def get_user_by_id(self, user_id):
        return self.users_by_id.get(user_id)

    def get_user_by_username(self, username):
        normalized_username = username.strip().casefold()

        user_id = self.user_id_by_username.get(
            normalized_username
        )

        if user_id is None:
            return None

        return self.users_by_id[user_id]

    def add_user(self, username, bio):
        """
        Dodaje novog korisnika u sve strukture grafa i ponovo racuna
        PageRank. Izmena vazi samo tokom trenutnog pokretanja programa.
        """
        if not isinstance(username, str):
            raise ValueError("Korisnicko ime mora biti tekst.")

        if not isinstance(bio, str):
            raise ValueError("Biografija mora biti tekst.")

        cleaned_username = username.strip()
        cleaned_bio = bio.strip()

        if not cleaned_username:
            raise ValueError("Korisnicko ime ne sme biti prazno.")

        if "|" in cleaned_username:
            raise ValueError(
                "Korisnicko ime ne sme sadrzati znak |."
            )

        normalized_username = cleaned_username.casefold()

        if normalized_username in self.user_id_by_username:
            raise ValueError(
                "Korisnicko ime vec postoji."
            )

        user_id = self.next_user_id
        self.next_user_id += 1

        user = User(user_id, cleaned_username, cleaned_bio)

        self.users_by_id[user_id] = user
        self.user_id_by_username[normalized_username] = user_id

        self.outgoing_connections[user_id] = set()
        self.incoming_connections[user_id] = []
        self.out_degree[user_id] = 0

        self.blocked_out[user_id] = set()
        self.blocked_in[user_id] = set()

        self.interaction_history[user_id] = []

        iterations, difference = self.calculate_pagerank(
            warm_start=False
        )

        return user, iterations, difference

    def is_blocked_between(
        self,
        first_user_id,
        second_user_id
    ):
        return (
            second_user_id
            in self.blocked_out[first_user_id]
            or
            first_user_id
            in self.blocked_out[second_user_id]
        )

    def has_follow_connection(self, follower_id, followed_id):
        self._validate_user_for_operation(follower_id)
        self._validate_user_for_operation(followed_id)

        return followed_id in self.outgoing_connections[follower_id]

    def add_follow_connection(self, follower_id, followed_id):
        """
        Dodaje novu follow vezu, evidentira je u istoriji oba
        korisnika i ponovo racuna PageRank.
        """
        self._validate_user_for_operation(follower_id)
        self._validate_user_for_operation(followed_id)

        if follower_id == followed_id:
            raise ValueError(
                "Korisnik ne moze pratiti samog sebe."
            )

        if self.is_blocked_between(follower_id, followed_id):
            raise ValueError(
                "Follow veza ne moze biti dodata jer izmedju "
                "korisnika postoji blokiranje."
            )

        if followed_id in self.outgoing_connections[follower_id]:
            raise ValueError(
                "Ova follow veza vec postoji."
            )

        had_pagerank = bool(self.pagerank)

        self.outgoing_connections[follower_id].add(followed_id)
        self.incoming_connections[followed_id].append(follower_id)
        self.out_degree[follower_id] += 1

        interaction = FollowInteraction(
            self.next_interaction_sequence,
            follower_id,
            followed_id
        )

        self.next_interaction_sequence += 1

        self.interaction_history[follower_id].append(interaction)
        self.interaction_history[followed_id].append(interaction)

        iterations, difference = self.calculate_pagerank(
            warm_start=had_pagerank
        )

        return interaction, iterations, difference

    def get_interaction_history(self, user_id):
        """
        Vraca interakcije korisnika redom kojim su nastale.

        Svaki rezultat ima oblik:
        (redni_broj, tip_interakcije, drugi_korisnik)
        """
        self._validate_user_for_operation(user_id)
        results = []

        for interaction in self.interaction_history[user_id]:
            if interaction.follower_id == user_id:
                interaction_type = "followed"
                other_user_id = interaction.followed_id
            else:
                interaction_type = "followed_by"
                other_user_id = interaction.follower_id

            other_user = self.users_by_id[other_user_id]

            results.append((
                interaction.sequence_number,
                interaction_type,
                other_user
            ))

        return results

    def get_connection_levels(self, start_user_id, max_level):
        """
        Pomocu BFS algoritma pronalazi korisnike do zadatog nivoa.

        Nivo 1 sadrzi korisnike koje pocetni korisnik direktno prati,
        nivo 2 korisnike do kojih se stize preko jednog posrednika, itd.
        Graf se obilazi u smeru outgoing follow veza.
        """
        self._validate_user_for_operation(start_user_id)

        if (
            not isinstance(max_level, int)
            or isinstance(max_level, bool)
            or max_level <= 0
        ):
            raise ValueError(
                "Maksimalni BFS nivo mora biti pozitivan ceo broj."
            )

        visited = {start_user_id}
        queue = deque()
        queue.append((start_user_id, 0))

        user_ids_by_level = {}

        while queue:
            current_user_id, current_level = queue.popleft()

            if current_level == max_level:
                continue

            next_level = current_level + 1

            for neighbour_id in self.outgoing_connections[current_user_id]:
                if neighbour_id in visited:
                    continue

                visited.add(neighbour_id)

                if next_level not in user_ids_by_level:
                    user_ids_by_level[next_level] = []

                user_ids_by_level[next_level].append(neighbour_id)
                queue.append((neighbour_id, next_level))

        results = {}

        for level, user_ids in user_ids_by_level.items():
            user_ids.sort()
            results[level] = []

            for user_id in user_ids:
                results[level].append(self.users_by_id[user_id])

        return results

    def _validate_user_for_operation(self, user_id):
        if user_id not in self.users_by_id:
            raise ValueError(
                f"Korisnik sa ID-jem {user_id} ne postoji."
            )

    def number_of_users(self):
        return len(self.users_by_id)

    def number_of_connections(self):
        return sum(self.out_degree.values())

    def number_of_blocks(self):
        number_of_blocks = 0

        for blocked_users in self.blocked_out.values():
            number_of_blocks += len(blocked_users)

        return number_of_blocks

    def calculate_pagerank(
        self,
        damping_factor=0.85,
        epsilon=1e-6,
        max_iterations=100,
        warm_start=False
    ):
        number_of_users = len(self.users_by_id)

        if number_of_users == 0:
            self.pagerank = {}
            return 0, 0.0

        if not 0 < damping_factor < 1:
            raise ValueError(
                "Damping factor mora biti izmedju 0 i 1."
            )

        if epsilon <= 0:
            raise ValueError(
                "Epsilon mora biti veci od 0."
            )

        if max_iterations <= 0:
            raise ValueError(
                "Maksimalan broj iteracija mora biti veci od 0."
            )

        if (
            warm_start
            and len(self.pagerank) == number_of_users
            and all(
                user_id in self.pagerank
                for user_id in self.users_by_id
            )
        ):
            old_ranks = self.pagerank.copy()
            total_rank = sum(old_ranks.values())

            if total_rank > 0:
                for user_id in old_ranks:
                    old_ranks[user_id] /= total_rank
            else:
                initial_rank = 1.0 / number_of_users

                old_ranks = {
                    user_id: initial_rank
                    for user_id in self.users_by_id
                }
        else:
            initial_rank = 1.0 / number_of_users

            old_ranks = {
                user_id: initial_rank
                for user_id in self.users_by_id
            }

        difference = float("inf")
        completed_iterations = 0

        for iteration in range(1, max_iterations + 1):
            dangling_mass = 0.0
            contribution_by_user = {}

            for user_id in self.users_by_id:
                degree = self.out_degree[user_id]

                if degree == 0:
                    dangling_mass += old_ranks[user_id]
                else:
                    contribution_by_user[user_id] = (
                        damping_factor
                        * old_ranks[user_id]
                        / degree
                    )

            base_rank = (
                (1.0 - damping_factor) / number_of_users
                + damping_factor
                * dangling_mass
                / number_of_users
            )

            new_ranks = {}

            for user_id in self.users_by_id:
                new_rank = base_rank

                for follower_id in self.incoming_connections[user_id]:
                    new_rank += contribution_by_user[follower_id]

                new_ranks[user_id] = new_rank

            difference = 0.0

            for user_id in self.users_by_id:
                difference += abs(
                    new_ranks[user_id]
                    - old_ranks[user_id]
                )

            old_ranks = new_ranks
            completed_iterations = iteration

            if difference < epsilon:
                break

        self.pagerank = old_ranks

        return completed_iterations, difference

    def calculate_personalized_pagerank(
        self,
        start_user_id,
        damping_factor=0.85,
        epsilon=1e-6,
        max_iterations=100
    ):
        """
        Racuna Personalized PageRank iz perspektive jednog korisnika.

        Teleportacija i masa dangling cvorova vracaju se pocetnom
        korisniku, pa veci skor dobijaju korisnici relevantni za njegov
        deo mreze.
        """
        self._validate_user_for_operation(start_user_id)

        if not 0 < damping_factor < 1:
            raise ValueError(
                "Damping factor mora biti izmedju 0 i 1."
            )

        if epsilon <= 0:
            raise ValueError("Epsilon mora biti veci od 0.")

        if max_iterations <= 0:
            raise ValueError(
                "Maksimalan broj iteracija mora biti veci od 0."
            )

        old_ranks = {
            user_id: 0.0
            for user_id in self.users_by_id
        }
        old_ranks[start_user_id] = 1.0

        difference = float("inf")
        completed_iterations = 0

        for iteration in range(1, max_iterations + 1):
            dangling_mass = 0.0
            contribution_by_user = {}

            for user_id in self.users_by_id:
                degree = self.out_degree[user_id]

                if degree == 0:
                    dangling_mass += old_ranks[user_id]
                else:
                    contribution_by_user[user_id] = (
                        damping_factor
                        * old_ranks[user_id]
                        / degree
                    )

            new_ranks = {
                user_id: 0.0
                for user_id in self.users_by_id
            }

            new_ranks[start_user_id] = (
                1.0
                - damping_factor
                + damping_factor * dangling_mass
            )

            for user_id in self.users_by_id:
                for follower_id in self.incoming_connections[user_id]:
                    new_ranks[user_id] += (
                        contribution_by_user[follower_id]
                    )

            difference = 0.0

            for user_id in self.users_by_id:
                difference += abs(
                    new_ranks[user_id]
                    - old_ranks[user_id]
                )

            old_ranks = new_ranks
            completed_iterations = iteration

            if difference < epsilon:
                break

        return old_ranks, completed_iterations, difference

    def get_top_users_by_pagerank(self, number_of_results):
        if not self.pagerank:
            raise ValueError(
                "PageRank nije izracunat. "
                "Prvo pozovite calculate_pagerank()."
            )

        if number_of_results <= 0:
            raise ValueError(
                "Broj rezultata mora biti veci od 0."
            )

        number_of_results = min(
            number_of_results,
            len(self.pagerank)
        )

        top_items = heapq.nlargest(
            number_of_results,
            self.pagerank.items(),
            key=lambda item: (item[1], -item[0])
        )

        results = []

        for user_id, rank in top_items:
            user = self.users_by_id[user_id]
            results.append((user, rank))

        return results
