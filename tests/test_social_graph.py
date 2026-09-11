import tempfile
import unittest

from tests.helpers import load_graph


class TestSocialGraph(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.graph = load_graph(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_loads_users_connections_and_blocks(self):
        self.assertEqual(self.graph.number_of_users(), 8)
        self.assertEqual(self.graph.number_of_connections(), 11)
        self.assertEqual(self.graph.number_of_blocks(), 2)
        self.assertEqual(self.graph.get_user_by_username("ALICE").id, 1)

    def test_pagerank_converges_and_sums_to_one(self):
        iterations, difference = self.graph.calculate_pagerank()

        self.assertLess(iterations, 100)
        self.assertLess(difference, 1e-6)
        self.assertAlmostEqual(sum(self.graph.pagerank.values()), 1.0)
        self.assertTrue(all(rank > 0 for rank in self.graph.pagerank.values()))

    def test_personalized_pagerank_starts_from_selected_user(self):
        ranks, iterations, difference = self.graph.calculate_personalized_pagerank(1)

        self.assertLess(iterations, 100)
        self.assertLess(difference, 1e-6)
        self.assertAlmostEqual(sum(ranks.values()), 1.0)
        self.assertEqual(set(ranks), set(self.graph.users_by_id))

    def test_adds_follow_connection_and_updates_both_directions(self):
        self.graph.calculate_pagerank()

        interaction, iterations, difference = self.graph.add_follow_connection(1, 4)

        self.assertIn(4, self.graph.outgoing_connections[1])
        self.assertIn(1, self.graph.incoming_connections[4])
        self.assertEqual(self.graph.out_degree[1], 3)
        self.assertEqual(interaction.sequence_number, 1)
        self.assertGreater(iterations, 0)
        self.assertLess(difference, 1e-6)

    def test_rejects_self_follow_duplicate_and_blocked_connections(self):
        with self.assertRaisesRegex(ValueError, "samog sebe"):
            self.graph.add_follow_connection(1, 1)
        with self.assertRaisesRegex(ValueError, "vec postoji"):
            self.graph.add_follow_connection(1, 2)
        with self.assertRaisesRegex(ValueError, "blokiranje"):
            self.graph.add_follow_connection(1, 6)
        with self.assertRaisesRegex(ValueError, "blokiranje"):
            self.graph.add_follow_connection(6, 1)

        self.assertEqual(self.graph.number_of_connections(), 11)

    def test_records_chronological_history_for_both_users(self):
        self.graph.calculate_pagerank()
        self.graph.add_follow_connection(1, 4)
        self.graph.add_follow_connection(4, 2)

        alice_history = self.graph.get_interaction_history(1)
        dave_history = self.graph.get_interaction_history(4)

        self.assertEqual(
            [(item[0], item[1], item[2].id) for item in alice_history],
            [(1, "followed", 4)],
        )
        self.assertEqual(
            [(item[0], item[1], item[2].id) for item in dave_history],
            [(1, "followed_by", 1), (2, "followed", 2)],
        )

    def test_bfs_returns_each_user_at_the_first_reachable_level(self):
        levels = self.graph.get_connection_levels(1, 3)

        self.assertEqual([user.id for user in levels[1]], [2, 3])
        self.assertEqual([user.id for user in levels[2]], [4, 5])
        self.assertEqual([user.id for user in levels[3]], [6])

    def test_add_user_initializes_all_graph_structures(self):
        self.graph.calculate_pagerank()

        user, iterations, difference = self.graph.add_user(
            "new_user",
            "Python algorithms",
        )

        self.assertEqual(user.id, 9)
        self.assertIs(self.graph.get_user_by_username("NEW_USER"), user)
        self.assertEqual(self.graph.outgoing_connections[user.id], set())
        self.assertEqual(self.graph.incoming_connections[user.id], [])
        self.assertEqual(self.graph.blocked_out[user.id], set())
        self.assertEqual(self.graph.interaction_history[user.id], [])
        self.assertGreater(iterations, 0)
        self.assertLess(difference, 1e-6)

    def test_rejects_duplicate_username_case_insensitively(self):
        with self.assertRaisesRegex(ValueError, "vec postoji"):
            self.graph.add_user("ALICE", "Another biography")


if __name__ == "__main__":
    unittest.main()
