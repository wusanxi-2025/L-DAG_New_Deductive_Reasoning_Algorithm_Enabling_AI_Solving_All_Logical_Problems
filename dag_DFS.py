from collections import defaultdict
import argparse
import json
import networkx as nx
import matplotlib.pyplot as plt

# Read graph data from an external file
def read_graph_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            edges = json.load(file)
            return edges
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        print_usage()
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_name}' is not in valid JSON format.")
        print_usage()
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        print_usage()
        return None

# Topological Sort using DFS
def topological_sort_dfs(graph):
    def dfs(node):
        if node in visited:
            if node in recursion_stack:
                raise ValueError("Graph contains a cycle")
            return
        
        visited.add(node)
        recursion_stack.add(node)
        
        for neighbor in graph[node]:
            dfs(neighbor)
        
        recursion_stack.remove(node)
        result.append(node)
    
    visited = set()
    recursion_stack = set()
    result = []
    
    for node in graph:
        if node not in visited:
            dfs(node)
    
    return result[::-1]

# Find the deepest path in the DAG
def find_deepest_path(graph, topological_order):
    depths = {node: 0 for node in graph}
    for node in topological_order:
        for neighbor in graph[node]:
            depths[neighbor] = max(depths[neighbor], depths[node] + 1)
    
    max_depth = max(depths.values())
    deepest_node = max(depths, key=depths.get)
    
    path = []
    current = deepest_node
    while current is not None:
        path.append(current)
        current = max(
            (node for node in graph if current in graph[node]),
            key=lambda x: depths[x],
            default=None
        )
    
    return path[::-1]

# Print usage instructions
def print_usage():
    usage_text = """
    Usage Instructions:
    1. Create a JSON file containing the edges of the graph.
       - The JSON file should be formatted as a list of edge pairs. Each edge is represented by a pair of nodes (source, target).
       - Example format: [[1, 5], [1, 23], [2, 4], [2, 5], ...]
       - Ensure each pair represents a directed edge from the first element to the second element.
    2. Ensure the JSON file is in the same directory as this script or provide the correct path.
    3. Run the script with the command: python script_name.py <input_file>
       Replace <input_file> with the name of your input JSON file.

    Example: python script_name.py graph_edges.json

    Note: The script will check if the provided graph is a Directed Acyclic Graph (DAG). If it is, it will perform a topological sort and save the result to 'topological_sort.txt'.
    It will also visualize the graph layout and save the visualization as an image file.
    """
    print(usage_text)

# Main function to execute the program
def main():
    # Parsing command line arguments
    parser = argparse.ArgumentParser(description="Read graph data from a JSON file and perform operations on it.")
    parser.add_argument('input_file', type=str, help="The name of the input JSON file containing graph edges")
    args = parser.parse_args()

    # Reading the graph data from the file
    edges = read_graph_from_file(args.input_file)

    if edges is None:
        print("Program terminated due to file reading error.")
        return

    # Create the graph from the edges
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        if v not in graph:
            graph[v] = []

    # Perform topological sorting
    try:
        topological_order = topological_sort_dfs(graph)
        print("Topological order:", topological_order)
    except ValueError as e:
        print(e)
        return

    # Find the deepest path
    deepest_path = find_deepest_path(graph, topological_order)
    print("Deepest path:", deepest_path)
    print("Depth:", len(deepest_path) - 1)

    # Generate graphical representation of the graph
    G = nx.DiGraph()
    G.add_edges_from(edges)

    # Set spring layout parameters
    k_value = 3
    iterations_value = 10
    seed_value = 40

    # Use Spring Layout
    pos = nx.spring_layout(G, k=k_value, iterations=iterations_value, seed=seed_value)

    # Plot the graph and save it as an image file with parameters in the file name
    file_name = f"dag_graph_k{k_value}_iter{iterations_value}_seed{seed_value}.png"
    nx.draw(G, pos, with_labels=True, node_color='lightblue', arrows=True)

    # Add title to the graph with layout parameters
    plt.title(f"Graph Layout (k={k_value}, iterations={iterations_value}, seed={seed_value})")

    # Save the graph as an image file
    plt.savefig(file_name)
    plt.show()

if __name__ == "__main__":
    main()
