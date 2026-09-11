from time import perf_counter


class ConsoleApplication:
    CANCEL_COMMAND = "x"

    def __init__(
        self,
        social_graph,
        search_engine,
        username_trie,
        recommendation_engine
    ):
        self.social_graph = social_graph
        self.search_engine = search_engine
        self.username_trie = username_trie
        self.recommendation_engine = recommendation_engine

    def run(self):
        print()
        print("Aplikacija je spremna za rad.")

        while True:
            self._print_menu()

            try:
                choice = input("Izaberite opciju: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                print("Program je zavrsen.")
                return

            if choice == "0":
                print("Program je zavrsen.")
                return

            actions = {
                "1": self._search_by_username,
                "2": self._search_by_bio,
                "3": self._show_top_users,
                "4": self._add_follow_connection,
                "5": self._show_interaction_history,
                "6": self._autocomplete,
                "7": self._recommend_users,
                "8": self._show_bfs_levels,
                "9": self._show_did_you_mean,
                "10": self._add_user
            }

            action = actions.get(choice)

            if action is None:
                print("Nepostojeca opcija. Pokusajte ponovo.")
                continue

            try:
                print()
                action()
            except ValueError as error:
                print(f"Greska: {error}")
            except (EOFError, KeyboardInterrupt):
                print()
                print("Operacija je prekinuta. Povratak na glavni meni.")

    def _print_menu(self):
        print()
        print("=" * 62)
        print("DRUSTVENA MREZA - GLAVNI MENI")
        print("=" * 62)
        print("1. Pretraga po korisnickom imenu")
        print("2. Pretraga po recima iz biografije")
        print("3. Prikaz najuticajnijih korisnika")
        print("4. Dodavanje nove follow veze")
        print("5. Prikaz istorije interakcija")
        print("6. Autocomplete korisnickog imena")
        print("7. Hibridne preporuke korisnika")
        print("8. BFS nivoi konekcije")
        print("9. Did you mean predlozi")
        print("10. Dodavanje novog korisnika")
        print("0. Izlazak")
        print("-" * 62)
        print("U okviru opcije unesite x za povratak na glavni meni.")
        print("=" * 62)

    def _search_by_username(self):
        query = self._read_required_text(
            "Unesite upit za korisnicko ime: "
        )

        if query is None:
            return

        number_of_results = self._read_positive_integer(
            "Maksimalan broj rezultata [10]: ",
            default_value=10
        )

        if number_of_results is None:
            return

        results = self.search_engine.search_by_username(
            query,
            number_of_results
        )

        self._print_username_search_results(results)

    def _search_by_bio(self):
        query = self._read_required_text(
            "Unesite reci za pretragu biografije: "
        )

        if query is None:
            return

        number_of_results = self._read_positive_integer(
            "Maksimalan broj rezultata [10]: ",
            default_value=10
        )

        if number_of_results is None:
            return

        results = self.search_engine.search_by_bio(
            query,
            number_of_results
        )

        self._print_bio_search_results(results)

    def _show_top_users(self):
        number_of_results = self._read_positive_integer(
            "Broj najuticajnijih korisnika [10]: ",
            default_value=10
        )

        if number_of_results is None:
            return

        results = self.social_graph.get_top_users_by_pagerank(
            number_of_results
        )

        print("Najuticajniji korisnici:")

        for position, result in enumerate(results, start=1):
            user = result[0]
            rank = result[1]

            print(
                f"  {position}. {user.username} "
                f"(ID: {user.id}, PageRank: {rank:.10f})"
            )

    def _add_follow_connection(self):
        follower = self._read_existing_user(
            "Korisnicko ime korisnika koji prati: "
        )

        if follower is None:
            return

        followed = self._read_existing_user(
            "Korisnicko ime korisnika koji ce biti zapracen: "
        )

        if followed is None:
            return

        print("Dodavanje veze i ponovno racunanje PageRank-a...")
        start_time = perf_counter()
        interaction, iterations, difference = (
            self.social_graph.add_follow_connection(
                follower.id,
                followed.id
            )
        )
        elapsed_time = perf_counter() - start_time

        print(
            f"Uspesno je dodata veza: {follower.username} -> "
            f"{followed.username}."
        )
        print(
            f"Redni broj nove interakcije: "
            f"{interaction.sequence_number}"
        )
        print(
            f"PageRank je ponovo izracunat warm start postupkom "
            f"za {iterations} iteracija."
        )
        print(f"Poslednja razlika: {difference:.10f}")
        print(f"Vreme izmene i PageRank-a: {elapsed_time:.6f} s")

    def _show_interaction_history(self):
        user = self._read_existing_user(
            "Korisnicko ime za prikaz istorije: "
        )

        if user is None:
            return

        history = self.social_graph.get_interaction_history(user.id)

        print(
            f"Istorija interakcija za {user.username} "
            f"(ID: {user.id}):"
        )

        if not history:
            print(
                "  Nema novih interakcija u trenutnom "
                "pokretanju programa."
            )
            return

        for sequence_number, interaction_type, other_user in history:
            if interaction_type == "followed":
                print(
                    f"  {sequence_number}. Zapratio/la je "
                    f"{other_user.username} (ID: {other_user.id})"
                )
            else:
                print(
                    f"  {sequence_number}. Zapratio/la ga/je "
                    f"{other_user.username} (ID: {other_user.id})"
                )

    def _autocomplete(self):
        prefix = self._read_required_text(
            "Unesite prefiks korisnickog imena, npr. mar*: "
        )

        if prefix is None:
            return

        number_of_results = self._read_positive_integer(
            "Maksimalan broj rezultata [10]: ",
            default_value=10
        )

        if number_of_results is None:
            return

        results = self.username_trie.autocomplete(
            prefix,
            number_of_results
        )

        if not results:
            print("Nema korisnickih imena za zadati prefiks.")
            return

        print("Autocomplete rezultati:")

        for position, result in enumerate(results, start=1):
            user = result[0]
            rank = result[1]

            print(
                f"  {position}. {user.username} "
                f"(ID: {user.id}, PageRank: {rank:.10f})"
            )

    def _recommend_users(self):
        user = self._read_existing_user(
            "Korisnicko ime za koje se formiraju preporuke: "
        )

        if user is None:
            return

        alpha = self._read_alpha(
            "Unesite alpha od 0 do 1 [0.5]: ",
            default_value=0.5
        )

        if alpha is None:
            return

        number_of_results = self._read_positive_integer(
            "Maksimalan broj preporuka [10]: ",
            default_value=10
        )

        if number_of_results is None:
            return

        print("Racunanje Personalized PageRank-a i preporuka...")
        start_time = perf_counter()
        results, iterations, difference = (
            self.recommendation_engine.recommend_users(
                user.id,
                alpha,
                number_of_results
            )
        )
        elapsed_time = perf_counter() - start_time

        if not results:
            print("Nema odgovarajucih preporuka.")
        else:
            print(
                f"Hibridne preporuke za {user.username} "
                f"(alpha = {alpha}):"
            )

            for position, result in enumerate(results, start=1):
                candidate = result[0]
                combined_score = result[1]
                personalized_rank = result[2]
                content_similarity = result[3]
                global_rank = result[4]

                print(
                    f"  {position}. {candidate.username} "
                    f"(ID: {candidate.id}, kombinovani skor: "
                    f"{combined_score:.10f}, PPR: "
                    f"{personalized_rank:.10f}, Jaccard: "
                    f"{content_similarity:.4f}, PageRank: "
                    f"{global_rank:.10f})"
                )

        print(f"Broj PPR iteracija: {iterations}")
        print(f"Poslednja PPR razlika: {difference:.10f}")
        print(f"Vreme preporuke: {elapsed_time:.6f} s")

    def _show_bfs_levels(self):
        user = self._read_existing_user(
            "Pocetno korisnicko ime za BFS: "
        )

        if user is None:
            return

        max_level = self._read_positive_integer(
            "Maksimalni BFS nivo: "
        )

        if max_level is None:
            return

        sample_size = self._read_positive_integer(
            "Broj prikazanih korisnika po nivou [10]: ",
            default_value=10
        )

        if sample_size is None:
            return

        start_time = perf_counter()
        levels = self.social_graph.get_connection_levels(
            user.id,
            max_level
        )
        elapsed_time = perf_counter() - start_time

        if not levels:
            print("Nema dostiznih korisnika do zadatog nivoa.")
        else:
            print(
                f"BFS nivoi za {user.username} "
                f"(ID: {user.id}):"
            )
            self._print_bfs_levels(levels, sample_size)

        print(f"Vreme BFS obilaska: {elapsed_time:.6f} s")

    def _show_did_you_mean(self):
        username = self._read_required_text(
            "Unesite nepostojece ili pogresno korisnicko ime: "
        )

        if username is None:
            return

        number_of_results = self._read_positive_integer(
            "Maksimalan broj predloga [5]: ",
            default_value=5
        )

        if number_of_results is None:
            return

        max_distance = self._read_positive_integer(
            "Maksimalno Levenshtein rastojanje [3]: ",
            default_value=3
        )

        if max_distance is None:
            return

        existing_user = self.social_graph.get_user_by_username(username)

        if existing_user is not None:
            print(
                f"Korisnik {existing_user.username} vec postoji "
                f"(ID: {existing_user.id})."
            )
            return

        results = self.search_engine.suggest_usernames(
            username,
            number_of_results,
            max_distance
        )

        self._print_username_suggestions(results)

    def _add_user(self):
        while True:
            username = self._read_required_text(
                "Novo korisnicko ime: "
            )

            if username is None:
                return

            if self.social_graph.get_user_by_username(username) is not None:
                print(
                    "Korisnicko ime vec postoji. "
                    "Unesite drugo ime ili x za povratak."
                )
                continue

            bio = self._read_optional_text(
                "Biografija (moze ostati prazna): "
            )

            if bio is None:
                return

            try:
                print("Dodavanje korisnika i ponovno racunanje PageRank-a...")
                start_time = perf_counter()
                user, iterations, difference = self.social_graph.add_user(
                    username,
                    bio
                )

                self.username_trie.add_user(user)
                self.search_engine.add_user_to_index(user)
                elapsed_time = perf_counter() - start_time
            except ValueError as error:
                print(f"Greska: {error}")
                print("Pokusajte ponovo ili unesite x za povratak.")
                continue

            print(
                f"Uspesno je dodat korisnik {user.username} "
                f"sa automatski dodeljenim ID-jem {user.id}."
            )
            print(
                f"PageRank je ponovo izracunat od pocetka "
                f"za {iterations} iteracija."
            )
            print(f"Poslednja razlika: {difference:.10f}")
            print(f"Vreme dodavanja i PageRank-a: {elapsed_time:.6f} s")
            print(
                "Novi korisnik je dodat i u trie i inverted index."
            )
            return

    def _read_existing_user(self, prompt):
        while True:
            username = input(prompt).strip()

            if self._is_cancel_command(username):
                print("Povratak na glavni meni.")
                return None

            if not username:
                print(
                    "Korisnicko ime ne sme biti prazno. "
                    "Pokusajte ponovo ili unesite x za povratak."
                )
                continue

            user = self.social_graph.get_user_by_username(username)

            if user is not None:
                return user

            print(f"Korisnik '{username}' ne postoji.")

            suggestions = self.search_engine.suggest_usernames(
                username,
                number_of_results=5,
                max_distance=3
            )

            if suggestions:
                print("Da li ste mislili:")
                self._print_username_suggestions(suggestions)
            else:
                print("Nema dovoljno slicnih korisnickih imena za predlog.")

            print(
                "Unesite korisnicko ime ponovo ili x za povratak."
            )

    def _read_required_text(self, prompt):
        while True:
            value = input(prompt).strip()

            if self._is_cancel_command(value):
                print("Povratak na glavni meni.")
                return None

            if not value:
                print(
                    "Unos ne sme biti prazan. "
                    "Pokusajte ponovo ili unesite x za povratak."
                )
                continue

            return value

    def _read_optional_text(self, prompt):
        value = input(prompt).strip()

        if self._is_cancel_command(value):
            print("Povratak na glavni meni.")
            return None

        return value

    def _read_positive_integer(self, prompt, default_value=None):
        while True:
            value = input(prompt).strip()

            if self._is_cancel_command(value):
                print("Povratak na glavni meni.")
                return None

            if value == "" and default_value is not None:
                return default_value

            try:
                number = int(value)
            except ValueError:
                print(
                    "Potrebno je uneti pozitivan ceo broj ili x "
                    "za povratak."
                )
                continue

            if number <= 0:
                print(
                    "Potrebno je uneti pozitivan ceo broj ili x "
                    "za povratak."
                )
                continue

            return number

    def _read_alpha(self, prompt, default_value=0.5):
        while True:
            value = input(prompt).strip()

            if self._is_cancel_command(value):
                print("Povratak na glavni meni.")
                return None

            if value == "":
                return default_value

            try:
                alpha = float(value)
            except ValueError:
                print("Alpha mora biti broj od 0 do 1 ili x za povratak.")
                continue

            if not 0.0 <= alpha <= 1.0:
                print("Alpha mora biti broj od 0 do 1 ili x za povratak.")
                continue

            return alpha

    def _is_cancel_command(self, value):
        return value.casefold() == self.CANCEL_COMMAND

    def _print_username_search_results(self, results):
        if not results:
            print("Nema rezultata pretrage.")
            return

        print("Rezultati pretrage po korisnickom imenu:")

        for position, result in enumerate(results, start=1):
            user = result[0]
            relevance = result[1]
            rank = result[2]

            print(
                f"  {position}. {user.username} "
                f"(ID: {user.id}, relevantnost: {relevance}, "
                f"PageRank: {rank:.10f})"
            )

    def _print_bio_search_results(self, results):
        if not results:
            print("Nema rezultata pretrage.")
            return

        print("Rezultati pretrage po biografiji:")

        for position, result in enumerate(results, start=1):
            user = result[0]
            relevance = result[1]
            rank = result[2]

            print(
                f"  {position}. {user.username} "
                f"(ID: {user.id}, relevantnost: "
                f"{relevance:.4f}, PageRank: {rank:.10f})"
            )

    def _print_username_suggestions(self, results):
        if not results:
            print("Nema dovoljno slicnih korisnickih imena za predlog.")
            return

        for position, result in enumerate(results, start=1):
            user = result[0]
            distance = result[1]
            rank = result[2]

            print(
                f"  {position}. {user.username} "
                f"(ID: {user.id}, Levenshtein rastojanje: "
                f"{distance}, PageRank: {rank:.10f})"
            )

    def _print_bfs_levels(self, levels, sample_size):
        for level in sorted(levels):
            users = levels[level]
            print(f"  Nivo {level}: {len(users)} korisnika")

            number_to_show = min(sample_size, len(users))

            for index in range(number_to_show):
                user = users[index]
                print(f"    - {user.username} (ID: {user.id})")

            if len(users) > sample_size:
                print(
                    f"    ... i jos "
                    f"{len(users) - sample_size} korisnika"
                )
