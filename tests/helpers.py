from pathlib import Path

from social_graph import SocialGraph


USERS = """\
1|alice|Python data graphs
2|bob|Python networks
3|carol|Art and design
4|dave|Data science
5|erin|Python data
6|marko_ai|Machine learning
7|maria_dev|Python developer
8|marketing_notes|Marketing analytics
"""

CONNECTIONS = """\
1|2
1|3
2|3
2|4
3|1
3|5
4|5
5|6
6|7
7|8
8|1
"""

BLOCKED = """\
1|6
5|2
"""


def write_dataset(directory, users=USERS, connections=CONNECTIONS, blocked=BLOCKED):
    data_directory = Path(directory)
    data_directory.mkdir(parents=True, exist_ok=True)
    (data_directory / "users.txt").write_text(users, encoding="utf-8")
    (data_directory / "connections.txt").write_text(
        connections,
        encoding="utf-8",
    )
    (data_directory / "blocked.txt").write_text(blocked, encoding="utf-8")
    return data_directory


def load_graph(directory, users=USERS, connections=CONNECTIONS, blocked=BLOCKED):
    data_directory = write_dataset(directory, users, connections, blocked)
    graph = SocialGraph()
    graph.load_from_directory(data_directory)
    return graph
