# Social Network Analysis and User Recommendation System

[Srpska verzija](README.sr.md)

University course project for **Algorithms and Data Structures**, developed during the 2025/2026 academic year at the Faculty of Technical Sciences, University of Novi Sad.

## Overview

This Python console application models a directed social graph and provides tools for exploring its structure, finding users, ranking influence, managing connections, and generating personalized user recommendations.

The application works with three supplied synthetic datasets and implements its core data structures and algorithms without third-party libraries.

## Highlights

- directed follow graph with blocking rules;
- global influence ranking using PageRank;
- username and biography search with relevance ranking;
- trie-based autocomplete;
- spelling suggestions using Levenshtein distance;
- breadth-first search for connection levels;
- hybrid recommendations using Personalized PageRank and Jaccard similarity;
- runtime addition of users and follow connections;
- chronological history of connections created during the current session;
- benchmark support for all three datasets.

## Datasets

| Dataset | Users | Follow connections | Blocks |
|---|---:|---:|---:|
| `small` | 1,000 | 80,693 | 20 |
| `medium` | 10,000 | 354,503 | 200 |
| `full` | 81,306 | 1,768,135 | 1,626 |

The supplied profiles and relationships are synthetic and intended exclusively for the academic assignment.

Each directory under `data/` contains:

| File | Format | Meaning |
|---|---|---|
| `users.txt` | `id\|username\|bio` | user profiles |
| `connections.txt` | `from_id\|to_id` | directed follow connections |
| `blocked.txt` | `blocker_id\|blocked_id` | directed blocking relationships |

## Data structures and algorithms

| Area | Implementation |
|---|---|
| Graph representation | hash maps, outgoing sets, incoming lists, and outdegree map |
| Global ranking | iterative PageRank with damping factor `0.85`, tolerance `1e-6`, dangling-node handling, and warm start |
| Top results | heaps for PageRank, search, autocomplete, spelling suggestions, and recommendations |
| Username search | exact hash-map lookup, trie prefix search, and substring matching |
| Biography search | inverted index with relevance scoring |
| Autocomplete | custom trie implementation, ranked by PageRank |
| Spelling suggestions | custom two-row dynamic-programming implementation of Levenshtein distance |
| Connection levels | breadth-first search using a `deque` and visited set |
| Recommendations | custom Personalized PageRank and Jaccard biography similarity |

The hybrid recommendation score is:

```text
alpha * Personalized PageRank + (1 - alpha) * Jaccard similarity
```

Candidates exclude the selected user, already-followed users, and users involved in a block in either direction.

## Requirements

- Python 3.11 or newer is recommended.
- No external packages are required; the project uses only the Python standard library.

## Running the application

From the project root, run:

```bash
python main.py
```

Choose a dataset when prompted:

```text
1 - small
2 - medium
3 - full
```

Pressing Enter selects `small`. Entering `x` inside a feature returns to the main menu.

The `small` dataset is suitable for quick checks, `medium` for an interactive demonstration, and `full` for performance testing.

## Console features

| Option | Feature |
|---:|---|
| 1 | search by username |
| 2 | search by biography terms |
| 3 | display the most influential users |
| 4 | add a follow connection |
| 5 | display interaction history |
| 6 | autocomplete a username |
| 7 | generate hybrid recommendations |
| 8 | display BFS connection levels |
| 9 | show "Did you mean" suggestions |
| 10 | add a new user |
| 0 | exit |

## Project structure

| Path | Purpose |
|---|---|
| `main.py` | dataset selection, loading, and application startup |
| `console_app.py` | console menu, input handling, and result display |
| `user.py` | `User` model and biography tokenization |
| `interaction.py` | `FollowInteraction` model |
| `social_graph.py` | graph storage, PageRank, PPR, BFS, users, connections, and history |
| `trie.py` | custom trie and autocomplete |
| `search_engine.py` | username and biography search, inverted index, and spelling suggestions |
| `recommendation_engine.py` | Jaccard similarity and hybrid recommendations |
| `benchmark.py` | representative performance measurements |
| `tests/` | automated unit and integration tests |
| `data/` | supplied `small`, `medium`, and `full` datasets |

## Automated tests

Run the test suite from the project root:

```bash
python -m unittest discover -s tests -v
```

The 23 tests cover graph loading and mutation, PageRank and Personalized PageRank convergence, blocking rules, interaction history, BFS, trie operations, search relevance, spelling suggestions, index updates, recommendation filtering and ranking, and integration with the supplied `small` dataset.

## Benchmark

Run the benchmark with:

```bash
python benchmark.py
```

It measures dataset loading, PageRank, index construction, search, autocomplete, spelling suggestions, BFS, recommendations, graph mutations, interaction history, and dynamic index updates. The benchmark evaluates performance, while the automated tests verify correctness.

The `full` run may take several minutes because it performs multiple PageRank and Personalized PageRank calculations.

### Results for the full dataset

The following values are averages from five consecutive runs on the same computer using Python 3.11.1 and Windows 11. The range shows the minimum and maximum observed time.

| Operation | Average time | Measured range |
|---|---:|---:|
| Input file loading | 5.49 s | 5.11-6.06 s |
| Initial PageRank | 47.35 s | 45.33-48.03 s |
| Trie construction | 2.97 s | 2.89-3.08 s |
| Inverted-index construction | 0.815 s | 0.795-0.850 s |
| Did you mean | 0.109 s | 0.106-0.112 s |
| BFS to level 3 | 0.055 s | 0.051-0.058 s |
| Hybrid recommendations | 53.75 s | 50.66-58.34 s |
| New connection and warm-start PageRank | 4.25 s | 3.91-4.49 s |
| New user and PageRank from scratch | 48.97 s | 45.86-51.11 s |
| Total initial initialization | 56.63 s | 54.61-57.68 s |
| PPR and two graph mutations | 106.98 s | 100.44-112.83 s |

A complete `full` benchmark run took approximately 2 minutes and 44 seconds on average, ranging from about 2:35 to 2:50. Regular interactive operations such as username and biography search, top-user selection, and autocomplete each completed in less than 0.017 seconds.

All five runs produced the same algorithmic results: 81,306 users and 1,768,135 connections, 58 PageRank iterations, 59 Personalized PageRank iterations, 504,027 trie nodes, 148,143 unique indexed words, and 30,198 users reached by BFS up to level 3.

Times depend on hardware, operating system, Python version, and current system load.

## Scope and limitations

- Users and connections added through the menu exist only during the current run and are not written back to the input files.
- The history contains only connections created during the current session because the supplied connections do not include timestamps.
- The project focuses on graph algorithms, data structures, search, and recommendations rather than implementing a complete social networking platform.

## Academic context

This project was created individually as the second project assignment for the **Algorithms and Data Structures** course. Its purpose was to apply graph structures, hashing, heaps, tries, breadth-first search, dynamic programming, indexing, and ranking algorithms to a larger dataset.
