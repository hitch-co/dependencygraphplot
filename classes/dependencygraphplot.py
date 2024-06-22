import random
import math
import pandas as pd

class ForceDirectedGraph:
    def __init__(self, items, attraction=0.1, repulsion=0.5, timestep=0.01, iterations=1000):
        self.items = items
        self.attraction = attraction
        self.repulsion = repulsion
        self.timestep = timestep
        self.iterations = iterations
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
            if pd.isna(dependencies):
                dependencies = ''
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

    def run(self):
        for _ in range(self.iterations):
            self._calculate_forces()
            self._update_positions()
        return [(node.item, node.x, node.y) for node in self.nodes]

# Example usage
items = [
    {"item": "Item1", "dependencies": "Item5,Item3"},
    {"item": "Item2", "dependencies": "Item1,Item3,Item4"},
    {"item": "Item3", "dependencies": ""},
    {"item": "Item4", "dependencies": "Item3"},
    {"item": "Item5", "dependencies": "Item2,Item4"}
]

graph = ForceDirectedGraph(items)
layout = graph.run()
for item, x, y in layout:
    print(f"{item}: ({x:.2f}, {y:.2f})")
