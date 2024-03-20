from itertools import chain
from typing import Iterable, Tuple, Set, Callable, List, FrozenSet
import networkx as nwx
from data import DataSource, Instance


def load_graph(sources: Iterable[DataSource],
               edge_creation_strategy: Callable) -> None:
    graph = nwx.DiGraph()
    graph.add_nodes_from(
        set(
            map(lambda val: val.class_name,
                chain(*map(lambda source: source.everything(), sources)))))
    stack: List[Tuple[Instance, Instance | None]] = [(source.root, None)
                                                     for source in sources]
    edge_set: Set[FrozenSet[Tuple[Instance, Instance]]] = set()
    while stack:
        cur = stack.pop()
        u, v = edge_creation_strategy(cur[0], cur[1])
        if cur[1] is not None:
            edge = frozenset((u, v))
            if edge not in edge_set:
                edge_set.add(edge)
                graph.add_edge(u, v)
        if cur[0].children:
            for child in cur[0].children:
                stack.append((child, cur[0]))
    return graph
