import tempfile
import unittest

from search_engine import SearchEngine
from tests.helpers import load_graph
from trie import UsernameTrie


class TestSearchAndTrie(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.graph = load_graph(self.temporary_directory.name)
        self.graph.calculate_pagerank()
        self.trie = UsernameTrie(self.graph)
        self.search = SearchEngine(self.graph, self.trie)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_trie_prefix_search_is_case_insensitive(self):
        user_ids = self.trie.find_user_ids_by_prefix("MAR")

        self.assertEqual(set(user_ids), {6, 7, 8})

    def test_autocomplete_accepts_optional_asterisk_and_ranks_by_pagerank(self):
        plain = self.trie.autocomplete("mar", 3)
        with_asterisk = self.trie.autocomplete("MAR*", 3)

        self.assertEqual(
            [user.id for user, _ in plain],
            [user.id for user, _ in with_asterisk],
        )
        ranks = [rank for _, rank in plain]
        self.assertEqual(ranks, sorted(ranks, reverse=True))

    def test_username_search_prioritizes_exact_prefix_and_substring_matches(self):
        exact = self.search.search_by_username("ALICE", 10)
        prefix = self.search.search_by_username("mar", 10)
        substring = self.search.search_by_username("aria", 10)

        self.assertEqual((exact[0][0].id, exact[0][1]), (1, 3))
        self.assertTrue(all(relevance == 2 for _, relevance, _ in prefix))
        self.assertEqual((substring[0][0].id, substring[0][1]), (7, 1))

    def test_bio_search_uses_distinct_query_words(self):
        results = self.search.search_by_bio("python data python", 10)
        relevance_by_id = {user.id: relevance for user, relevance, _ in results}

        self.assertEqual(relevance_by_id[1], 1.0)
        self.assertEqual(relevance_by_id[5], 1.0)
        self.assertEqual(relevance_by_id[2], 0.5)

    def test_did_you_mean_uses_levenshtein_distance(self):
        results = self.search.suggest_usernames("marko_aj", 3, 2)

        self.assertEqual(results[0][0].username, "marko_ai")
        self.assertEqual(results[0][1], 1)

    def test_new_user_can_be_added_to_existing_trie_and_index(self):
        user, _, _ = self.graph.add_user("marvel_dev", "Python algorithms")
        self.trie.add_user(user)
        self.search.add_user_to_index(user)

        autocomplete_ids = {
            candidate.id for candidate, _ in self.trie.autocomplete("marv*", 10)
        }
        bio_ids = {
            candidate.id
            for candidate, _, _ in self.search.search_by_bio("algorithms", 10)
        }

        self.assertIn(user.id, autocomplete_ids)
        self.assertIn(user.id, bio_ids)

    def test_rejects_empty_queries_and_nonpositive_result_counts(self):
        with self.assertRaises(ValueError):
            self.search.search_by_username("", 10)
        with self.assertRaises(ValueError):
            self.search.search_by_bio("python", 0)
        with self.assertRaises(ValueError):
            self.trie.autocomplete("mar", 0)


if __name__ == "__main__":
    unittest.main()
