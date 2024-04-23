"""This file implements helper methods for graphs."""
from typing import Iterable, Callable, Iterator
import networkx as nwx
from data import DataSource, Instance


def make_edges(graph: nwx.DiGraph, sources: Iterable[DataSource],
               edge_creation_strategy: Callable) -> None:
    """Creates edges."""
    stack: list[tuple[Instance, Iterator[Instance]]] = [
        (source.root, iter(source.root.children or ())) for source in sources
    ]
    dup = set()
    while stack:
        cur = stack[-1]
        child = next(cur[1], None)
        if child is None:
            stack.pop()
            continue
        u, v = edge_creation_strategy(cur[0], child)
        dup_check = (u, v)
        if dup_check not in dup:
            dup.add(dup_check)
            graph.add_edge(u, v)
        if child.children:
            stack.append((child, iter(child.children)))
