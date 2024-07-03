import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    """
    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")
    """

    print("What actor will you start with?")
    # source_name = "Kevin Bacon" #input()
    source = person_id_for_name("Olivia de Havilland")
    # source_name = "Emma Watson"
    print("What actor are you trying to get to?")
    # target_name = "chris sarandon"  # input()
    # target_name = "Chris Sarandon"
    target = person_id_for_name("Tom Cruise")  # input()
    # target = person_id_for_name("Robin Wright")  # input()

    queue = QueueFrontier()
    queue.add(Node(state=source, parent=None, action=None))

    path = bfs(queue, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def dfs(source, target, path, used_movies, used_people):
    queue = QueueFrontier()
    neighbors = neighbors_for_person(source, used_movies, used_people)

    new_used_movies = used_movies.copy()
    new_used_people = used_people.copy()

    if neighbors:
        for neighbor in neighbors:
            if neighbor["person_id"] == target:
                return path + [(neighbor["movie_id"], neighbor["person_id"])]
            queue.add(Node(state=neighbor["person_id"], parent=source, action=(neighbor["movie_id"], neighbor["person_id"])))
            new_used_movies.add(neighbor['movie_id'])
            new_used_people.add(neighbor["person_id"])
    else:
        return None

    paths = []

    for node in queue.frontier:
        new_path = path.copy()
        new_path.append(node.action)
        result = bfs(node.state, target, new_path, new_used_movies, new_used_people)
        if result:
            paths.append(result)

    if paths:  # Ensure there is at least one path in the list
        shortest_path = min(paths, key=len)  # Find the path with the minimum length
        return shortest_path
    else:
        print("No valid paths found.")

def bfs(queue, target):

    used_people = set()
    used_movies = set()
    while queue.frontier:
        current_node = queue.remove()
        used_people.add(current_node.state)
        print(f"person: {people[current_node.state]['name']}")

        neighbors = neighbors_for_person(current_node.state, used_movies, used_people)
        for neighbor in neighbors:
            used_movies.add(neighbors[0]['movie_id'])
            if neighbor['person_id'] == target:
                return reconstruct_path(Node(state=neighbor["person_id"], parent=current_node, action=(neighbor["movie_id"], neighbor["person_id"])))
            queue.add(
                Node(
                    state=neighbor["person_id"],
                    parent=current_node,
                    action=(neighbor["movie_id"], neighbor["person_id"]),
                )
            )  


def reconstruct_path(end_node):
    path = []
    current_node = end_node
    while current_node.parent is not None:
        path.append(
            current_node.action
        )  # Assuming action holds the necessary step data
        current_node = current_node.parent
    path.reverse()  # Reverse the path to start from the source
    return path


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id, used_movies, used_people):
    neighbors = []
    actors_movies = people[person_id]["movies"]
    for movie in actors_movies:
        if movie in used_movies:
            continue
        for neighbor in movies[movie]["stars"]:
            if neighbor in used_people:
                continue
            if person_id != neighbor:
                neighbors.append({"movie_id": movie, "person_id": neighbor})
    
    return neighbors


if __name__ == "__main__":
    main()
