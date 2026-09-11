import heapq


class TrieNode:
    def __init__(self):
        self.children = {}
        self.user_id = None


class UsernameTrie:
    def __init__(self, social_graph):
        self.social_graph = social_graph
        self.root = TrieNode()
        self.node_count = 1
        self.username_count = 0

        self._build_trie()

    def _build_trie(self):
        """
        Formira trie od normalizovanih korisnickih imena svih
        trenutno ucitanih korisnika.
        """
        self.root = TrieNode()
        self.node_count = 1
        self.username_count = 0

        for user in self.social_graph.users_by_id.values():
            self.add_user(user)

    def add_user(self, user):
        """
        Dodaje korisnicko ime jednog korisnika u postojeci trie.
        """
        current_node = self.root

        for character in user.normalized_username:
            if character not in current_node.children:
                current_node.children[character] = TrieNode()
                self.node_count += 1

            current_node = current_node.children[character]

        if current_node.user_id is None:
            current_node.user_id = user.id
            self.username_count += 1

    def find_user_ids_by_prefix(self, prefix):
        """
        Vraca ID-jeve svih korisnika cija normalizovana korisnicka
        imena pocinju zadatim prefiksom.

        Metoda samo pronalazi kandidate. Ne koristi PageRank i ne
        ogranicava broj rezultata, pa je mogu koristiti i autocomplete
        i pretraga po korisnickom imenu.
        """
        normalized_prefix = self._normalize_prefix(prefix)
        prefix_node = self._find_prefix_node(normalized_prefix)

        if prefix_node is None:
            return []

        return self._collect_user_ids(prefix_node)

    def autocomplete(self, prefix, number_of_results=10):
        """
        Vraca korisnike cija korisnicka imena pocinju zadatim
        prefiksom. Rezultati se rangiraju po PageRank vrednosti.
        """
        self._validate_number_of_results(number_of_results)
        self._ensure_pagerank_is_calculated()

        matching_user_ids = self.find_user_ids_by_prefix(prefix)
        number_of_results = min(
            number_of_results,
            len(matching_user_ids)
        )

        top_user_ids = heapq.nlargest(
            number_of_results,
            matching_user_ids,
            key=lambda user_id: (
                self.social_graph.pagerank[user_id],
                -user_id
            )
        )

        results = []

        for user_id in top_user_ids:
            user = self.social_graph.users_by_id[user_id]
            rank = self.social_graph.pagerank[user_id]
            results.append((user, rank))

        return results

    def _normalize_prefix(self, prefix):
        if not isinstance(prefix, str):
            raise ValueError("Prefiks mora biti tekst.")

        normalized_prefix = prefix.strip().casefold()

        if normalized_prefix.endswith("*"):
            normalized_prefix = normalized_prefix[:-1].rstrip()

        if not normalized_prefix:
            raise ValueError("Prefiks za autocomplete ne sme biti prazan.")

        return normalized_prefix

    def _find_prefix_node(self, normalized_prefix):
        current_node = self.root

        for character in normalized_prefix:
            if character not in current_node.children:
                return None

            current_node = current_node.children[character]

        return current_node

    def _collect_user_ids(self, start_node):
        user_ids = []
        nodes_to_visit = [start_node]

        while nodes_to_visit:
            current_node = nodes_to_visit.pop()

            if current_node.user_id is not None:
                user_ids.append(current_node.user_id)

            for child_node in current_node.children.values():
                nodes_to_visit.append(child_node)

        return user_ids

    def _validate_number_of_results(self, number_of_results):
        if number_of_results <= 0:
            raise ValueError(
                "Broj autocomplete rezultata mora biti veci od 0."
            )

    def _ensure_pagerank_is_calculated(self):
        if not self.social_graph.pagerank:
            raise ValueError(
                "PageRank nije izracunat. "
                "Prvo pozovite calculate_pagerank()."
            )

    def number_of_nodes(self):
        return self.node_count

    def number_of_usernames(self):
        return self.username_count
