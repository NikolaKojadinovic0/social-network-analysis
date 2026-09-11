import tempfile
import unittest

from recommendation_engine import RecommendationEngine
from tests.helpers import load_graph


class TestRecommendations(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.graph = load_graph(self.temporary_directory.name)
        self.graph.calculate_pagerank()
        self.engine = RecommendationEngine(self.graph)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_jaccard_similarity(self):
        self.assertEqual(self.engine.jaccard_similarity(set(), set()), 0.0)
        self.assertEqual(
            self.engine.jaccard_similarity({"python", "data"}, {"python", "web"}),
            1 / 3,
        )

    def test_recommendations_exclude_self_followed_and_blocked_users(self):
        results, iterations, difference = self.engine.recommend_users(1, 0.5, 10)
        result_ids = {item[0].id for item in results}

        self.assertTrue(result_ids.isdisjoint({1, 2, 3, 6}))
        self.assertGreater(iterations, 0)
        self.assertLess(difference, 1e-6)

    def test_results_are_sorted_by_combined_score(self):
        results, _, _ = self.engine.recommend_users(1, 0.5, 10)
        scores = [item[1] for item in results]

        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_alpha_zero_uses_content_similarity(self):
        results, _, _ = self.engine.recommend_users(1, 0.0, 10)

        for _, combined, _, jaccard, _ in results:
            self.assertEqual(combined, jaccard)

    def test_rejects_invalid_alpha(self):
        with self.assertRaises(ValueError):
            self.engine.recommend_users(1, 1.1, 10)


if __name__ == "__main__":
    unittest.main()
