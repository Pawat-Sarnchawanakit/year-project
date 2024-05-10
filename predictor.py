"""The implementation."""
import json
from typing import Self, Iterator
from pathlib import Path
from dataclasses import dataclass
from functools import cache
from tkinter.ttk import Treeview
from rapidfuzz import fuzz, process
from data import Database, Instance


@dataclass
class Vertex:
    """The vertex."""
    name: str
    classname: str
    children: list[Self] | None


class LTable:
    """The levenshtein distance table
    """
    __table: dict[str, str]

    def __init__(self, input_table: dict[str, str]) -> None:
        self.__table = input_table

    @cache
    def find(self, string: str) -> str:
        """Find string. O(n)

        Args:
            string (str): The string to find.

        Returns:
            str: The mapped string.
        """
        name = string.lower()
        result = self.__table.get(name)
        if result is not None:
            return result
        best_name = process.extractOne(name,
                                       self.__table.keys(),
                                       scorer=fuzz.ratio)[0]
        return self.__table[best_name]


def load_single_data(file_path: Path) -> dict:
    """Load a single file as a dictionary.

    Args:
        file_path (Path): The path of the file to load

    Returns:
        dict: The file data.
    """
    data = None
    with open(file_path, 'r', encoding="UTF-8") as file:
        data = json.load(file)
    return data


def to_graph(dictionary: dict) -> Vertex:
    """Convert dictionary to graph."""
    children = dictionary.get("children")
    if children is None:
        return Vertex(name=dictionary["name"],
                      classname=dictionary["class"],
                      children=None)
    new_children: list[Vertex] = []
    stack = [(new_children, children)]
    while stack:
        cur_children, data_children = stack.pop()
        for child in data_children:
            child_children = child.get("children")
            new_child_children: list[
                Vertex] | None = [] if child_children else None
            if child_children:
                new_child_children = []
                stack.append((new_child_children, child_children))
            cur_children.append(
                Vertex(name=child.get("name"),
                       classname=child.get("class"),
                       children=new_child_children))
    return Vertex(name=dictionary["name"],
                  classname=dictionary["class"],
                  children=new_children)


def initialize(db: Database) -> tuple[Vertex, LTable]:
    """Initialize"""
    freq_table: dict[tuple, int] = {}
    count: dict[int, int] = {}
    root_children: list[Vertex] = []
    # load and do the merging and filling the table.
    stack: list[tuple[Iterator, list[Vertex], set]] = []
    for source in db.sources:
        child: list[Instance] | None = source.root.children
        if child is None:
            continue
        stack.append((iter(child), root_children, set()))
    while stack:
        left, right, dup = stack[-1]
        child: Instance = next(left, None)
        if child is None:
            stack.pop()
            continue
        children = child.children
        name, class_name = child.name.lower(), child.class_name
        dup_check = (class_name, name)
        freq_table[dup_check] = freq_table.get(dup_check, 0) + 1
        if children is None:
            if dup_check not in dup:
                dup.add(dup_check)
                new_vertex = Vertex(name=name,
                                    classname=class_name,
                                    children=None)
                right.append(new_vertex)
                count[id(new_vertex)] = 1
            else:
                old_vert = next(
                    (vert for vert in right
                     if vert.name == name and vert.classname == class_name))
                count[id(old_vert)] += 1
            continue
        new_children: list[Vertex] = []
        if dup_check not in dup:
            dup.add(dup_check)
            new_vertex = Vertex(name=name,
                                classname=class_name,
                                children=new_children)
            count[id(new_vertex)] = 1
            right.append(new_vertex)
        else:
            old_vert = next(
                (vert for vert in right
                 if vert.name == name and vert.classname == class_name))
            count[id(old_vert)] += 1
            if old_vert.children is not None:
                new_children = old_vert.children
            else:
                old_vert.children = new_children
        stack.append((iter(children), new_children, set()))
    # Now do the sorting thing.
    root_children.sort(key=lambda vertex: count[id(vertex)], reverse=True)
    sort_stack: list[Iterator[Vertex]] = [iter(root_children)]
    while sort_stack:
        it = sort_stack[-1]
        child: Vertex = next(it, None)
        if child is None:
            sort_stack.pop()
            continue
        if child.children is None:
            continue
        child.children.sort(key=lambda vertex: count[id(vertex)], reverse=True)
        sort_stack.append(iter(child.children))
    root_vert: Vertex = Vertex(name="Game",
                               classname="DataModel",
                               children=root_children)
    freq_arr = [(*k, v) for k, v in freq_table.items()]
    freq_arr.sort(key=lambda val: val[2], reverse=True)
    index_table: dict = {}
    for entry in freq_arr:
        if index_table.get(entry[1]) is None:
            index_table[entry[1]] = entry[0]
    return root_vert, LTable(index_table)


def predict_tree(k_tree, table, tree_view: Treeview):
    """Predicts the tree."""
    test_children = tree_view.get_children(tree_view.get_children()[0])
    predicted_name: dict[str, str | bool] = {}
    add_stack: list[Iterator[str]] = [iter(test_children)]
    while add_stack:
        it = add_stack[-1]
        cur = next(it, None)
        if cur is None:
            add_stack.pop()
            continue
        predicted_name[cur] = True
        children = tree_view.get_children(cur)
        if children is not None:
            add_stack.append(iter(children))
    # Restricted DFS
    stack: list[tuple[list[Vertex], Iterator[str]]] = [(k_tree.children,
                                                        iter(test_children))]
    while stack:
        cur_k, cur_test = stack[-1]
        cur = next(cur_test, None)
        if cur is None:
            stack.pop()
            continue
        is_found = predicted_name.get(cur) is not True
        for k_child in cur_k:
            cur_name = tree_view.item(cur)['text'].lower()
            if k_child.name != cur_name:
                continue
            if not is_found:
                is_found = True
                predicted_name[cur] = k_child.classname
            cur_children = tree_view.get_children(cur)
            if k_child.children is not None and cur_children is not None:
                stack.append((k_child.children, iter(cur_children)))
    # Fallback to levienstein if not found.
    for k, v in predicted_name.items():
        if v is True:
            predicted_name[k] = table.find(tree_view.item(k)['text'].lower())
    # Apply the results
    for k, v in predicted_name.items():
        tree_view.set(k, "class", v)
