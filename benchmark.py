from pathlib import Path
from time import perf_counter
import sys

from recommendation_engine import RecommendationEngine
from search_engine import SearchEngine
from social_graph import SocialGraph
from trie import UsernameTrie


DATASET_BY_CHOICE = {
    "1": "small",
    "2": "medium",
    "3": "full"
}


def read_dataset_name():
    print("Izaberite skup podataka za benchmark:")
    print("1 - small")
    print("2 - medium")
    print("3 - full")

    while True:
        choice = input("Izbor: ").strip()

        if choice in DATASET_BY_CHOICE:
            return DATASET_BY_CHOICE[choice]

        print("Neispravan izbor. Unesite 1, 2 ili 3.")


def print_result(operation_name, elapsed_time, details=""):
    if details:
        print(
            f"{operation_name:<43} {elapsed_time:>10.6f} s  {details}"
        )
    else:
        print(f"{operation_name:<43} {elapsed_time:>10.6f} s")


def main():
    dataset_name = read_dataset_name()

    project_directory = Path(__file__).resolve().parent
    data_directory = project_directory / "data" / dataset_name

    print()
    print("=" * 84)
    print(f"BENCHMARK - {dataset_name.upper()} SKUP")
    print("=" * 84)
    python_version = (
        f"{sys.version_info.major}."
        f"{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )
    print(f"Python: {python_version}")

    if dataset_name == "full":
        print(
            "Napomena: kompletan benchmark full skupa moze trajati "
            "nekoliko minuta."
        )

    print("-" * 84)

    graph = SocialGraph()

    print("Merenje ucitavanja...", flush=True)
    start_time = perf_counter()
    graph.load_from_directory(data_directory)
    loading_time = perf_counter() - start_time
    print_result(
        "Ucitavanje ulaznih fajlova",
        loading_time,
        f"V={graph.number_of_users()}, E={graph.number_of_connections()}"
    )

    print("Merenje pocetnog PageRank-a...", flush=True)
    start_time = perf_counter()
    pagerank_iterations, pagerank_difference = graph.calculate_pagerank()
    pagerank_time = perf_counter() - start_time
    print_result(
        "Pocetni PageRank",
        pagerank_time,
        (
            f"iteracije={pagerank_iterations}, "
            f"razlika={pagerank_difference:.10f}"
        )
    )

    print("Merenje formiranja trie-a...", flush=True)
    start_time = perf_counter()
    username_trie = UsernameTrie(graph)
    trie_time = perf_counter() - start_time
    print_result(
        "Formiranje trie-a",
        trie_time,
        (
            f"username-ovi={username_trie.number_of_usernames()}, "
            f"cvorovi={username_trie.number_of_nodes()}"
        )
    )

    print("Merenje formiranja inverted index-a...", flush=True)
    start_time = perf_counter()
    search_engine = SearchEngine(graph, username_trie)
    index_time = perf_counter() - start_time
    print_result(
        "Formiranje inverted index-a",
        index_time,
        f"jedinstvene_reci={search_engine.number_of_indexed_words()}"
    )

    recommendation_engine = RecommendationEngine(graph)

    start_time = perf_counter()
    username_results = search_engine.search_by_username("mark", 10)
    elapsed_time = perf_counter() - start_time
    print_result(
        "Pretraga username-a: mark",
        elapsed_time,
        f"rezultati={len(username_results)}"
    )

    start_time = perf_counter()
    bio_results = search_engine.search_by_bio("data networks", 10)
    elapsed_time = perf_counter() - start_time
    print_result(
        "Pretraga biografije: data networks",
        elapsed_time,
        f"rezultati={len(bio_results)}"
    )

    start_time = perf_counter()
    top_users = graph.get_top_users_by_pagerank(10)
    elapsed_time = perf_counter() - start_time
    print_result(
        "Top 10 PageRank korisnika",
        elapsed_time,
        f"rezultati={len(top_users)}"
    )

    start_time = perf_counter()
    autocomplete_results = username_trie.autocomplete("mar*", 10)
    elapsed_time = perf_counter() - start_time
    print_result(
        "Autocomplete: mar*",
        elapsed_time,
        f"rezultati={len(autocomplete_results)}"
    )

    start_time = perf_counter()
    suggestion_results = search_engine.suggest_usernames(
        "luis",
        5,
        3
    )
    elapsed_time = perf_counter() - start_time
    print_result(
        "Did you mean: luis",
        elapsed_time,
        f"rezultati={len(suggestion_results)}"
    )

    start_user = graph.get_user_by_username("reece99")

    if start_user is None:
        raise SystemExit(
            "Benchmark korisnik reece99 nije pronadjen."
        )

    start_time = perf_counter()
    bfs_levels = graph.get_connection_levels(start_user.id, 3)
    elapsed_time = perf_counter() - start_time
    reached_users = 0

    for users in bfs_levels.values():
        reached_users += len(users)

    print_result(
        "BFS: reece99, nivo 3",
        elapsed_time,
        f"dostignuti_korisnici={reached_users}"
    )

    print("Merenje PPR-a i hibridnih preporuka...", flush=True)
    start_time = perf_counter()
    recommendations, ppr_iterations, ppr_difference = (
        recommendation_engine.recommend_users(
            start_user.id,
            0.5,
            10
        )
    )
    recommendation_time = perf_counter() - start_time
    print_result(
        "Hibridne preporuke: reece99",
        recommendation_time,
        (
            f"rezultati={len(recommendations)}, "
            f"PPR_iteracije={ppr_iterations}, "
            f"razlika={ppr_difference:.10f}"
        )
    )

    follower = graph.get_user_by_username("guimanja")
    followed = graph.get_user_by_username("itsenglishtime")

    if follower is None or followed is None:
        raise SystemExit(
            "Benchmark korisnici za novu vezu nisu pronadjeni."
        )

    print("Merenje dodavanja veze i warm-start PageRank-a...", flush=True)
    start_time = perf_counter()
    interaction, connection_iterations, connection_difference = (
        graph.add_follow_connection(
            follower.id,
            followed.id
        )
    )
    connection_time = perf_counter() - start_time
    print_result(
        "Nova veza i warm-start PageRank",
        connection_time,
        (
            f"interakcija={interaction.sequence_number}, "
            f"iteracije={connection_iterations}, "
            f"razlika={connection_difference:.10f}"
        )
    )

    start_time = perf_counter()
    follower_history = graph.get_interaction_history(follower.id)
    followed_history = graph.get_interaction_history(followed.id)
    history_time = perf_counter() - start_time
    print_result(
        "Provera istorije nove veze",
        history_time,
        (
            f"pratilac_interakcije={len(follower_history)}, "
            f"praceni_interakcije={len(followed_history)}"
        )
    )

    print("Merenje dodavanja korisnika i PageRank-a od pocetka...", flush=True)
    start_time = perf_counter()
    new_user, user_iterations, user_difference = graph.add_user(
        "asp_benchmark_user",
        "Python data networks algorithms aspbenchmarktoken"
    )
    username_trie.add_user(new_user)
    search_engine.add_user_to_index(new_user)
    user_addition_time = perf_counter() - start_time
    print_result(
        "Novi korisnik i PageRank od pocetka",
        user_addition_time,
        (
            f"ID={new_user.id}, iteracije={user_iterations}, "
            f"razlika={user_difference:.10f}"
        )
    )

    start_time = perf_counter()
    new_user_search = search_engine.search_by_username(
        "asp_benchmark_user",
        5
    )
    new_user_autocomplete = username_trie.autocomplete(
        "asp_benchmark*",
        5
    )
    new_user_bio_search = search_engine.search_by_bio(
        "aspbenchmarktoken",
        5
    )
    new_user_check_time = perf_counter() - start_time

    found_in_username_search = any(
        result[0].id == new_user.id
        for result in new_user_search
    )
    found_in_autocomplete = any(
        result[0].id == new_user.id
        for result in new_user_autocomplete
    )
    found_in_bio_search = any(
        result[0].id == new_user.id
        for result in new_user_bio_search
    )

    print_result(
        "Provera novog korisnika u indeksima",
        new_user_check_time,
        (
            f"username={found_in_username_search}, "
            f"autocomplete={found_in_autocomplete}, "
            f"bio={found_in_bio_search}"
        )
    )

    total_initialization_time = (
        loading_time + pagerank_time + trie_time + index_time
    )

    total_expensive_operations_time = (
        recommendation_time
        + connection_time
        + user_addition_time
    )

    print("-" * 84)
    print_result(
        "Ukupna pocetna inicijalizacija",
        total_initialization_time
    )
    print_result(
        "PPR i dve mutacije grafa",
        total_expensive_operations_time
    )
    print("=" * 84)
    print(
        "Napomena: vremena zavise od hardvera, operativnog sistema, "
        "Python verzije i trenutnog opterecenja racunara."
    )


if __name__ == "__main__":
    main()
