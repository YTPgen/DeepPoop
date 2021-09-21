from typing import List
from deep_poop.effects.effect import EffectType
from numpy.core.fromnumeric import size
from numpy.lib.function_base import append
from deep_poop.effects.effect_graph import EffectNode
import networkx as nx
import matplotlib.pyplot as plt

from deep_poop import EFFECT_GRAPH


def node_size(node: EffectNode) -> int:
    return len(node.connections) * 500


def node_shape(node: EffectNode) -> str:
    return {
        EffectType.AUDIO: "^",
        EffectType.IMAGE: "o",
        EffectType.VIDEO: ",",
    }[node.effect.type]


def node_color(node: EffectNode) -> str:
    brightness = 150
    h = abs(hash(node.name)) % (255 - brightness) + brightness
    rgb = [h, h * h, h * h * h]
    rgb = [v % (255 - brightness) + brightness for v in rgb]
    return "#%02X%02X%02X" % tuple(rgb)


def indexes_with_shape(G, shape: str) -> List[int]:
    indexes = []
    i = 0
    for node in G.nodes(data=True):
        if node[1]["s"] == shape:
            indexes.append(i)
        i += 1
    return indexes


def draw_graph(effect_graph):
    G = nx.Graph()
    options = {
        # "node_color": "blue",
        # "node_size": 2000,
        # "width": 1,
    }

    nodes = effect_graph.nodes
    labels_dict = {}
    node_sizes = []
    node_colors = []
    for node in nodes:
        G.add_node(node, s=node_shape(node))
        node_sizes.append(node_size(node))
        node_colors.append(node_color(node))
    for node in nodes:
        labels_dict[node] = node.name
        for connection in node.get_connection_list():
            G.add_edge(node, connection.other, weight=connection.weight)

    node_shapes = set((node[1]["s"] for node in G.nodes(data=True)))
    # nx.
    pos = nx.spring_layout(G, k=0.15, iterations=20)
    for shape in node_shapes:
        node_indexes = indexes_with_shape(G, shape)
        # ...filter and draw the subset of nodes with the same symbol in the positions that are now known through the use of the layout.
        nx.draw_networkx_nodes(
            G,
            pos,
            node_shape=shape,
            node_size=[node_sizes[i] for i in node_indexes],
            node_color=[node_colors[i] for i in node_indexes],
            nodelist=[
                node[0]
                for node in filter(lambda x: x[1]["s"] == shape, G.nodes(data=True))
            ],
        )
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos, labels=labels_dict, verticalalignment="top")

    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.show()
    # plt.savefig("graph.png", dpi=600)


if __name__ == "__main__":
    draw_graph(EFFECT_GRAPH)
