import heapq


class RecommendationEngine:
    def __init__(self, social_graph):
        self.social_graph = social_graph

    def recommend_users(
        self,
        start_user_id,
        alpha=0.5,
        number_of_results=10,
        damping_factor=0.85,
        epsilon=1e-6,
        max_iterations=100
    ):
        """
        Preporucuje korisnike kombinovanjem Personalized PageRank-a
        i Jaccard slicnosti biografija.

        Ne preporucuju se pocetni korisnik, korisnici koje vec prati,
        korisnici koje je blokirao i korisnici koji su blokirali njega.
        """
        self._validate_request(
            start_user_id,
            alpha,
            number_of_results
        )
        self._ensure_pagerank_is_calculated()

        personalized_ranks, iterations, difference = (
            self.social_graph.calculate_personalized_pagerank(
                start_user_id,
                damping_factor,
                epsilon,
                max_iterations
            )
        )

        start_user = self.social_graph.users_by_id[start_user_id]

        excluded_user_ids = {start_user_id}
        excluded_user_ids.update(
            self.social_graph.outgoing_connections[start_user_id]
        )
        excluded_user_ids.update(
            self.social_graph.blocked_out[start_user_id]
        )
        excluded_user_ids.update(
            self.social_graph.blocked_in[start_user_id]
        )

        candidates = []

        for candidate_user in self.social_graph.users_by_id.values():
            if candidate_user.id in excluded_user_ids:
                continue

            content_similarity = self.jaccard_similarity(
                start_user.bio_tokens,
                candidate_user.bio_tokens
            )
            personalized_rank = personalized_ranks[candidate_user.id]

            combined_score = (
                alpha * personalized_rank
                + (1.0 - alpha) * content_similarity
            )

            if combined_score <= 0.0:
                continue

            global_rank = self.social_graph.pagerank[candidate_user.id]

            candidates.append((
                candidate_user.id,
                combined_score,
                personalized_rank,
                content_similarity,
                global_rank
            ))

        top_items = heapq.nlargest(
            number_of_results,
            candidates,
            key=lambda item: (
                item[1],
                item[4],
                -item[0]
            )
        )

        results = []

        for (
            user_id,
            combined_score,
            personalized_rank,
            content_similarity,
            global_rank
        ) in top_items:
            user = self.social_graph.users_by_id[user_id]

            results.append((
                user,
                combined_score,
                personalized_rank,
                content_similarity,
                global_rank
            ))

        return results, iterations, difference

    def jaccard_similarity(self, first_tokens, second_tokens):
        """
        Racuna odnos preseka i unije dva skupa reci.
        """
        union = first_tokens | second_tokens

        if not union:
            return 0.0

        intersection = first_tokens & second_tokens
        return len(intersection) / len(union)

    def _validate_request(
        self,
        start_user_id,
        alpha,
        number_of_results
    ):
        if start_user_id not in self.social_graph.users_by_id:
            raise ValueError(
                f"Korisnik sa ID-jem {start_user_id} ne postoji."
            )

        if (
            not isinstance(alpha, (int, float))
            or isinstance(alpha, bool)
            or not 0.0 <= alpha <= 1.0
        ):
            raise ValueError(
                "Alpha mora biti broj izmedju 0 i 1."
            )

        if (
            not isinstance(number_of_results, int)
            or isinstance(number_of_results, bool)
            or number_of_results <= 0
        ):
            raise ValueError(
                "Broj preporuka mora biti pozitivan ceo broj."
            )

    def _ensure_pagerank_is_calculated(self):
        if not self.social_graph.pagerank:
            raise ValueError(
                "PageRank nije izracunat. "
                "Prvo pozovite calculate_pagerank()."
            )
