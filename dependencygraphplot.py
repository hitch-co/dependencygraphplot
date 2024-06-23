import random
import math
import pandas as pd

class ForceDirectedGraph:
    def __init__(self, items: list[dict], attraction=1, repulsion=3, timestep=0.01, iterations=5000, max_distance=10.0):
        self.items = items
        self.attraction = attraction
        self.repulsion = repulsion
        self.timestep = timestep
        self.iterations = iterations
        self.max_distance = max_distance
        self.nodes = [self.Node(item['item']) for item in items]
        self.edges = []
        self._create_edges()

    class Node:
        def __init__(self, item):
            self.item = item
            self.x = random.uniform(-1, 1)
            self.y = random.uniform(-1, 1)
            self.vx = 0
            self.vy = 0

    class Edge:
        def __init__(self, node1, node2):
            self.node1 = node1
            self.node2 = node2

    def _create_edges(self):
        item_map = {node.item: node for node in self.nodes}
        for item in self.items:
            node = item_map[item['item']]
            dependencies = item.get('dependencies', '')
            if pd.isna(dependencies) or dependencies == 'None':
                dependencies = ''
            dependencies = dependencies.strip('{}')
            for dep in dependencies.split(','):
                dep = dep.strip()
                if dep in item_map:
                    self.edges.append(self.Edge(node, item_map[dep]))

    def _calculate_forces(self):
        for edge in self.edges:
            dx = edge.node2.x - edge.node1.x
            dy = edge.node2.y - edge.node1.y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance == 0:
                continue
            force = self.attraction * (distance - 1)
            fx = force * dx / distance
            fy = force * dy / distance
            edge.node1.vx += fx
            edge.node1.vy += fy
            edge.node2.vx -= fx
            edge.node2.vy -= fy

        for i, node1 in enumerate(self.nodes):
            for node2 in self.nodes[i+1:]:
                dx = node2.x - node1.x
                dy = node2.y - node1.y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance == 0:
                    continue
                if distance < self.max_distance:  # Only apply repulsion within a maximum distance
                    force = self.repulsion / (distance * distance)
                    fx = force * dx / distance
                    fy = force * dy / distance
                    node1.vx -= fx
                    node1.vy -= fy
                    node2.vx += fx
                    node2.vy += fy


    def _update_positions(self):
        for node in self.nodes:
            node.x += node.vx * self.timestep
            node.y += node.vy * self.timestep
            node.vx = 0
            node.vy = 0

    def gen_list_of_tuples(self) -> list[tuple]:
        for _ in range(self.iterations):
            self._calculate_forces()
            self._update_positions()
        return [(node.item, node.x, node.y) for node in self.nodes]
    
    def gen_nodes_df(self) -> pd.DataFrame:
        layout = self.gen_list_of_tuples()
        return pd.DataFrame(layout, columns=['item', 'x', 'y'])
    
    def gen_edges_df(self) -> pd.DataFrame:
        edges_data = []
        for edge in self.edges:
            edges_data.append({
                'source': edge.node1.item,
                'target': edge.node2.item,
                'x1': edge.node1.x,
                'y1': edge.node1.y,
                'x2': edge.node2.x,
                'y2': edge.node2.y
            })
        return pd.DataFrame(edges_data)

    def generate_intermediate_points(self, x1, y1, x2, y2, num_points=10):
        points = []
        for i in range(1, num_points):
            t = i / num_points
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            points.append((x, y))
        return points

    def transform_to_long_format(self, num_intermediate_points=10):
        long_format_data = []
        edges_df = self.gen_edges_df()
        edges_list = edges_df.to_dict(orient="records")

        for edge in edges_list:
            # Append the source node (no step indicator)
            long_format_data.append({
                "task_name": edge["source"],
                "x": edge["x1"],
                "y": edge["y1"],
                "path_order": 1,  # Source node is the first point in the path
                "step": 0,  # Indicate this is a node
                "type": "source",
                "node_type": "node"
            })

            # Generate intermediate points
            intermediate_points = self.generate_intermediate_points(edge["x1"], edge["y1"], edge["x2"], edge["y2"], num_points=num_intermediate_points)
            
            # Initialize path_order for intermediate points
            path_order = 2  # Starts from 2 for the first intermediate point
            step = 1  # Step starts from 1

            # Append intermediate points with step indicators
            for x, y in intermediate_points:
                long_format_data.append({
                    "task_name": edge["source"],  # Keep the task_name as the source task
                    "x": x,
                    "y": y,
                    "path_order": path_order,  # path_order for intermediate points starts from 2
                    "step": step,  # Step indicator starts from 1
                    "type": "step",
                    "node_type": "edge"
                })
                path_order += 1  # Increment path_order for each intermediate point
                step += 1  # Increment step for each intermediate point
            
            # Append the target node (no step indicator)
            long_format_data.append({
                "task_name": edge["target"],
                "x": edge["x2"],
                "y": edge["y2"],
                "path_order": path_order,  # Last path_order after intermediate points
                "step": 0,  # Indicate this is a node
                "type": "target",
                "node_type": "node"
            })
        
        # Convert the list to a DataFrame
        df_long = pd.DataFrame(long_format_data)
        return df_long


###########################
###########################
###########################
###########################
###########################
# Example usage
items = [
    {"item": "Item1", "dependencies": "{Item5,Item3}"},
    {"item": "Item2", "dependencies": "{Item1,Item3,Item4}"},
    {"item": "Item3", "dependencies": ""},
    {"item": "Item4", "dependencies": "{Item3}"},
    {"item": "Item5", "dependencies": "{Item2,Item4}"}
]

graph = ForceDirectedGraph(items)
nodes_df = graph.gen_nodes_df()
edges_df = graph.gen_edges_df()

# Print or save the dataframes to CSV files
print(nodes_df)
print(edges_df)

nodes_df.to_csv('nodes.csv', index=False)
edges_df.to_csv('edges.csv', index=False)


###########################
###########################
###########################
###########################
###########################
# Transform to long format
long_format_data = []

# gbefore the loop, format the df as a list of dictionaries
# format edges_df as a list of dictionaries
edges_list = edges_df.to_dict(orient="records")

for edge in edges_list:
    long_format_data.append({"item": edge["source"], "x": edge["x1"], "y": edge["y1"], "path_order": 1})
    long_format_data.append({"item": edge["target"], "x": edge["x2"], "y": edge["y2"], "path_order": 2})

# Create a DataFrame
df_long = pd.DataFrame(long_format_data)

# Save to CSV
df_long.to_csv("edges_long_format.csv", index=False)


###########################
###########################
###########################
###########################
###########################
# Extract unique nodes and their coordinates
nodes = {}
for edge in edges_list:
    nodes[edge["source"]] = (edge["x1"], edge["y1"])
    nodes[edge["target"]] = (edge["x2"], edge["y2"])

# Convert nodes dictionary to a DataFrame
nodes_data = [{"item": item, "x": coords[0], "y": coords[1]} for item, coords in nodes.items()]
df_nodes = pd.DataFrame(nodes_data)

# Convert edges to DataFrame
df_edges = pd.DataFrame(edges_list)

# Save to CSV
df_nodes.to_csv("nodes_new.csv", index=False)
df_edges.to_csv("edges_new.csv", index=False)