import unittest
from pathlib import Path

from search_engine import SearchEngine
from social_graph import SocialGraph
from trie import UsernameTrie


class TestSmallDatasetIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        project_directory = Path(__file__).resolve().parents[1]
        cls.graph = SocialGraph()
        cls.graph.load_from_directory(project_directory / "data" / "small")
        cls.graph.calculate_pagerank()
        cls.trie = UsernameTrie(cls.graph)
        cls.search = SearchEngine(cls.graph, cls.trie)

    def test_expected_dataset_size(self):
        self.assertEqual(self.graph.number_of_users(), 1000)
        self.assertEqual(self.graph.number_of_connections(), 80693)
        self.assertEqual(self.graph.number_of_blocks(), 20)

    def test_documented_search_and_autocomplete_examples(self):
        exact = self.search.search_by_username("markohulyo", 10)
        autocomplete = self.trie.autocomplete("mar*", 10)

        self.assertEqual(exact[0][0].username, "markohulyo")
        self.assertEqual(exact[0][1], 3)
        self.assertTrue(autocomplete)
        self.assertTrue(
            all(user.username.casefold().startswith("mar") for user, _ in autocomplete)
        )


if __name__ == "__main__":
    unittest.main()
