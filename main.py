from pathlib import Path
from time import perf_counter

from console_app import ConsoleApplication
from recommendation_engine import RecommendationEngine
from search_engine import SearchEngine
from social_graph import SocialGraph
from trie import UsernameTrie


def choose_dataset():
    choices = {
        "1": "small",
        "2": "medium",
        "3": "full",
        "small": "small",
        "medium": "medium",
        "full": "full"
    }

    print("Izaberite skup podataka:")
    print("  1. small")
    print("  2. medium")
    print("  3. full")

    while True:
        try:
            choice = input("Izbor [1]: ").strip().casefold()
        except (EOFError, KeyboardInterrupt):
            print()
            raise SystemExit("Pokretanje programa je prekinuto.")

        if choice == "":
            return "small"

        dataset_name = choices.get(choice)

        if dataset_name is not None:
            return dataset_name

        print("Unesite 1, 2 ili 3, odnosno small, medium ili full.")


def build_application(dataset_name):
    project_directory = Path(__file__).resolve().parent
    data_directory = project_directory / "data" / dataset_name

    graph = SocialGraph()

    print()
    print(f"Ucitavanje skupa {dataset_name}...")
    loading_start = perf_counter()
    graph.load_from_directory(data_directory)
    loading_time = perf_counter() - loading_start

    print("Racunanje pocetnog PageRank-a...")
    pagerank_start = perf_counter()
    iterations, difference = graph.calculate_pagerank()
    pagerank_time = perf_counter() - pagerank_start

    print("Formiranje trie-a i inverted index-a...")
    structures_start = perf_counter()
    username_trie = UsernameTrie(graph)
    search_engine = SearchEngine(graph, username_trie)
    recommendation_engine = RecommendationEngine(graph)
    structures_time = perf_counter() - structures_start

    print()
    print(f"Uspesno je ucitan skup: {dataset_name}")
    print(f"Broj korisnika: {graph.number_of_users()}")
    print(f"Broj follow veza: {graph.number_of_connections()}")
    print(f"Broj blokiranja: {graph.number_of_blocks()}")
    print(f"Vreme ucitavanja fajlova: {loading_time:.4f} s")
    print(
        f"Vreme PageRank-a: {pagerank_time:.4f} s "
        f"({iterations} iteracija, razlika {difference:.10f})"
    )
    print(
        f"Vreme formiranja trie-a i inverted index-a: "
        f"{structures_time:.4f} s"
    )

    return ConsoleApplication(
        graph,
        search_engine,
        username_trie,
        recommendation_engine
    )


def main():
    dataset_name = choose_dataset()

    try:
        application = build_application(dataset_name)
    except FileNotFoundError as error:
        raise SystemExit(
            "Nisu pronadjeni potrebni ulazni fajlovi. "
            "Proverite data/small, data/medium i data/full foldere.\n"
            f"Detalji: {error}"
        ) from error
    except ValueError as error:
        raise SystemExit(
            f"Greska pri ucitavanju ili inicijalizaciji: {error}"
        ) from error

    application.run()


if __name__ == "__main__":
    main()
