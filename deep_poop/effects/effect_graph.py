from __future__ import annotations

from typing import Dict, List
from deep_poop.effects import effect
from deep_poop.effects.effect import Effect


class EffectNode:
    class EffectConnection:
        def __init__(self, other: EffectNode, weight: int):
            self.other = other
            self.weight = weight

    @property
    def name(self):
        return self.effect.name()

    def __init__(self, effect: Effect):
        self.effect = effect
        self.connections = {}

    def add_connection(self, other: EffectNode, weight: int, overwrite=False):
        key = other.name
        if key in self.nodes and not overwrite:
            raise ValueError(f"effect neighbour {key} already exists")
        self.connections[key] = self.EffectConnection(other, weight=weight)

    def get_connection_list(self) -> List[EffectNode.EffectConnection]:
        return self.connections.values()


class EffectGraph:
    def __init__(self, overwrite_connections=False):
        self._nodes = {}
        self._overwrite_connections = overwrite_connections

    def get_node(self, effect: Effect) -> EffectNode:
        return self._nodes[effect.name]

    def add_node(self, effect: Effect) -> EffectNode:
        key = effect.name
        if key in self._nodes:
            raise ValueError(f"node {key} already added to effect graph")
        node = EffectNode(effect)
        self._nodes[key] = node
        return node

    def add_connection(
        self,
        from_node: EffectNode,
        to_node: EffectNode,
        weight: int,
        bidirectional: bool = True,
    ):
        from_node.add_connection(
            to_node, weight=weight, overwrite=self._overwrite_connections
        )
        if bidirectional:
            to_node.add_connection(
                from_node, weight=weight, overwrite=self._overwrite_connections
            )

    def get_neighbour_connections(
        self, current_effect: Effect
    ) -> List[EffectNode.EffectConnection]:
        current_node = self.get_node(current_effect)
        return current_node.get_connection_list()
