import heapq

from user import tokenize_bio


class SearchEngine:
    def __init__(self, social_graph, username_trie):
        self.social_graph = social_graph
        self.username_trie = username_trie
        self.inverted_index = {}

        self._build_inverted_index()

    def _build_inverted_index(self):
        """
        Za svaku rec cuva skup ID-jeva korisnika kod kojih se
        ta rec pojavljuje u biografiji.
        """
        self.inverted_index = {}

        for user in self.social_graph.users_by_id.values():
            for word in user.bio_tokens:
                if word not in self.inverted_index:
                    self.inverted_index[word] = set()

                self.inverted_index[word].add(user.id)

    def add_user_to_index(self, user):
        """
        Dodaje reci jednog novog korisnika u postojeci indeks.
        """
        for word in user.bio_tokens:
            if word not in self.inverted_index:
                self.inverted_index[word] = set()

            self.inverted_index[word].add(user.id)

    def number_of_indexed_words(self):
        return len(self.inverted_index)

    def search_by_username(self, query, number_of_results=10):
        """
        Pretrazuje korisnicka imena bez obzira na velika i mala slova.

        Relevantnost:
        3 - korisnicko ime je potpuno jednako upitu
        2 - korisnicko ime pocinje upitom
        1 - korisnicko ime sadrzi upit

        Tacno poklapanje se pronalazi hash mapom, prefiksna poklapanja
        pomocu trie-a, a prolazak kroz sva imena koristi se samo ako je
        potrebno dopuniti rezultate substring poklapanjima.
        """
        self._validate_search_request(query, number_of_results)
        self._ensure_pagerank_is_calculated()

        normalized_query = query.strip().casefold()
        results = []
        selected_user_ids = set()

        exact_user_id = self.social_graph.user_id_by_username.get(
            normalized_query
        )

        if exact_user_id is not None:
            exact_user = self.social_graph.users_by_id[exact_user_id]
            exact_rank = self.social_graph.pagerank[exact_user_id]

            results.append((exact_user, 3, exact_rank))
            selected_user_ids.add(exact_user_id)

        remaining_places = number_of_results - len(results)

        if remaining_places == 0:
            return results

        prefix_user_ids = self.username_trie.find_user_ids_by_prefix(
            normalized_query
        )

        prefix_candidates = []

        for user_id in prefix_user_ids:
            if user_id in selected_user_ids:
                continue

            rank = self.social_graph.pagerank[user_id]
            prefix_candidates.append((user_id, rank))

        top_prefix_candidates = heapq.nlargest(
            remaining_places,
            prefix_candidates,
            key=lambda item: (item[1], -item[0])
        )

        for user_id, rank in top_prefix_candidates:
            user = self.social_graph.users_by_id[user_id]
            results.append((user, 2, rank))
            selected_user_ids.add(user_id)

        remaining_places = number_of_results - len(results)

        if remaining_places == 0:
            return results

        substring_candidates = []

        for user in self.social_graph.users_by_id.values():
            if user.id in selected_user_ids:
                continue

            if normalized_query in user.normalized_username:
                rank = self.social_graph.pagerank[user.id]
                substring_candidates.append((user.id, rank))

        top_substring_candidates = heapq.nlargest(
            remaining_places,
            substring_candidates,
            key=lambda item: (item[1], -item[0])
        )

        for user_id, rank in top_substring_candidates:
            user = self.social_graph.users_by_id[user_id]
            results.append((user, 1, rank))

        return results


    def suggest_usernames(
        self,
        username,
        number_of_results=5,
        max_distance=3
    ):
        """
        Predlaze slicna postojeca korisnicka imena kada uneto
        korisnicko ime ne postoji.

        Kandidati se porede pomocu Levenshtein rastojanja. Manje
        rastojanje predstavlja vecu slicnost. Ako dva kandidata imaju
        isto rastojanje, prednost ima korisnik sa vecim PageRank-om.
        """
        self._validate_suggestion_request(
            username,
            number_of_results,
            max_distance
        )
        self._ensure_pagerank_is_calculated()

        normalized_username = username.strip().casefold()

        if normalized_username in self.social_graph.user_id_by_username:
            return []

        candidates = []
        query_length = len(normalized_username)

        for user in self.social_graph.users_by_id.values():
            candidate_username = user.normalized_username

            if abs(len(candidate_username) - query_length) > max_distance:
                continue

            distance = self._levenshtein_distance(
                normalized_username,
                candidate_username,
                max_distance
            )

            if distance > max_distance:
                continue

            rank = self.social_graph.pagerank[user.id]
            candidates.append((user.id, distance, rank))

        top_items = heapq.nsmallest(
            number_of_results,
            candidates,
            key=lambda item: (item[1], -item[2], item[0])
        )

        results = []

        for user_id, distance, rank in top_items:
            user = self.social_graph.users_by_id[user_id]
            results.append((user, distance, rank))

        return results

    def _levenshtein_distance(
        self,
        first_text,
        second_text,
        max_distance=None
    ):
        """
        Racuna Levenshtein rastojanje pomocu dinamickog programiranja.

        Koriste se samo prethodni i trenutni red DP tabele. Ako je
        prosledjen max_distance, racunanje se prekida kada je jasno da
        kandidat ne moze biti dovoljno slican.
        """
        if first_text == second_text:
            return 0

        if len(first_text) < len(second_text):
            first_text, second_text = second_text, first_text

        if (
            max_distance is not None
            and abs(len(first_text) - len(second_text)) > max_distance
        ):
            return max_distance + 1

        previous_row = list(range(len(second_text) + 1))

        for first_index, first_character in enumerate(
            first_text,
            start=1
        ):
            current_row = [first_index]
            smallest_value_in_row = first_index

            for second_index, second_character in enumerate(
                second_text,
                start=1
            ):
                insertion_cost = current_row[second_index - 1] + 1
                deletion_cost = previous_row[second_index] + 1

                if first_character == second_character:
                    replacement_cost = previous_row[second_index - 1]
                else:
                    replacement_cost = (
                        previous_row[second_index - 1] + 1
                    )

                current_value = min(
                    insertion_cost,
                    deletion_cost,
                    replacement_cost
                )

                current_row.append(current_value)

                if current_value < smallest_value_in_row:
                    smallest_value_in_row = current_value

            if (
                max_distance is not None
                and smallest_value_in_row > max_distance
            ):
                return max_distance + 1

            previous_row = current_row

        return previous_row[-1]

    def search_by_bio(self, query, number_of_results=10):
        """
        Pretrazuje biografije pomocu inverted index-a.

        Relevantnost je odnos broja pronadjenih razlicitih reci
        i ukupnog broja razlicitih reci u upitu.
        """
        self._validate_search_request(query, number_of_results)
        self._ensure_pagerank_is_calculated()

        query_tokens = tokenize_bio(query)

        if not query_tokens:
            return []

        match_count_by_user = {}

        for word in query_tokens:
            user_ids = self.inverted_index.get(word, set())

            for user_id in user_ids:
                if user_id not in match_count_by_user:
                    match_count_by_user[user_id] = 0

                match_count_by_user[user_id] += 1

        candidates = []
        number_of_query_words = len(query_tokens)

        for user_id, match_count in match_count_by_user.items():
            relevance = match_count / number_of_query_words
            rank = self.social_graph.pagerank[user_id]

            candidates.append((user_id, relevance, rank))

        number_of_results = min(number_of_results, len(candidates))

        top_items = heapq.nlargest(
            number_of_results,
            candidates,
            key=lambda item: (item[1], item[2], -item[0])
        )

        results = []

        for user_id, relevance, rank in top_items:
            user = self.social_graph.users_by_id[user_id]
            results.append((user, relevance, rank))

        return results

    def _validate_search_request(self, query, number_of_results):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Upit za pretragu ne sme biti prazan.")

        if number_of_results <= 0:
            raise ValueError(
                "Broj rezultata mora biti veci od 0."
            )


    def _validate_suggestion_request(
        self,
        username,
        number_of_results,
        max_distance
    ):
        if not isinstance(username, str) or not username.strip():
            raise ValueError(
                "Korisnicko ime za predlog ne sme biti prazno."
            )

        if (
            not isinstance(number_of_results, int)
            or isinstance(number_of_results, bool)
            or number_of_results <= 0
        ):
            raise ValueError(
                "Broj predloga mora biti pozitivan ceo broj."
            )

        if (
            not isinstance(max_distance, int)
            or isinstance(max_distance, bool)
            or max_distance <= 0
        ):
            raise ValueError(
                "Maksimalno rastojanje mora biti pozitivan ceo broj."
            )

    def _ensure_pagerank_is_calculated(self):
        if not self.social_graph.pagerank:
            raise ValueError(
                "PageRank nije izracunat. "
                "Prvo pozovite calculate_pagerank()."
            )
